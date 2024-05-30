import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

bot = telebot.TeleBot('7290494006:AAF-_u8HAzyu75gAnsSkap_XY-0pFyCIaCg')

admin_id = 967468929  # Замените на ID администратора
users = {}  # Храним данные о пользователях, это может быть база данных на практике
tasks = {}  # Храним задания и их статусы

# Команда для старта бота
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id == admin_id:
        bot.send_message(message.chat.id, f'Привет, админ! Используй /addtasks для добавления заданий.')
    else:
        users[message.chat.id] = {'status': 'active', 'last_submission': None}
        bot.send_message(message.chat.id, 'Привет! Вперед к написанию шуток!')

# Команда для администратора для добавления заданий
@bot.message_handler(commands=['addtasks'])
def add_tasks(message):
    if message.chat.id == admin_id:
        bot.send_message(message.chat.id, 'Отправь задание в формате "дата:задание" (например, 2022-12-01:Придумай шутку про котов). Отправь /endtasks для завершения добавления заданий.')
        bot.register_next_step_handler(message, get_task)
    else:
        bot.send_message(message.chat.id, 'Эта команда доступна только администратору.')
        bot.send_message(message.chat.id, message.chat.id)

def get_task(message):
    if message.text == "/endtasks":
        bot.send_message(admin_id, 'Задания успешно добавлены.')
    else:
        try:
            date_str, task = message.text.split(':')
            task_date = datetime.strptime(date_str, '%Y-%m-%d')
            tasks[task_date.date()] = {'task': task, 'completed': []}
            bot.send_message(admin_id, f'Задание на {date_str} было успешно добавлено.')
        except ValueError:
            bot.send_message(admin_id, 'Некорректный формат. Попробуйте еще раз в формате "дата:задание".')
        
        bot.register_next_step_handler(message, get_task)

# Проверка регулярности выполнения задач
def check_tasks():
    today = datetime.today().date()
    if today in tasks:
        task = tasks[today]['task']
        
        inactive_users = []
        
        for user_id, data in users.items():
            if data['status'] == 'active' and data['last_submission'] != today:
                users[user_id]['status'] = 'inactive'
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            bot.send_message(user_id, 'Вы выбыли из игры, так как не прислали шутку.')

        for user_id in users:
            if users[user_id]['status'] == 'active':
                bot.send_message(user_id, f'Сегодняшнее задание: {task}')

# Периодически вызываем функцию проверки задач
@bot.message_handler(commands=['checktasks'])
def start_check_tasks(message):
    if message.chat.id == admin_id:
        bot.send_message(admin_id, 'Запуск проверки задач.')
        check_tasks()

# Получение шуток от пользователей
@bot.message_handler(content_types=['text'])
def on_text_messages(message):
    if message.chat.id in users:
        today = datetime.today().date()
        if today in tasks:
            if users[message.chat.id]['status'] == 'active':
                tasks[today]['completed'].append({'user': message.chat.id, 'joke': message.text})
                users[message.chat.id]['last_submission'] = today
                bot.send_message(message.chat.id, 'Шутка принята!')
                bot.send_message(admin_id, f'Получена шутка от {message.chat.username}: {message.text}')
            else:
                bot.send_message(message.chat.id, 'Вы не можете отправить шутку, так как выбиты из игры.')
        else:
            bot.send_message(message.chat.id, 'Сегодня нет задания.')
    else:
        bot.send_message(message.chat.id, 'Нажмите /start для начала.')

# Запрос на пропуск задания
@bot.message_handler(commands=['skip'])
def request_skip(message):
    if message.chat.id in users and users[message.chat.id]['status'] == 'active':
        markup = InlineKeyboardMarkup()
        button_yes = InlineKeyboardButton(text='Да', callback_data=f'skip:{message.chat.id}:accept')
        button_no = InlineKeyboardButton(text='Нет', callback_data=f'skip:{message.chat.id}:decline')
        markup.add(button_yes, button_no)
        bot.send_message(admin_id, f'Пользователь {message.chat.username} просит разрешение пропустить задание. Разрешить?', reply_markup=markup)

# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith('skip'))
def callback_query(call):
    action = call.data.split(':')[2]
    user_id = call.data.split(':')[1]
    if action == 'accept':
        users[int(user_id)]['status'] = 'active'
        bot.send_message(int(user_id), 'Ваша просьба пропустить задание принята.')
    elif action == 'decline':
        bot.send_message(int(user_id), 'Ваша просьба пропустить задание отклонена.')

if __name__ == '__main__':
    from threading import Timer
    def periodic_task():
        check_tasks()
        Timer(86400, periodic_task).start()  # 86400 секунд = 24 часа

    periodic_task()
    bot.infinity_polling()
