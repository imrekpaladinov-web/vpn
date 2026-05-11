from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

import asyncio
import os
import requests

TOKEN = os.getenv("BOT_TOKEN")

KAGGLE_API = os.getenv("KAGGLE_API")

bot = Bot(token=TOKEN)

dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "Привет, я нейросеть по ACF. "
        "Задай мне любой вопрос и я отвечу. 🎉"
    )

@dp.message()
async def ai(message: Message):

    try:

        r = requests.post(
            f"{KAGGLE_API}/generate",
            json={
                "text": message.text
            },
            timeout=120
        )

        data = r.json()

        answer = data["response"]

    except Exception as e:

        answer = f"Ошибка: {e}"

    await message.answer(answer[:4000])

async def main():

    print("BOT STARTED")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
