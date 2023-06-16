import telebot
import threading

bot = telebot.TeleBot("********")

timers = {}
allowed_chat_id = "****"


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, "Привіт! Це телеграм бот методу Pomodoro. Щоб почати роботу, введіть /work.")


@bot.message_handler(commands=['work'])
def work_command(message):
    chat_id = message.chat.id
    if str(chat_id) == allowed_chat_id:
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = telebot.types.KeyboardButton('5 хвилин')
        itembtn2 = telebot.types.KeyboardButton('10 хвилин')
        itembtn3 = telebot.types.KeyboardButton('20 хвилин')
        itembtn4 = telebot.types.KeyboardButton('30 хвилин')
        itembtn5 = telebot.types.KeyboardButton('Вказати час')
        itembtn6 = telebot.types.KeyboardButton('Зупинити таймер')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
        bot.send_message(chat_id, "Виберіть таймер або введіть кількість хвилин:", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Ви не маєте доступу до цього бота.")


@bot.message_handler(func=lambda message: True)
def timer_command(message):
    chat_id = message.chat.id
    if str(chat_id) != allowed_chat_id:
        bot.send_message(chat_id, "Ви не маєте доступу до цього бота.")
        return

    if message.text == 'Вказати час':
        bot.send_message(chat_id, "Введіть кількість хвилин:")
        bot.register_next_step_handler(message, custom_timer_command)
        return
    elif message.text == 'Зупинити таймер':
        if chat_id not in timers:
            bot.send_message(chat_id, "Таймер не запущено.")
        else:
            timer_thread = timers[chat_id]['timer_thread']
            timer_thread.cancel()
            timers.pop(chat_id)
            bot.send_message(chat_id, "Таймер зупинено.")
        return
    else:
        try:
            timer = int(message.text.split()[0])
            if timer < 1:
                bot.send_message(chat_id, "Таймер не може бути меншим за 1 хвилину.")
                return
            bot.send_message(chat_id, "Таймер запущено на %s хвилин." % timer)
            timer_thread = threading.Timer(timer * 60, work_finished, args=[chat_id])
            timers[chat_id] = {'timer_thread': timer_thread}
            timer_thread.start()
            return
        except ValueError:
            pass

    bot.send_message(chat_id,
                     "Невірна команда. Виберіть таймер за допомогою кнопок на екрані або введіть кількість хвилин.")
    return


def work_finished(chat_id):
    bot.send_message(chat_id, "Час вийшов! Робота завершена. Щоб розпочати нову, введіть /work.")
    timers.pop(chat_id)


def custom_timer_command(message):
    chat_id = message.chat.id
    try:
        timer = int(message.text)
    except ValueError:
        bot.send_message(chat_id, "Невірне значення. Введіть число.")
        return

    if timer < 1:
        bot.send_message(chat_id, "Таймер не може бути меншим за 1 хвилину.")
        return

    bot.send_message(chat_id, "Таймер запущено на %s хвилин." % timer)
    timer_thread = threading.Timer(timer * 60, work_finished, args=[chat_id])
    timers[chat_id] = {'timer_thread': timer_thread}
    timer_thread.start()


bot.polling()
