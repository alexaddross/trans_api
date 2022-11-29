from pydantic import BaseSettings


class Settings(BaseSettings):
    # Core
    app_name: str = 'Transconvey ServiceHub'
    port: int = 5000
    core_group: int = -680390307

    # SMTP
    core_address = 'noreply@transconvey.ru'
    core_address_password = 'ulluauz5a'

    smtp_host = 'smtp.masterhost.ru'

    # Storage
    data_dir = 'main/data'

    # Monday API
    apikey = 'eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjE5NzQ3Mjc4NywidWlkIjo2OTkwODksImlhZCI6IjIwMjItMTEtMjFUMTA6NDg6MzEuMDAwWiIsInBlciI6Im1lOndyaXRlIiwiYWN0aWQiOjI3NzgyMiwicmduIjoidXNlMSJ9.TD-p53yQZsYeytLH6v9jMgbJ_8vCFr-pPNt4OUwrO_k'


settings = Settings()
