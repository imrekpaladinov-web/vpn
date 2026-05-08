import asyncio
import logging
import os
import time

from openai import OpenAI

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =========================
# CONFIG
# =========================

BOT_TOKEN = "8620489449:AAHwbVrlg0J74MGAZRoQ9yO1_7ZWokQ3xQQ"

API_KEYS = [
    "sk-1dcd4dd9501f4e74835dba1b35f2b77f",
    "sk-fbd9f58a79604a3dae3eae2ca052662f",
    "sk-fa1eafb9699846369bce36dd4cbbe146",
    "sk-cc1e91b597424ef087ce47b4778a0b0e",
    "sk-faf61e964d97439ab11fd35c5f44dc2b",
    "sk-66322bda747c427d833c6f593d2f8c9e",
    "sk-35916cff53e443e6a60e802edad13e87",
    "sk-7a766b3b329b46aa85ca52357367f1d7",
    "sk-48352573e99d41df9829986ca4fb860d",
    "sk-a1d558434cbf4573a5512e42b8b3f601"
]

MODEL_NAME = "deepseek-v4-flash"

MAX_TOKENS = 1000

COOLDOWN = 20

# =========================
# LOGGING
# =========================

logging.basicConfig(level=logging.INFO)

# =========================
# BOT
# =========================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# API ROTATION
# =========================

current_key_index = 0

def get_client():

    global current_key_index

    api_key = API_KEYS[current_key_index]

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"
    )

    return client

def switch_api():

    global current_key_index

    current_key_index += 1

    if current_key_index >= len(API_KEYS):
        current_key_index = 0

# =========================
# LOAD KNOWLEDGE FILE
# =========================

try:

    with open("ACF файловое.txt", "r", encoding="utf-8") as f:
        ACF_KNOWLEDGE = f.read()

    print(">>> БАЗА ЗНАНИЙ ЗАГРУЖЕНА <<<")

except Exception as e:

    print(f"Ошибка загрузки файла: {e}")

    ACF_KNOWLEDGE = "База знаний не загружена."

# =========================
# USER COOLDOWNS
# =========================

user_cooldowns = {}

# =========================
# START
# =========================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):

    await message.answer(
        "Привет я Anime Characters Fight AI ! Я готов помочь тебе с любыми вопросами. Пиши свой вопрос сюда, прямо в чат. 🌐"
    )

# =========================
# AI CHAT
# =========================

@dp.message()
async def ai_chat(message: types.Message):

    user_id = message.from_user.id

    current_time = time.time()

    if user_id in user_cooldowns:

        last_time = user_cooldowns[user_id]

        if current_time - last_time < COOLDOWN:

            wait_time = int(COOLDOWN - (current_time - last_time))

            await message.answer(
                f"Вы уже отправляли запрос, попробуйте через {wait_time} секунд."
            )

            return

    user_cooldowns[user_id] = current_time

    user_question = message.text

    wait_msg = await message.answer("🤖 AI думает...")

    success = False

    for _ in range(len(API_KEYS)):

        try:

            client = get_client()

            system_prompt = f"""
Ты — эксперт по Anime Characters Fight Wiki (ACF).

Ты ОБЯЗАН отвечать ТОЛЬКО используя информацию из базы знаний ниже.

Если информации нет в базе знаний — так и скажи.

Никогда не придумывай информацию.

База знаний:
{ACF_KNOWLEDGE}
"""

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_question
                    }
                ],
                temperature=0.7,
                max_tokens=MAX_TOKENS
            )

            answer = response.choices[0].message.content

            if not answer:
                answer = "AI не смог дать ответ."

            if len(answer) > 4000:
                answer = answer[:4000]

            await wait_msg.edit_text(answer)

            success = True

            break

        except Exception as e:

            error_text = str(e).lower()

            print(f"Ошибка ключа: {e}")

            if (
                "429" in error_text
                or "rate limit" in error_text
                or "quota" in error_text
                or "insufficient" in error_text
            ):

                switch_api()

                continue

            else:

                await wait_msg.edit_text(
                    f"❌ Ошибка AI: {e}"
                )

                success = True

                break

    if not success:

        await wait_msg.edit_text(
            "❌ Все API ключи временно перегружены. Отправьте запрос позже."
        )

# =========================
# MAIN
# =========================

async def main():

    print(">>> ACF AI ЗАПУЩЕН <<<")

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
