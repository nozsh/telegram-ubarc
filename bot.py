from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import logging
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение переменных окружения
TOKEN = os.getenv('BOT_TOKEN')  # Токен бота для взаимодействия с Telegram API
ADMIN_ID = int(os.getenv('ADMIN_ID'))  # Идентификатор администратора
userbots_str = os.getenv('USERBOTS')  # Строка с идентификаторами юзерботов, разделенными запятыми

# Преобразование строки userbots в список
userbots = userbots_str.split(',')  # Разделение строки на отдельные идентификаторы юзерботов

# Настройка логирования
logging.basicConfig(level=logging.INFO)  # Установка уровня логирования на INFO
# logging.basicConfig(level=logging.WARNING)  # Установка уровня логирования на WARNING
# logging.basicConfig(level=logging.ERROR)  # Установка уровня логирования на ERROR

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)  # Создание экземпляра бота
dp = Dispatcher(bot)  # Создание диспетчера для обработки событий

# Проверка на администратора
def is_admin(user_id):
    """
    Проверяет, является ли пользователь администратором.
    
    :param user_id: Идентификатор пользователя
    :return: True, если пользователь является администратором, иначе False
    """
    return user_id == ADMIN_ID

# Получение текущего статуса юзербота
def get_userbot_status(userbot_id):
    """
    Получает текущий статус юзербота (включен/выключен).
    
    :param userbot_id: Идентификатор юзербота
    :return: Статус юзербота ('1' - включен, '0' - выключен)
    """
    directory = f'data/{userbot_id}'
    os.makedirs(directory, exist_ok=True)  # Создание директории, если она не существует
    try:
        with open(f'{directory}/{userbot_id}_status.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return '0'

# Получение текущего сообщения юзербота
def get_userbot_message(userbot_id):
    """
    Получает текущее сообщение, которое юзербот отправляет в ответ.
    
    :param userbot_id: Идентификатор юзербота
    :return: Текст сообщения
    """
    directory = f'data/{userbot_id}'
    os.makedirs(directory, exist_ok=True)  # Создание директории, если она не существует
    try:
        with open(f'{directory}/{userbot_id}_message.txt', 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        return ''

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    Обрабатывает команду /start.
    
    :param message: Сообщение от пользователя
    """
    if not is_admin(message.from_user.id):  # Проверка, является ли пользователь администратором
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🔌 ВКЛ/ВЫКЛ", callback_data='manage_userbots'),
        types.InlineKeyboardButton("💬 Сообщения", callback_data='settings')
    )
    await message.answer('👾 *Telegram UserBot Auto Reply Control*', reply_markup=keyboard, parse_mode='Markdown')
    
    # Удаляем сообщение, которое отправил пользователь
    await message.delete()

# Обработчик инлайн-кнопок
@dp.callback_query_handler(lambda c: c.data.startswith('manage_userbots'))
async def manage_userbots(callback_query: types.CallbackQuery):
    """
    Обрабатывает нажатие на инлайн-кнопку для управления юзерботами.
    
    :param callback_query: Объект callback_query, содержащий данные о нажатой кнопке
    """
    if not is_admin(callback_query.from_user.id):  # Проверка, является ли пользователь администратором
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if not any(userbots):  # Проверка, если список userbots пустой
        keyboard.row(types.InlineKeyboardButton("🔽", callback_data='back_to_main'))
        await callback_query.message.edit_text("*Нет ни одного юзербота...*", reply_markup=keyboard, parse_mode='Markdown')
    else:
        buttons = []
        for ub in userbots:
            status = get_userbot_status(ub)
            if status == '1':
                buttons.append(types.InlineKeyboardButton(f"✅ {ub}", callback_data=f'toggle_{ub}'))  # Включен
            else:
                buttons.append(types.InlineKeyboardButton(f"🔌 {ub}", callback_data=f'toggle_{ub}'))  # Выключен
        
        # Добавляем кнопки в клавиатуру с учетом row_width
        for i in range(0, len(buttons), keyboard.row_width):
            keyboard.row(*buttons[i:i + keyboard.row_width])
        
        keyboard.row(types.InlineKeyboardButton("🔽", callback_data='back_to_main'))
        await callback_query.message.edit_text("*Кого включаем/выключаем?*", reply_markup=keyboard, parse_mode='Markdown')

@dp.callback_query_handler(lambda c: c.data.startswith('toggle_'))
async def toggle_userbot(callback_query: types.CallbackQuery):
    """
    Обрабатывает нажатие на инлайн-кнопку для включения/выключения юзербота.
    
    :param callback_query: Объект callback_query, содержащий данные о нажатой кнопке
    """
    if not is_admin(callback_query.from_user.id):  # Проверка, является ли пользователь администратором
        return

    userbot_id = callback_query.data.split('_')[1]  # Извлечение идентификатора юзербота из данных кнопки
    current_status = get_userbot_status(userbot_id)  # Получение текущего статуса юзербота
    new_status = '1' if current_status == '0' else '0'  # Переключение статуса
    directory = f'data/{userbot_id}'
    os.makedirs(directory, exist_ok=True)  # Создание директории, если она не существует
    with open(f'{directory}/{userbot_id}_status.txt', 'w') as file:
        file.write(new_status)  # Запись нового статуса в файл

    await manage_userbots(callback_query)  # Обновление сообщения с кнопками управления юзерботами
    await callback_query.answer(f"{userbot_id} {'включен' if new_status == '1' else 'выключен'}.")  # Уведомление о смене статуса

@dp.callback_query_handler(lambda c: c.data.startswith('settings'))
async def settings(callback_query: types.CallbackQuery):
    """
    Обрабатывает нажатие на инлайн-кнопку для настройки сообщений юзерботов.
    
    :param callback_query: Объект callback_query, содержащий данные о нажатой кнопке
    """
    if not is_admin(callback_query.from_user.id):  # Проверка, является ли пользователь администратором
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    if not any(userbots):  # Проверка, если список userbots пустой
        keyboard.row(types.InlineKeyboardButton("🔽", callback_data='back_to_main'))
        await callback_query.message.edit_text("*Нет ни одного юзербота...*", reply_markup=keyboard, parse_mode='Markdown')
    else:
        buttons = []
        for ub in userbots:
            message = get_userbot_message(ub)  # Получение текущего сообщения юзербота
            buttons.append(types.InlineKeyboardButton(f"💬 {ub}", callback_data=f'edit_message_{ub}'))
        
        # Добавляем кнопки в клавиатуру с учетом row_width
        for i in range(0, len(buttons), keyboard.row_width):
            keyboard.row(*buttons[i:i + keyboard.row_width])
        
        keyboard.row(types.InlineKeyboardButton("🔽", callback_data='back_to_main'))
        await callback_query.message.edit_text("*Чье сообщение редактируем?*", reply_markup=keyboard, parse_mode='Markdown')

@dp.callback_query_handler(lambda c: c.data.startswith('edit_message_'))
async def edit_message(callback_query: types.CallbackQuery):
    """
    Обрабатывает нажатие на инлайн-кнопку для редактирования сообщения юзербота.
    
    :param callback_query: Объект callback_query, содержащий данные о нажатой кнопке
    """
    if not is_admin(callback_query.from_user.id):  # Проверка, является ли пользователь администратором
        return

    userbot_id = callback_query.data.split('_')[2]  # Извлечение идентификатора юзербота из данных кнопки
    
    current_message = get_userbot_message(userbot_id)  # Получение текущего сообщения юзербота
    await callback_query.message.edit_text(f"---\n{current_message}\n---\n\nНовое сообщение для {userbot_id}:", parse_mode=None)
    
    # Регистрация временного обработчика
    @dp.message_handler(lambda message: message.from_user.id == ADMIN_ID)
    async def save_message(message: types.Message):
        directory = f'data/{userbot_id}'
        os.makedirs(directory, exist_ok=True)  # Создание директории, если она не существует
        formatted_message = reconstruct_message_with_formatting(message)  # Форматирование сообщения
        with open(f'{directory}/{userbot_id}_message.txt', 'w', encoding='utf-8') as file:
            file.write(formatted_message)  # Запись нового сообщения в файл

        # Обновляем current_message новым сообщением
        current_message = get_userbot_message(userbot_id)

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton("🔽", callback_data='back_to_main'))
        await callback_query.message.edit_text(f"---\n{current_message}\n---\n\nСообщение для {userbot_id} обновлено.", parse_mode=None, reply_markup=keyboard)

        # Удаляем сообщение, которое отправил пользователь
        await message.delete()

        # Отмена регистрации временного обработчика
        dp.message_handlers.unregister(save_message)

def reconstruct_message_with_formatting(message: types.Message):
    """
    Восстанавливает форматирование сообщения на основе его сущностей.
    
    :param message: Сообщение от пользователя
    :return: Отформатированный текст сообщения
    """
    text = message.text
    entities = message.entities or []
    formatted_message = ""
    last_offset = 0

    for entity in entities:
        formatted_message += text[last_offset:entity.offset]
        entity_text = text[entity.offset:entity.offset + entity.length]
        if entity.type == "bold":
            formatted_message += f"<b>{entity_text}</b>"
        elif entity.type == "italic":
            formatted_message += f"<i>{entity_text}</i>"
        elif entity.type == "underline":
            formatted_message += f"<u>{entity_text}</u>"
        elif entity.type == "strikethrough":
            formatted_message += f"<s>{entity_text}</s>"
        elif entity.type == "code":
            formatted_message += f"<code>{entity_text}</code>"
        elif entity.type == "pre":
            formatted_message += f"<pre><code>{entity_text}</code></pre>"
        elif entity.type == "text_link":
            formatted_message += f"<a href='{entity.url}'>{entity_text}</a>" 
        elif entity.type == "blockquote":
            formatted_message += f"<blockquote>{entity_text}</blockquote>"
        elif entity.type == "expandable_blockquote":
            formatted_message += f"<blockquote expandable>{entity_text}</blockquote>"
        last_offset = entity.offset + entity.length

    formatted_message += text[last_offset:]
    return formatted_message

@dp.callback_query_handler(lambda c: c.data.startswith('back_to_main'))
async def back_to_main(callback_query: types.CallbackQuery):
    """
    Обрабатывает нажатие на инлайн-кнопку для возврата в главное меню.
    
    :param callback_query: Объект callback_query, содержащий данные о нажатой кнопке
    """
    if not is_admin(callback_query.from_user.id):  # Проверка, является ли пользователь администратором
        return

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🔌 ВКЛ/ВЫКЛ", callback_data='manage_userbots'),
        types.InlineKeyboardButton("💬 Сообщения", callback_data='settings')
    )
    await callback_query.message.edit_text('👾 *Telegram UserBot Auto Reply Control*', reply_markup=keyboard, parse_mode='Markdown')

# Регистрация команд в меню бота
async def set_bot_commands(dp: Dispatcher):
    """
    Устанавливает команды бота, которые будут отображаться в меню.
    
    :param dp: Диспетчер бота
    """
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Меню"),
        types.BotCommand("start2", "Меню2"),
    ])

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=set_bot_commands)