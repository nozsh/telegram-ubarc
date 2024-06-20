from pyrogram import Client
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение переменных окружения
userbotName = os.getenv('NEW_USER_BOT_NAME')
api_id = os.getenv('NEW_USER_BOT_API_ID')
api_hash = os.getenv('NEW_USER_BOT_API_HASH')

# Создание директории для данного юзербота, если она не существует
directory = f'data/{userbotName}'
os.makedirs(directory, exist_ok=True)

# Имя файла сессии
session_file = f'{directory}/{userbotName}_session.session'

# Создание файлов message.txt и status.txt с текстом по умолчанию
message_file = f'{directory}/{userbotName}_message.txt'
status_file = f'{directory}/{userbotName}_status.txt'

with open(message_file, 'w', encoding='utf-8') as file:
    file.write("Пример сообщения")

with open(status_file, 'w', encoding='utf-8') as file:
    file.write("0")

# Создание клиента и авторизация
client = Client(session_file, api_id, api_hash)

# Запуск клиента для авторизации
with client:
    print("Авторизация прошла успешно!")