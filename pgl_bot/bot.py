import telebot
from telebot import types
from db import get_connection

bot = telebot.TeleBot('7974723442:AAHpqGUbqQMVOTMTupnVBy3ovICN1SiUO7c')
user_states = {}

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = str(message.chat.id)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM tg WHERE login = %s", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO tg (login, date, isbuy) VALUES (%s, CURRENT_DATE, FALSE)", (user_id,))
        conn.commit()

    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Создать аккаунт", "Купить подписку")
    markup.row("Удалить аккаунт")
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "Создать аккаунт")
def ask_password(message):
    bot.send_message(message.chat.id, "Введите желаемый пароль:")
    user_states[message.chat.id] = 'awaiting_password'

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == 'awaiting_password')
def create_account(message):
    password = message.text
    user_id = str(message.chat.id)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM website WHERE login = %s", (user_id,))
    if cur.fetchone():
        bot.send_message(message.chat.id, "Аккаунт уже существует.")
    else:
        cur.execute("INSERT INTO website (login, password, isbuy) VALUES (%s, %s, FALSE)", (user_id, password))
        conn.commit()
        bot.send_message(message.chat.id, "Аккаунт создан. Теперь вы можете купить подписку.")

    cur.close()
    conn.close()
    user_states.pop(message.chat.id, None)

@bot.message_handler(func=lambda msg: msg.text == "Купить подписку")
def handle_buy(message):
    user_id = str(message.chat.id)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE tg SET isbuy = TRUE WHERE login = %s", (user_id,))

    cur.execute("SELECT * FROM website WHERE login = %s", (user_id,))
    if cur.fetchone():
        cur.execute("UPDATE website SET isbuy = TRUE WHERE login = %s", (user_id,))
    else:
        cur.execute("INSERT INTO website (login, password, isbuy) VALUES (%s, %s, TRUE)", (user_id, "default123"))

    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, "Подписка активирована.")

@bot.message_handler(func=lambda msg: msg.text == "Удалить аккаунт")
def confirm_delete(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Да, удалить", "Нет")
    bot.send_message(message.chat.id, "Вы уверены, что хотите удалить аккаунт?", reply_markup=markup)
    user_states[message.chat.id] = 'awaiting_delete_confirmation'

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == 'awaiting_delete_confirmation')
def delete_account_handler(message):
    user_id = str(message.chat.id)
    if message.text == "Да, удалить":
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM tg WHERE login = %s", (user_id,))
        cur.execute("DELETE FROM website WHERE login = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()

        bot.send_message(message.chat.id, "Ваш аккаунт и подписка удалены.")
    else:
        bot.send_message(message.chat.id, "Удаление отменено.")

    user_states.pop(message.chat.id, None)
    handle_start(message) 
        
bot.infinity_polling()
