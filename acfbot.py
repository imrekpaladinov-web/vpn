import os
import asyncio
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("KAGGLE_API")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()


@dp.message(F.text)
async def chat(message: Message):

    wait_msg = await message.answer(
        "<i>ACF AI думает, подождите пожалуйста! 🧡</i>"
    )

    try:

        response = requests.post(
            f"{API_URL}/generate",
            json={
                "text": message.text
            },
            timeout=300
        )

        data = response.json()

        print(data)

        # поддержка любых ответов от kaggle
        answer = (
            data.get("answer")
            or data.get("response")
            or data.get("text")
            or str(data)
        )

        if not answer:
            answer = "Не удалось получить ответ."

        # ограничение telegram
        answer = answer[:4000]

        # жирный текст
        answer = f"<b>{answer}</b>"

        await wait_msg.delete()

        await message.answer(answer)

    except Exception as e:

        await wait_msg.delete()

        await message.answer(
            f"<b>Ошибка:</b>\n<code>{e}</code>"
        )


async def main():

    print("BOT STARTED")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
