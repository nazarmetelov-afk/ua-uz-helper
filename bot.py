import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

TOKEN = "8816399169:AAEeCdexznbCh4vTKqBWqE8gRYTqWIspWV0"
bot = telebot.TeleBot(TOKEN)

# Универсальная функция парсинга любого запроса
def parse_vagon_by(model_name):
    # Убираем пробелы по краям
    clean_model = model_name.strip()
    url = f"https://vagon.by/model/{clean_model}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return f"⚠️ Модель `{clean_model}` не знайдено на сайті vagon.by або доступ тимчасово обмежено.\nПеревірте правильність вводу або відкрийте посилання:\n🔗 {url}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else f"Вагон {clean_model}"
        
        table = soup.find('table')
        if not table:
            return f"🚛 **{title}**\n\nСторінку знайдено, але таблиця технічних характеристик порожня.\n🔗 {url}"
            
        rows = table.find_all('tr')
        details = []
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) == 2:
                key = cols[0].text.strip()
                val = cols[1].text.strip()
                details.append(f"• **{key}:** {val}")
        
        if details:
            characteristics = "\n".join(details[:12])
            return f"🚛 **{title}**\n\n📊 **Технічні характеристики:**\n{characteristics}\n\n🔗 [Відкрити джерело на vagon.by]({url})"
        
        return f"🚛 **{title}**\n\nНе вдалося автоматично зчитати характеристики.\n🔗 {url}"
        
    except Exception as e:
        return f"❌ Помилка підключення до бази даних сайту.\n🔗 Спробуйте перейти вручну: {url}"

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📄 Аварійні картки"),
        types.KeyboardButton("☣️ Небезпечні вантажі (UN)"),
        types.KeyboardButton("🚛 Вагони та 4истерни"),
        types.KeyboardButton("📷 Розпізнати фото")
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "🚆 **ЖД Помічник UA** готовий до пошуку!", 
        reply_markup=get_main_menu(), 
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    text = message.text.strip()

    if text == "📄 Аварійні картки":
        msg = bot.send_message(message.chat.id, "Введіть номер аварійної картки (наприклад, 328):")
        bot.register_next_step_handler(msg, process_emergency_card)
        return
        
    elif text == "☣️ Небезпечні вантажі (UN)":
        msg = bot.send_message(message.chat.id, "Введіть номер ООН (наприклад, 1075):")
        bot.register_next_step_handler(msg, process_un_number)
        return
        
    elif text == "🚛 Вагони та цистерни":
        # Включаем режим ожидания ЛЮБОГО ввода от пользователя
        msg = bot.send_message(message.chat.id, "Введіть **будь-який** номер моделі вагона або цистерни (наприклад: `15-1443`, `11-280`, `15-150-04`):", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_wagon_search)
        return

    # Если пользователь просто отправил текст в чат вне меню
    bot.send_message(message.chat.id, "Будь ласка, скористайтеся кнопками меню для вибору розділу.")

# Логика обработки ввода модели вагона (сработает на ВСЁ, что вы введете)
def process_wagon_search(message):
    model = message.text.strip()
    bot.send_message(message.chat.id, f"🔍 Шукаю модель `{model}` на vagon.by...", parse_mode="Markdown")
    
    result = parse_vagon_by(model)
    bot.send_message(message.chat.id, result, parse_mode="Markdown", disable_web_page_preview=True)

# Логика обработки аварийных карточек
def process_emergency_card(message):
    card = message.text.strip()
    if card == "328":
        bot.send_message(message.chat.id, "📋 **Аварійна картка №328**\n• Гази вуглеводневі зріджені.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"Картку №{card} не знайдено в демо-базі.")

# Логика обработки UN номеров
def process_un_number(message):
    un = message.text.strip()
    if un == "1075":
        bot.send_message(message.chat.id, "☣️ **ООН 1075**\n• Назва: Зріджені вуглеводневі гази.", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"Номер ООН {un} не знайдено в демо-базі.")

if __name__ == '__main__':
    bot.infinity_polling()
