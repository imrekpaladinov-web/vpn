import os
import requests
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio

TOKEN = os.getenv("TOKEN")
API_URL = os.getenv("API_URL")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.MARKDOWN
    )
)

dp = Dispatcher()


@dp.message()
async def handle_message(message: Message):

    # Игнорируем команды
    if not message.text:
        return

    if message.text.startswith("/"):
        return

    # Сообщение ожидания
    wait_msg = await message.answer(
        "_ACF AI думает, подождите пожалуйста! 🧡_"
    )

    try:

        payload = {
            "prompt": message.text
        }

        response = requests.post(
            API_URL,
            json=payload,
            timeout=180
        )

        # Проверка ответа
        if response.status_code != 200:
            await wait_msg.delete()

            await message.answer(
                "Ошибка API."
            )
            return

        data = response.json()

        answer = data.get("answer", "")

        # Если пусто
        if not answer:
            answer = "Не удалось сгенерировать ответ."

        # Убираем мусор markdown
        answer = answer.replace("```", "")
        answer = answer.replace("###", "")
        answer = answer.replace("##", "")
        answer = answer.replace("#", "")
        answer = answer.replace("**", "")
        answer = answer.replace("__", "")

        # Убираем возможный системный промпт
        bad_phrases = [
            "ТВОИ ПРАВИЛА",
            "Ты — профессиональная",
            "SYSTEM_PROMPT",
            "Пользователь:",
            "Ассистент:"
        ]

        for phrase in bad_phrases:
            if phrase in answer:
                answer = "Не удалось сгенерировать ответ."
                break

        answer = answer.strip()

        # Telegram не любит пустой текст
        if len(answer.strip()) == 0:
            answer = "Не удалось сгенерировать ответ."

        # Ограничение Telegram
        answer = answer[:4000]

        # Делаем текст жирным
        answer = f"*{answer}*"

        # Удаляем сообщение ожидания
        try:
            await wait_msg.delete()
        except:
            pass

        # Отправляем ответ
        await message.answer(answer)

    except Exception as e:

        print("ERROR:", e)

        try:
            await wait_msg.delete()
        except:
            pass

        await message.answer(
            "Не удалось сгенерировать ответ."
        )


async def main():

    print(">>> BOT STARTED <<<")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
