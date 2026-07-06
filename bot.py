import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🚆 UA.УЗ. Справочник\n\n"
        "Бот успешно запущен!\n\n"
        "Доступные команды:\n"
        "📄 328 — аварийная карточка\n"
        "☣️ UN 1075 — поиск опасного груза"
    )


@dp.message()
async def search(message: Message):
    text = message.text.upper().strip()

    if text == "328":
        await message.answer("📄 Аварийная карточка №328 (пока тестовая версия).")
    elif text.startswith("UN"):
        await message.answer(f"☣️ Поиск по номеру: {text}")
    else:
        await message.answer("Не понял запрос. Попробуй: 328 или UN 1075")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())