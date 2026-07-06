import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import re

TOKEN = "ВАШ_ТОКЕН_БОТА"
bot = telebot.TeleBot(TOKEN)

# Функция автоматического парсинга с сайта vagon.by
def parse_vagon_by(model_name):
    # Формируем чистый URL (убираем лишние пробелы)
    model_cleaned = model_name.strip()
    url = f"https://vagon.by/model/{model_cleaned}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Находим главный заголовок (название вагона)
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else f"Вагон моделі {model_name}"
        
        # Находим таблицу с техническими характеристиками
        table = soup.find('table', {'class': 'table'}) # ищем таблицу характеристик
        if not table:
            # Если класс таблицы другой, ищем просто первую попавшуюся таблицу
            table = soup.find('table')
            
        if torch := table:
            rows = torch.find_all('tr')
            details = []
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    val = cols[1].text.strip()
                    # Убираем лишние пробелы и переносы строк внутри текста
                    val = re.sub(r'\s+', ' ', val)
                    details.append(f"• **{key}:** {val}")
            
            if details:
                characteristics = "\n".join(details[:10]) # берем первые 10 главных характеристик
                return f"🚛 **{title}**\n\n📊 **Технічні характеристики з сайту vagon.by:**\n{characteristics}\n\n🔗 [Посилання на джерело]({url})"
        
        return f"🚛 **{title}**\n\nДанні на сайті є, але не вдалося автоматично прочитати таблицю характеристик.\n🔗 [Відкрити на сайті]({url})"
        
    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        return None

# Главное меню
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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "🚆 **ЖД Помічник UA** вітає вас!\n\nОберіть потрібний розділ меню нижче для початку роботи:"
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu(), parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.strip()

    if text == "📄 Аварійні картки":
        bot.send_message(message.chat.id, "Введіть номер аварійної картки (например, 328):")
        return
    elif text == "☣️ Небезпечні вантажі (UN)":
        bot.send_message(message.chat.id, "Введіть номер ООН (например, 1075):")
        return
    elif text == "🚛 Вагони та цистерни":
        bot.send_message(message.chat.id, "Введіть модель цистерни або вагона (наприклад: `15-1443` або `15-150-04`):", parse_mode="Markdown")
        return

    # Проверка: если текст похож на модель вагона (содержит дефис, например 15-1443)
    if "-" in text and len(text) >= 5:
        bot.send_message(message.chat.id, f"🔍 Шукаю модель `{text}` на vagon.by...", parse_mode="Markdown")
        
        # Запускаем живой поиск по сайту
        online_result = parse_vagon_by(text)
        if online_result:
            bot.send_message(message.chat.id, online_result, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            bot.send_message(message.chat.id, f"❌ Не вдалося знайти модель `{text}` автоматично. Перевірте правильність написання (наприклад, 15-1443).", parse_mode="Markdown")
        return

    # Стандартные ответы на тесты (как в версии 1.0)
    if text == "328":
        response = "📋 **Аварійна картка №328**\n\n• **Вантаж:** Гази вуглеводневі зріджені\n• **Дії:** Евакуація 800м."
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    elif text in ["1075", "UN 1075"]:
        response = "☣️ **ООН 1075**\n\n• **Назва:** Зріджені вуглеводневі гази (СУГ)"
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Скористайтеся кнопками меню або введіть модель цистерни з дефісом (наприклад, 15-1443).")

if __name__ == '__main__':
    bot.infinity_polling()
