from fastapi import Request
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from main.utils import send_mail
from bot_module.core import bot

from config import settings


core_router = APIRouter()


@core_router.post('/cp_visited')
async def proposal_visited(request: Request):
    '''
    Отправка уведомления о посещении клиентом КП
    '''
    # --- Получение данных
    data = await request.json()

    await bot.send_message(settings.core_group, f'Клиент {data["email"]} посетил страницу с КП')


@core_router.post('/new_client')
async def new_client(request: Request):
    '''
    Отправка уведомлений о новом клиенте по всем каналам связи и отправка письма с КП

    request: Объект типа Request, обыкновенный HTTP запрос приходящий от клиента
    ''' 

    # --- Получение данных
    data = await request.json()

    # --- Валидация ---
    if request.headers.get('X-Api-Key', '') != '62302d3f50824775e7a06df5e400064d74864fe64aef6ca702fec5f3189a594b':
        return JSONResponse({'error': 'invalid key'}, 403)
    
    if not data.get('test', None) is None:
        return JSONResponse({'message': 'ok'})

    # --- Тело ---
    # Разделение по двум формам (0 -- основная форма pop-up, 1 -- форма в самом низу страницы)
    if data['form_ident'] == '0':
        await bot.send_message(settings.core_group,
                        f'<b>Новая заявка!</b>\n\nФИО: {data["ФИО"]}\nКонтактный номер: {data["Телефон"]}\nПочта: {data["Почта"]}\nПроизводительность: {data["Производительность"]}\nТип захвата: {data["Продукция"]}', parse_mode='HTML')
        pass

    elif data['form_ident'] == '1':
        await bot.send_message(settings.core_group,
                        f'<b>Новая заявка!</b>\n\nФИО: {data["ФИО"]}\nКонтактный номер: {data["Телефон"]}\nПочта: {data["Почта"]}\nКомментарий: {data.get("Комментарий", "---")}', parse_mode='HTML')

        data.update({'Продукция': 'Другое'})

    # --- Ответ от сервера
    # Возвращается результата работы функции по отправке письма
    return await send_mail(data)