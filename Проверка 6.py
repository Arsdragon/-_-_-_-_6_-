import chardet
import telebot
import logging
import os
chs = []
q = []
r = []
a = []
message_count = 0
gr= 0
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = telebot.TeleBot('8115861077:AAGWlE6hSLf5XgdxdWksF4x6E1RRFAqMv4k')

def read_file_with_encoding(filename):
    try:
        with open(filename, 'rb') as textee:
            rawdata = textee.read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
            with open(filename, 'r', encoding=encoding) as textee:
                return [x.strip() for x in textee.read().split('&') if x.strip()]
    except FileNotFoundError:
        logging.error(f"Файл {filename} не найден.")
        return []
    except Exception as e:
        logging.error(f"Ошибка при чтении файла {filename}: {e}")
        return []

v = read_file_with_encoding('Classes.txt')
vv = read_file_with_encoding('description.txt')
vvv = read_file_with_encoding('data.txt')
vvvv = read_file_with_encoding('office.txt')
vvvvv = read_file_with_encoding('grade.txt')
vvvvvv = read_file_with_encoding('space.txt')
vvvvvvv = read_file_with_encoding('teacher.txt')


registered_users = {}

if os.path.exists("registered_users.txt"):
    try:
        with open("registered_users.txt", "r", encoding="utf-8") as f:
            registered_users = eval(f.read()) 
    except Exception as e:
        logging.error(f"Ошибка загрузки данных о зарегистрированных пользователях: {e}")


@bot.message_handler(commands=['start'])
def start(message):
    global in_circle_selection, message_handled, message_count
    in_circle_selection = True
    if v:
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i, circle_name in enumerate(v):
            callback_data = f"button_{i}"
            keyboard.add(telebot.types.InlineKeyboardButton(circle_name, callback_data=callback_data))
        bot.send_message(message.chat.id, "Выберите кружок о котором хотите узнать подробнее или записаться:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Список кружков пуст.")
        in_circle_selection = False


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data.startswith("button_"):
            circle_index = int(call.data.split('_')[1])
            if 0 <= circle_index < len(v):
                bot.answer_callback_query(callback_query_id=call.id, text="Кружок выбран!")

                new_keyboard = telebot.types.InlineKeyboardMarkup()
                new_keyboard.add(telebot.types.InlineKeyboardButton("Записаться", callback_data=f"register_{circle_index}"))
                new_keyboard.add(telebot.types.InlineKeyboardButton("Вернуться", callback_data="back"))

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f"Вы выбрали кружок: {v[circle_index]}\n проводится {vvv[circle_index]}\n кабинет {vvvv[circle_index]}\n для {vvvvv[circle_index]} класса  \n преподователь {vvvvvvv[circle_index]}\n мест осталось {vvvvvv[circle_index]}\n Краткая информация: {vv[circle_index]} \n учавствуют {read_file_with_encoding(f'{v[circle_index]}.txt')}",
                                      reply_markup=new_keyboard)
                in_circle_selection = False
                message_handled = False
            else:
                bot.answer_callback_query(callback_query_id=call.id, text="Ошибка: Неверный номер кружка.")
                logging.error(f"Неверный индекс кружка: {circle_index}")

        elif call.data.startswith("register_"):
            circle_index = int(call.data.split('_')[1])
            username = call.from_user.username or call.from_user.first_name 
            filename = f'{v[circle_index]}.txt'
            if username not in registered_users:
                registered_users[username] = []
            if v[circle_index] not in registered_users[username]:
                with open(filename, 'a', encoding='utf-8') as text:
                    text.write(f"{username}&")  
                registered_users[username].append(v[circle_index])
                bot.answer_callback_query(callback_query_id=call.id, text=f"Вы записались на кружок {v[circle_index]}!")
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=f"Вы записались на кружок {v[circle_index]}!")
                start(call.message)
            else:
                bot.answer_callback_query(callback_query_id=call.id, text="Вы уже записаны на этот кружок!")

        elif call.data == "back":
            bot.answer_callback_query(callback_query_id=call.id, text="Возврат к списку кружков...")
            start(call.message)

    except Exception as e:
        logging.error(f"Ошибка обработки callback-запроса: {e}, данные: {call.data}")
        bot.answer_callback_query(callback_query_id=call.id, text="Произошла ошибка.")


@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    global message_count
    message_count += 1
    if message_count == 1:
        bot.reply_to(message, "Напишите ваш класс") 
    elif message_count == 2:
        bot.send_message(message.chat.id, "Здравствуй!")
        bot.send_message(message.chat.id, 'Это бот для удобной работы с дополнительными кружками Силаэдра!')
        bot.reply_to(message, "Теперь напишите /start для продолжения работы с ботом")
        message_count = 0 
import atexit
@atexit.register
def save_registered_users():
    try:
        with open("registered_users.txt", "w", encoding="utf-8") as f:
            f.write(str(registered_users))
    except Exception as e:
        logging.error(f"Ошибка сохранения данных о зарегистрированных пользователях: {e}")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.exception(f"Ошибка в polling: {e}")
