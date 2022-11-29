from pydantic import BaseSettings


class Settings(BaseSettings):
    # Core
    app_name: str = 'НАЗВАНИЕ ПРИЛОЖЕНИЯ'
    port: int = 5000
    core_group: int = -1000000000
    db_link: str = 'URL БАЗЫ ДАННЫХ ДЛЯ ПОДКЛЮЧЕНИЯ'

    # SMTP
    core_address = 'АДРЕС С КОТОРОГО БУДЕТ ОТПРАВЛЕНО КП'
    core_address_password = 'ПАРОЛЬ АДРЕСА'

    smtp_host = 'ХОСТ-СЕРВЕР АДРЕСА'

    # Storage
    data_dir = 'ПАПКА С ФАЙЛАМИ'

    # Monday API
    apikey = 'КЛЮЧ ОТ MONDAY API'


settings = Settings()
