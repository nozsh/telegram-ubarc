from pyrogram import Client, filters
from pyrogram.enums import ParseMode
import time
import logging
import multiprocessing
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение переменных окружения
userbots_str = os.getenv('USERBOTS')  # Строка с идентификаторами юзерботов, разделенными запятыми
cooldown_time = int(os.getenv('COOLDOWN_TIME'))  # Время cooldown в секундах, преобразованное в целое число

# Преобразование строки userbots в список
userbots = userbots_str.split(',')  # Разделение строки на отдельные идентификаторы юзерботов

# Настройка логирования
logging.basicConfig(level=logging.INFO)  # Установка уровня логирования на INFO

def run_userbot(userbot_id):
    """
    Функция для запуска отдельного юзербота.
    
    :param userbot_id: Идентификатор юзербота
    """
    directory = f'data/{userbot_id}'  # Директория для данных юзербота
    os.makedirs(directory, exist_ok=True)  # Создание директории, если она не существует

    # Путь к файлу сессии
    session_file = f'{directory}/{userbot_id}_session.session'  # Файл сессии для юзербота

    userbot = Client(session_file)  # Создание клиента юзербота

    # Словарь для хранения времени последнего ответа для каждого пользователя
    last_response_times = {}

    @userbot.on_message(filters.private)
    async def handler(client, message):
        """
        Обработчик сообщений для юзербота.
        
        :param client: Клиент Pyrogram
        :param message: Полученное сообщение
        """
        user_id = message.from_user.id  # Идентификатор отправителя сообщения
        current_time = time.time()  # Текущее время в секундах

        status_file = f'{directory}/{userbot_id}_status.txt'  # Файл статуса юзербота
        message_file = f'{directory}/{userbot_id}_message.txt'  # Файл с текстом сообщения для отправки
        
        with open(status_file, 'r') as file:
            status = file.read().strip()  # Чтение статуса юзербота (1 - активен, иначе - неактивен)
        
        if status == '1':
            # Проверка, что сообщение не отправлено самим юзерботом и не ботом
            if message.from_user.is_self or message.from_user.is_bot:
                return

            # Проверка cooldown для пользователя
            if user_id in last_response_times and current_time - last_response_times[user_id] < cooldown_time:
                logging.info(f"{userbot_id}: Ответ пользователю {user_id} на cooldown.")
                return

            # Чтение текста сообщения из файла
            with open(message_file, 'r', encoding='utf-8') as file:
                message_text = file.read()
            await message.reply(message_text, parse_mode=ParseMode.HTML)  # Отправка сообщения
            logging.info(f"Отправлено сообщение от {userbot_id}: {message_text}")
            last_response_times[user_id] = current_time  # Обновление времени последнего ответа
        else:
            logging.info(f"{userbot_id} выключен, сообщение не отправлено.")
            return

    userbot.run()  # Запуск юзербота

if __name__ == '__main__':
    processes = []
    for userbot_id in userbots:
        p = multiprocessing.Process(target=run_userbot, args=(userbot_id,))  # Создание процесса для каждого юзербота
        p.start()  # Запуск процесса
        processes.append(p)

    for p in processes:
        p.join()  # Ожидание завершения всех процессов