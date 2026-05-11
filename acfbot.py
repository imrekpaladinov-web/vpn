from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart

import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)

dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "Привет, я нейросеть по ACF. "
        "Задай мне любой вопрос и я отвечу. 🎉"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
