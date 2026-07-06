import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

TOKEN = "8816399169:AAEeCdexznbCh4vTKqBWqE8gRYTqWIspWV0"
bot = telebot.TeleBot(TOKEN)

# Список головних кнопок, щоб бот розумів, коли користувач передумав і нажав меню
MENU_BUTTONS = [
    "📄 Аварійні картки", 
    "☣️ Небезпечні вантажі (UN)", 
    "🚛 Вагони та цистерни", 
    "🔢 Пошук за номером вагона",
    "📷 Rozпізнати фото",
    "🧮 Калькулятор",
    "❓ Запитати ШІ"
]

# Заголовки для маскування під реальний браузер
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,uk-UA;q=0.8,uk;q=0.7,en-US;q=0.6,en;q=0.5"
}

# ================= 1. ФУНКЦІЇ ПОШУКУ ТА ПАРСИНГУ =================

def parse_emergency_card_online(card_number):
    """Парсинг аварійної картки напряму з сайту bazanpa.ru"""
    clean_card = card_number.strip()
    url = f"https://bazanpa.ru/szht-sng-protokol-ot30052008-h1492538/avariinaia-kartochka-{clean_card}/"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=7)
        if response.status_code == 404:
            return f"⚠️ **Картку № {clean_card} не знайдено** на сайті.\nПеревірте, чи правильно вказано номер."
        elif response.status_code != 200:
            return f"⚠️ Не вдалося отримати дані з сайту (Код: {response.status_code}).\n🔗 Спробуйте відкрити вручну:\n{url}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', class_='document-text') or soup.find('main')
        if not content_div:
            return f"📋 **Аварійна картка № {clean_card} знайдена**, але не вдалося автоматично зчитати її текст.\n🔗 [Відкрити на сайті]({url})"
        
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else f"Аварійна картка № {clean_card}"
        
        paragraphs = content_div.find_all('p')
        text_lines = []
        for p in paragraphs:
            p_text = p.text.strip()
            if p_text and not p_text.startswith("Назад") and not p_text.startswith("Вперед"):
                text_lines.append(p_text)
                
        if text_lines:
            summary = "\n\n".join(text_lines[:5])
            if len(summary) > 3500:
                summary = summary[:3500] + "...\n\n*(текст скорочено через ліміти Telegram)*"
            return f"📄 **{title}**\n\n{summary}\n\n🔗 [Читати повну версію на сайті]({url})"
        
        return f"📋 **Аварійна картка № {clean_card}**\n\nТекст картки порожній.\n🔗 [Переглянути на сайті]({url})"
    except requests.exceptions.Timeout:
        return "❌ Перевищено час очікування відповіді від сайту. Спробуйте пізніше."
    except Exception as e:
        return f"❌ Помилка при підключенні до сайту або обробці даних.\n🔗 Спробуйте вручну: {url}"


def parse_un_number_online(un_number):
    """Парсинг інформації про небезпечний вантаж за номером ООН з сайту bazanpa.ru"""
    clean_un = un_number.strip()
    
    # Формуємо посилання під стандарт сайту для номерів ООН
    url = f"https://bazanpa.ru/szht-sng-protokol-ot30052008-h1492538/un-{clean_un}/"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=7)
        if response.status_code == 404:
            return f"⚠️ **Вантаж ООН {clean_un} не знайдено** на сайті.\nПеревірте правильність введення (вносьте лише 4 цифри)."
        elif response.status_code != 200:
            return f"⚠️ Не вдалося отримати дані про ООН {clean_un} (Код: {response.status_code}).\n🔗 Посилання: {url}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content_div = soup.find('div', class_='document-text') or soup.find('main')
        if not content_div:
            return f"☣️ **Вантаж ООН {clean_un} знайдено**, але не вдалося зчитати опис.\n🔗 [Відкрити на сайті]({url})"
        
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else f"Небезпечний вантаж ООН {clean_un}"
        
        paragraphs = content_div.find_all('p')
        text_lines = []
        for p in paragraphs:
            p_text = p.text.strip()
            if p_text and not p_text.startswith("Назад") and not p_text.startswith("Вперед"):
                text_lines.append(p_text)
                
        if text_lines:
            summary = "\n\n".join(text_lines[:5])
            if len(summary) > 3500:
                summary = summary[:3500] + "...\n\n*(текст скорочено)*"
            return f"☣️ **{title}**\n\n{summary}\n\n🔗 [Детальніше на сайті]({url})"
        
        return f"☣️ **Вантаж ООН {clean_un}**\n\nОпис вантажу порожній.\n🔗 [Переглянути на сайті]({url})"
    except requests.exceptions.Timeout:
        return "❌ Перевищено час очікування від сайту. Спробуйте пізніше."
    except Exception as e:
        return f"❌ Помилка обробки даних вантажу ООН.\n🔗 Спробуйте вручну: {url}"


def parse_vagon_by(model_name):
    clean_model = model_name.strip()
    url = f"https://vagon.by/model/{clean_model}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            return f"⚠️ Модель `{clean_model}` не знайдено на сайті vagon.by.\nПеревірте правильність вводу або відкрийте посилання:\n🔗 {url}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else f"Вагон {clean_model}"
        
        table = soup.find('table')
        if not table:
            return f"🚛 **{title}**\n\nСторінку знайдено, але таблиця характеристик порожня.\n🔗 {url}"
            
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
        return f"❌ Помилка підключення до сайту.\n🔗 Спробуйте вручну: {url}"


def get_wagon_type_by_number(number_str):
    if not number_str.isdigit() or len(number_str) != 8:
        return "⚠️ Номер вагона має складатися рівно з 8 цифр."
    
    first_digit = number_str[0]
    weights = [2, 1, 2, 1, 2, 1, 2]
    total_sum = 0
    for i in range(7):
        prod = int(number_str[i]) * weights[i]
        total_sum += sum(map(int, str(prod)))
    
    next_ten = ((total_sum // 10) + 1) * 10
    if total_sum % 10 == 0:
        next_ten = total_sum
    correct_checksum = next_ten - total_sum
    
    if int(number_str[7]) == correct_checksum:
        checksum_status = "✅ **Номер коректний** (контрольне число збігається)."
    else:
        checksum_status = f"❌ **Помилка!** Контрольна цифра має бути `{correct_checksum}`, а введено `{number_str[7]}`."

    wagon_types = {
        '2': "🏠 **Критий вагон**",
        '4': "📦 **Платформа**",
        '6': "🗑️ **Піввагон (Полувагон)**",
        '7': "⚡ **Цистерна**",
        '8': "❄️ **Ізотермічний вагон**",
        '3': "🪨 **Спеціальний вагон / Хоппер**",
        '9': "🏗️ **Інші вагони (спецтехніка)**",
        '0': "Pass **Пасажирський вагон**"
    }
    
    type_desc = wagon_types.get(first_digit, "Невідомий рід вагона")
    url = f"https://vagon.by/number/{number_str}"
    
    return (
        f"🔢 **Аналіз вагона № {number_str}**\n\n"
        f"• {checksum_status}\n"
        f"• **Рід вагона:** {type_desc}\n\n"
        f"🔗 [Переглянути деталі на vagon.by]({url})"
    )

# ================= 2. СТВОРЕННЯ КНОПОК МЕНЮ =================
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("📄 Аварійні картки"),
        types.KeyboardButton("☣️ Небезпечні вантажі (UN)"),
        types.KeyboardButton("🚛 Вагони та цистерни"),
        types.KeyboardButton("🔢 Пошук за номером вагона"),
        types.KeyboardButton("📷 Розпізнати фото"),
        types.KeyboardButton("🧮 Калькулятор"),
        types.KeyboardButton("❓ Запитати ШІ")
    )
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id, 
        "🚆 **ЖД Помічник UA** готовий до роботи!\nОнлайн-пошук аварійних карток та номерів ООН підключено.", 
        reply_markup=get_main_menu(), 
        parse_mode="Markdown"
    )

# ================= 3. ОБРОБКА НАВІГАЦІЇ МЕНЮ =================
@bot.message_handler(content_types=['text'])
def handle_text(message):
    route_menu(message)


def route_menu(message):
    text = message.text.strip()

    if text == "📄 Аварійні картки":
        msg = bot.send_message(message.chat.id, "Введіть номер аварійної картки (наприклад, 328):")
        bot.register_next_step_handler(msg, process_emergency_card)
        return
    elif text == "☣️ Небезпечні вантажі (UN)":
        msg = bot.send_message(message.chat.id, "Введіть 4-значний номер ООН (наприклад, 1075):")
        bot.register_next_step_handler(msg, process_un_number)
        return
    elif text == "🚛 Вагони та цистерни":
        msg = bot.send_message(message.chat.id, "Введіть **номер моделі** вагона (наприклад: `15-1443`):", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_wagon_search)
        return
    elif text == "🔢 Пошук за номером вагона":
        msg = bot.send_message(message.chat.id, "Введіть **8-значний номер** вагона для аналізу:")
        bot.register_next_step_handler(msg, process_number_search)
        return
    elif text == "📷 Розпізнати фото":
        bot.send_message(message.chat.id, "🛠️ Функція розпізнавання фото знаходиться у розробці.")
        return
    elif text == "🧮 Калькулятор":
        bot.send_message(message.chat.id, "🧮 Розрахунок залізничних тарифів буде додано у наступних оновленнях.")
        return
    elif text == "❓ Запитати ШІ":
        bot.send_message(message.chat.id, "🤖 Модуль штучного інтелекту наразі підключається.")
        return

    bot.send_message(message.chat.id, "Будь ласка, скористайтеся кнопками меню для вибору розділу.")

# ================= 4. КРОКИ ОБРОБКИ ВВОДУ =================
def process_wagon_search(message):
    if message.text in MENU_BUTTONS:
        route_menu(message)
        return
    model = message.text.strip()
    bot.send_message(message.chat.id, f"🔍 Шукаю модель `{model}` на vagon.by...", parse_mode="Markdown")
    result = parse_vagon_by(model)
    bot.send_message(message.chat.id, result, parse_mode="Markdown", disable_web_page_preview=True)


def process_number_search(message):
    if message.text in MENU_BUTTONS:
        route_menu(message)
        return
    num = message.text.strip()
    result = get_wagon_type_by_number(num)
    bot.send_message(message.chat.id, result, parse_mode="Markdown", disable_web_page_preview=True)


def process_emergency_card(message):
    if message.text in MENU_BUTTONS:
        route_menu(message)
        return
    card = message.text.strip()
    if not card.isdigit():
        bot.send_message(message.chat.id, "⚠️ Номер аварійної картки має складатися лише з цифр.")
        return
    bot.send_message(message.chat.id, f"🔍 Запитую дані для картки №{card} з сайту bazanpa.ru...")
    result = parse_emergency_card_online(card)
    bot.send_message(message.chat.id, result, parse_mode="Markdown", disable_web_page_preview=True)


def process_un_number(message):
    if message.text in MENU_BUTTONS:
        route_menu(message)
        return
    un = message.text.strip()
    
    # Перевірка на дурня (номери ООН завжди чотиризначні цифри)
    if not un.isdigit() or len(un) != 4:
        bot.send_message(message.chat.id, "⚠️ Номер ООН (UN) повинен складатися рівно з 4 цифр (наприклад: 1075).")
        return
        
    bot.send_message(message.chat.id, f"🔍 Шукаю інформацію про вантаж ООН {un} на сайті bazanpa.ru...")
    result = parse_un_number_online(un)
    bot.send_message(message.chat.id, result, parse_mode="Markdown", disable_web_page_preview=True)


if __name__ == '__main__':
    bot.infinity_polling()
