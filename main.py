import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot('YOUR_SECRET_TOKEN')

# Сюда попадаем при первом открытии бота пользователем либо если юзер явно отправит команду /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я – бот, который много чего умеет')

# Сюда попадаем при отправке команды /help
@bot.message_handler(commands=['help'])
def on_help_command(message):
    bot.send_message(message.chat.id, 'Вызвана команда /help')

# Сюда попадаем при отправке команды /buttons (и показываем кнопки)
@bot.message_handler(commands=['buttons'])
def on_help_command(message):
    bot.send_message(message.chat.id, 'Вызвана команда /buttons, держи кнопочки...')
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    button = InlineKeyboardButton(
        text='Первая кнопка',
        callback_data='button_1'
    )
    markup.add(button)
    button = InlineKeyboardButton(
        text='Вторая кнопка',
        callback_data='button_2'
    )
    markup.add(button)
    bot.send_message(message.chat.id, 'Твои кнопки', reply_markup=markup)

# Сюда попадаем по нажатию на какую-то кнопку, которую мы ранее и показали
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'button_1':
        bot.send_message(call.message.chat.id, 'Нажата первая кнопка')
    elif call.data == 'button_2':
        bot.send_message(call.message.chat.id, 'Нажата вторая кнопка')
    else:
        pass # неизвестный callback

# Сюда попадаем, когда пользователь написал какое-то сообщение
@bot.message_handler(content_types=['text'])
def on_text_messages(message):
    bot.send_message(message.chat.id, f'Получено сообщение: {message.text}')

if __name__ == '__main__':
    bot.infinity_polling()