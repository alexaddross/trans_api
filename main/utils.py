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

    msg_text = MIMEText(f'Здравствуйте!<br>Высылаем коммерческое предложение.<br><br>С уважением,<br>Transconvey', 'html')
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