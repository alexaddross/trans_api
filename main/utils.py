import aiosmtplib
import aiohttp
import asyncio

from config import settings

from os.path import basename

from email.utils import make_msgid
from email.utils import formatdate
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from fastapi.responses import JSONResponse

CP_TEXT = '''Здравствуйте!<br>
Спасибо за интерес к роботам STEP.
<br><br>
В приложении к письму вы найдете коммерческое предложение на линию укладки в простейшей из возможных конфигураций, схему оптимального размещения робота и линии подачи продукции. При таком взаимном размещении робота, пикап конвейера и зоны укладки, производительность линии будет максимальной. Скажем, для мешков весом 30кг возможно ожидать производительности в районе 600-700 мешков в час.
Роботы STEP производятся в городе Шанхай на заводе Шанхай СТЕП Электрик Корпорейшн. Это крупная группа компаний, занимающая одно из лидирующих мест на рынке промышленных роботов в Китае. Производственные мощности завода позволяют выпускать до 10000 роботов различных типов в год. 
Несколько слов о нас: первые роботы в России мы установили в 2010 году, они до сих пор на ходу. Всю периферию, захваты и конвейеры для подачи продукции для своих проектов мы создаём на собственном производстве, запчасти всегда в наличии. Знаем, как поддерживать предприятия на ходу, несмотря на большие расстояния. Работаем от Калининграда до Владивостока, также есть реализованные проекты в Казахстане и Молдове.
<br><br>
В приложении к письму вы также найдете коммерческое предложение на робот и план размещения оборудования. Цена в предложении за систему под ключ, когда продукция укладывается на поддоны, предварительно размещенные слева и справа от робота.
<br><br>
В дополнение к коммерческому предложению вы найдете пример для расчета финансирования поставки линии по схеме лизинга.
<br><br>
Если у вас будут вопросы, мы с удовольствием ответим и если понадобится приедем к вам и подробно расскажем, что и как мы делаем.
https://t.me/fujirobotics -- это группа в Телеграм, где наши инженеры публикуют видео и фото монтажей и обслуживания линий, которые мы установили. Возможно найдете что-то полезное для себя.
<br><br>
Видео
https://youtu.be/HiNSnYOj7xY
https://youtu.be/22CnijfQbok
https://youtu.be/-D9-EDCiOvc
https://youtu.be/uMQX7SvG_Xg
<br><br>
С уважением,
Генеральный директор
ООО "Трансконвей"
Соболевский Георгий
+7 (903) 766 45-56'''


async def send_mail(data):
    '''
    Функция для отправки сообщения с КП новому клиенту и отправка копии на почту сгенерированную Monday

    data: Данные в формате JSON, полученные из тела запроса
    '''

    # --- Запрос и поиск информации о новом клиенте в Monday
    query = 'query { boards(ids:35027256) { items (newest_first: true, limit: 5) {  id, column_values { text }, email }}}'
    headers = {'Authorization': settings.apikey}

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            monday_added = False
            errors = 0
            while not monday_added:
                async with session.post('https://api.monday.com/v2/', json={'query': query}) as items: 
                    try:
                        newest_clients = await items.json()
                        
                        if errors >= 5:
                            with open('last_error.txt', 'w') as errorf:
                                errorf.write(str(newest_clients))

                            raise ConnectionError
                        
                        newest_clients = newest_clients['data']['boards'][0]['items']
                    except KeyError:
                        errors += 1
                        await asyncio.sleep(2)
                    
                values = [[client['column_values'][i]['text'] for i in range(len(client['column_values']))] + [client['email']] for client in newest_clients]

                for client in values:
                    if data['Почта'] in client:
                        current_client = client
                        monday_added = True
                        break

                if not monday_added:
                    errors += 1
                    await asyncio.sleep(2)
    except ConnectionError:
        current_client = None

    # --- Формирование письма клиенту ---
    msg = MIMEMultipart()
    msg['From'] = settings.core_address
    msg['To'] = data["Почта"]
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = 'Коммерческое предложение от Transconvey LLC'
    msg['message-id'] = make_msgid(domain='transconvey.ru')

    msg_text = MIMEText(CP_TEXT, 'html')
    msg.attach(msg_text)

    # --- Разделение содержимого письмо по типу продукции
    # Мешки -- файл с мешками, Коробки -- файл с коробками, Другое -- оба файла сразу
    if data['Продукция'] == 'Мешки':
        required_data = ['schema.png', 'STEP Robot for bags.pdf','Reference list.pdf']
    elif data['Продукция'] == 'Коробки':
        required_data = ['schema.png', 'STEP Robot for boxes.pdf','Reference list.pdf']
    else:
        required_data = ['schema.png', 'STEP Robot for boxes.pdf','Reference list.pdf']
    
    # Загрузка файлов с локальной машины в письмо
    for filepath in required_data:
        with open(settings.data_dir + '/' + filepath, 'rb') as file:
            part = MIMEApplication(file.read(), Name=basename(filepath))

        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(filepath)
        msg.attach(part)

    # Формирование списка получателей (если смогли дождаться ответа от Monday, отправляем на сгенерированный адрес и на почту клиенту)
    recepients = data['Почта'] if current_client is None else [data['Почта'], current_client[-1]]
    await aiosmtplib.send(msg.as_string(), settings.core_address, recepients, hostname=settings.smtp_host, username=settings.core_address, password=settings.core_address_password)
    
    # Если клиент не был найден (= None), отправляет только на почту клиенту, отправляем предупреждение что была проблема
    if current_client is None:
        return JSONResponse({'warning': 'message sent but monday is not accessed (API Exceeded)'}, 206)
    else:
        return JSONResponse({'ok': 'all services worked'}, 201)