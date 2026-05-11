import os
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from aiogram.filters import CommandStart
import asyncio

TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("KAGGLE_API")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "*ACF Artificial Intelligence запущен 🧡*\n\n"
        "Пиши свой вопрос."
    )


@dp.message(F.text)
async def ai_chat(message: Message):

    wait_msg = await message.answer(
        "_ACF AI думает, подождите пожалуйста! 🧡_"
    )

    try:
        async with aiohttp.ClientSession() as session:

            payload = {
                "text": message.text
            }

            async with session.post(API_URL, json=payload, timeout=300) as resp:

                data = await resp.json()

                answer = data.get("answer", "").strip()

                # защита от пустого ответа
                if not answer:
                    answer = "Не удалось сгенерировать ответ."

                # убираем возможный prompt
                if "ТВОИ ПРАВИЛА" in answer:
                    parts = answer.split("Пользователь:")
                    answer = parts[-1].strip()

                # делаем жирным
                answer = f"*{answer}*"

                # ограничение Telegram
                answer = answer[:4000]

                await wait_msg.delete()

                await message.answer(answer)

    except Exception as e:

        await wait_msg.delete()

        await message.answer(
            f"Ошибка AI:\n`{str(e)[:3500]}`"
        )


async def main():
    print(">>> BOT STARTED <<<")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
