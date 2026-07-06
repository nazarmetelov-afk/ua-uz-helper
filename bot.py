
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

TOKEN = 8816399169:AAEeCdexznbCh4vTKqBWqE8gRYTqWIspWV0
bot = telebot.TeleBot(TOKEN)

def parse_vagon_by(model_name):
    url = f"https://vagon.by/model/{model_name.strip()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return f"⚠️ Не вдалося отримати дані з сайту (Помилка {response.status_code}). Спробуйте вручну:\n🔗 {url}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Шукаємо заголовок
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else f"Вагон {model_name}"
        
        # Шукаємо таблицю
        table = soup.find('table')
        if not table:
            return f"🚛 **{title}**\n\nХарактеристики на сторінці не знайдено.\n🔗 {url}"
            
        rows = table.find_all('tr')
        details = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) == 2:
                key = cols[0].text.strip()
                val = cols[1].text.strip()
                details.append(f"• **{key}:** {val}")
        
        if details:
            characteristics = "\n".join(details[:10])
            return f"🚛 **{title}**\n\n📊 **Технічні характеристики:**\n{characteristics}\n\n🔗 [Джерело]({url})"
        
        return f"🚛 **{title}**\n\nНе вдалося розпізнати таблицю.\n🔗 {url}"
        
    except Exception as e:
        return f"❌ Помилка з'єднання з сайтом.\n🔗 Перевірте вручну: {url}"

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📄 Аварійні картки"),
        types.KeyboardButton("☣️ Небезпечні вантажі (UN)"),
        types.KeyboardButton("🚛 Вагони та цистерни"),
        types.KeyboardButton("📷 Rozpiznaty")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "🚆 **ЖД Помічник UA** готовий до роботи!", 
        reply_markup=get_main_menu(), 
        parse_mode="Markdown"
    )

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
        bot.send_message(message.chat.id, "Введіть модель цистерни з дефісом (наприклад: `15-1443`):", parse_mode="Markdown")
        return

    # Якщо користувач ввів модель (містить дефис)
    if "-" in text:
        bot.send_message(message.chat.id, f"🔍 Шукаю модель `{text}` на vagon.by...", parse_mode="Markdown")
        result = parse_vagon_by(text)
        bot.send_message(message.chat.id, result, parse_mode="Markdown", disable_web_page_preview=True)
        return

    # Заглушки для тестів
    if text == "328":
        bot.send_message(message.chat.id, "📋 **Аварійна картка №328**\n• Гази вуглеводневі зріджені.", parse_mode="Markdown")
    elif text == "1075":
        bot.send_message(message.chat.id, "☣️ **ООН 1075**\n• Зріджені гази.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Будь ласка, оберіть пункт меню або введіть модель (наприклад, 15-1443).")

if __name__ == '__main__':
    bot.infinity_polling()
