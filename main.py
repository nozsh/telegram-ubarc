import multiprocessing
import bot
import userbot

def run_bot():
    """
    Функция для запуска бота.
    Запускает опрос обновлений с помощью executor.start_polling.
    """
    bot.executor.start_polling(bot.dp, skip_updates=True)

def run_userbot():
    """
    Функция для запуска юзерботов.
    Создает и запускает процессы для каждого юзербота из списка userbot.userbots.
    """
    processes = []
    for userbot_id in userbot.userbots:
        p = multiprocessing.Process(target=userbot.run_userbot, args=(userbot_id,))
        p.start()
        processes.append(p)

    # Ожидаем завершения всех процессов юзерботов
    for p in processes:
        p.join()

if __name__ == '__main__':
    # Создаем два процесса для запуска bot.py и userbot.py
    bot_process = multiprocessing.Process(target=run_bot)
    userbot_process = multiprocessing.Process(target=run_userbot)

    # Запускаем процессы
    bot_process.start()
    userbot_process.start()

    # Ждем завершения процессов
    bot_process.join()
    userbot_process.join()