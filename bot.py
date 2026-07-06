import telebot
from telebot import types

# ⚠️ ВСТАВТЕ СВІЙ ТОКЕН СЮДИ (отриманий від @BotFather)
TOKEN = "8816399169:AAEeCdexznbCh4vTKqBWqE8gRYTqWIspWV0"
bot = telebot.TeleBot(TOKEN)

# Головне меню
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📄 Аварійні картки")
    btn2 = types.KeyboardButton("☣️ Небезпечні вантажі (UN)")
    btn3 = types.KeyboardButton("🚛 Вагони та цистерни")
    btn4 = types.KeyboardButton("📷 Розпізнати фото")
    btn5 = types.KeyboardButton("🧮 Калькулятор")
    btn6 = types.KeyboardButton("❓ Запитати ШІ")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "🚆 **ЖД Помічник UA** вітає вас!\n\nОберіть потрібний розділ меню нижче для початку роботи:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

# Обробка текстових кнопок та пошуку
@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.strip()

    if text == "📄 Аварійні картки":
        bot.send_message(message.chat.id, "Введіть номер аварійної картки (наприклад, 328):")
    
    elif text == "☣️ Небезпечні вантажі (UN)":
        bot.send_message(message.chat.id, "Введіть номер ООН (наприклад, UN 1075):")
        
    elif text == "🚛 Вагони та цистерни":
        bot.send_message(message.chat.id, "Розділ бази даних моделей вагонів (у розробці).")
        
    elif text == "📷 Розпізнати фото":
        bot.send_message(message.chat.id, "Надішліть мені чітке фото цистерни або вагона, де видно номер чи маркування.")
        
    elif text == "🧮 Калькулятор":
        bot.send_message(message.chat.id, "Функція розрахунку заповнення цистерн з'явиться найближчим часом.")
        
    elif text == "❓ Запитати ШІ":
        bot.send_message(message.chat.id, "Напишіть своє складне запитання щодо правил перевезень, і ШІ спробує допомогти.")
        
    # Приклад пошуку аварійної картки 328
    elif text == "328":
        response = (
            "📋 **Аварійна картка №328**\n\n"
            "• **Назва вантажу:** Гази вуглеводневі зріджені\n"
            "• **Основні небезпеки:** Вогненебезпечно, вибухонебезпечно при нагріванні, задушлива дія.\n"
            "• **Дії при аварії:** Евакуювати людей, усунути джерела вогню, охолоджувати цистерну водою."
        )
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
        
    # Приклад пошуку за UN 1075
    elif text.upper() in ["UN 1075", "1075"]:
        response = (
            "☣️ **Інформація про вантаж (ООН 1075)**\n\n"
            "• **Назва:** Зріджені вуглеводневі гази (СУГ)\n"
            "• **Клас небезпеки:** 2 (Гази)\n"
            "• **Код небезпеки (КЕМ):** 23 (Займистий газ)"
        )
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
        
    else:
        bot.send_message(message.chat.id, "Я вас не зрозумів. Скористайтеся меню або введіть коректний номер (наприклад, 328 або 1075).")

# Обробка надісланих фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.send_message(message.chat.id, "Фото отримано! 🔄 Аналізую зображення вагона...")
    # Тут пізніше буде код для розпізнавання (OCR / AI)
    demo_response = (
        "📊 **Результат розпізнавання (Демо):**\n"
        "• **Модель цистерны:** 15-150-04\n"
        "• **Об'єм:** 54 м³\n"
        "• **Вантажопідйомність:** 66 т\n"
        "• **Рік побудови:** 2018"
    )
    bot.send_message(message.chat.id, demo_response, parse_mode="Markdown")

# Запуск бота
if __name__ == '__main__':
    print("Бот успішно запущений...")
    bot.infinity_polling()
