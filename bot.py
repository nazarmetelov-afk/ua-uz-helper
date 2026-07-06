import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import re

TOKEN = "ВАШ_ТОКЕН_БОТА"
bot = telebot.TeleBot(TOKEN)

# Исправленная функция парсинга с защитой от блокировок
def parse_vagon_by(model_name):
    model_cleaned = model_name.strip()
    url = f"https://vagon.by/model/{model_cleaned}"
    
    # Расширенные заголовки, чтобы сайт не блокировал Render
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=7)
        
        # Если сайт заблокировал запрос (например, ошибка 403 или 503)
        if response.status_code != 200:
            return f"⚠️ Сайт vagon.by повернув помилку {response.status_code}.\nМожливо, діє захист від автоматичних запитів. Спробуйте відкрити вручну:\n🔗 {url}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else f"Вагон моделі {model_name}"
        
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            details = []
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) == 2:
                    key = cols[0].text.strip()
                    val = cols[1].text.strip()
                    val = re.sub(r'\s+', ' ', val)
                    details.append(f"• **{key}:** {val}")
            
            if details:
                characteristics = "\n".join(details[:12])
                return f"🚛 **{title}**\n\n📊 **Технічні характеристики:**\n{characteristics}\n\n🔗 [Відкрити на vagon.by]({url})"
        
        return f"🚛 **{title}**\n\nДані на сторінці є, але таблицю характеристик не вдалося розібрати автоматично.\n🔗 [Відкрити сайт вручну]({url})"
        
    except requests.exceptions.Timeout:
        return f"⏱️ Сайт vagon.by відповідав занадто довго. Спробуйте пізніше або перейдіть за посиланням:\n🔗 {url}"
    except Exception as e:
        return f"❌ Сталася помилка при підключенні до сайту.\n🔗 [Перейти на vagon.by вручну]({url})"

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
        bot.send_message(message.chat.id, "Введіть номер аварійної картки (наприклад, 328):")
        return
    elif text == "☣️ Небезпечні вантажі (UN)":
        bot.send_message(message.chat.id, "Введіть номер ООН (наприклад, 1075):")
        return
    elif text == "🚛 Вагони та цистерни":
        bot.send_message(message.chat.id, "Введіть модель цистерни або вагона (наприклад: `15-1443`):", parse_mode="Markdown")
        return

    # Логика проверки модели (ищет дефис или если это модель из цифр)
    if "-" in text or (text.isdigit() and len(text) > 4):
        bot.send_message(message.chat.id, f"🔍 Запит відправлено. Шукаю модель `{text}`...", parse_mode="Markdown")
        online_result = parse_vagon_by(text)
        bot.send_message(message.chat.id, online_result, parse_mode="Markdown", disable_web_page_preview=True)
        return

    # Ответы на обычные цифры (карточки/ООН)
    if text.isdigit():
        if text == "328":
            response = "📋 **Аварійна картка №328**\n\n• **Вантаж:** Гази вуглеводневі зріджені\n• **Дії:** Евакуація 800м."
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        elif text == "1075":
            response = "☣️ **ООН 1075**\n\n• **Назва:** Зріджені вуглеводневі гази (СУГ)"
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, f"Номер `{text}` не знайдено в демо-базі. Спробуйте 328 або 1075.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Скористайтеся кнопками меню або введіть модель цистерни (наприклад, 15-1443).")

if __name__ == '__main__':
    bot.infinity_polling()
