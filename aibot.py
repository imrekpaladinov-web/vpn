import asyncio
import logging
import os
import time

import cohere

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_AI")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

MODEL_NAME = "command-a"

MAX_TOKENS = 700

COOLDOWN = 30

MAX_DAILY_REQUESTS = 10

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
# COHERE CLIENT
# =========================

client = cohere.ClientV2(
    api_key=COHERE_API_KEY
)

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
# DAILY LIMITS
# =========================

daily_limits = {}

# =========================
# START
# =========================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):

    await message.answer(
        "Привет я Anime Characters Fight AI ! Я готов помочь тебе с любыми вопросами. 🌐"
    )

# =========================
# AI CHAT
# =========================

@dp.message()
async def ai_chat(message: types.Message):

    user_id = message.from_user.id

    current_time = time.time()

    # =========================
    # COOLDOWN
    # =========================

    if user_id in user_cooldowns:

        last_time = user_cooldowns[user_id]

        if current_time - last_time < COOLDOWN:

            wait_time = int(COOLDOWN - (current_time - last_time))

            await message.answer(
                f"⏳ Подождите {wait_time} секунд перед следующим запросом."
            )

            return

    user_cooldowns[user_id] = current_time

    # =========================
    # DAILY LIMIT
    # =========================

    today = time.strftime("%Y-%m-%d")

    if user_id not in daily_limits:

        daily_limits[user_id] = {
            "date": today,
            "count": 0
        }

    if daily_limits[user_id]["date"] != today:

        daily_limits[user_id] = {
            "date": today,
            "count": 0
        }

    if daily_limits[user_id]["count"] >= MAX_DAILY_REQUESTS:

        await message.answer(
            "❌ Вы исчерпали лимит 10 запросов на сегодня."
        )

        return

    daily_limits[user_id]["count"] += 1

    # =========================
    # USER MESSAGE
    # =========================

    user_question = message.text

    wait_msg = await message.answer("🤖 AI думает...")

    try:

        system_prompt = f"""
Ты — эксперт по Anime Characters Fight Wiki (ACF).

Ты ОБЯЗАН отвечать ТОЛЬКО используя информацию из базы знаний ниже.

Если информации нет в базе знаний — так и скажи.

Никогда не придумывай информацию.

База знаний:
{ACF_KNOWLEDGE}
"""

        response = client.chat(
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

        answer = response.message.content[0].text

        if not answer:
            answer = "AI не смог дать ответ."

        if len(answer) > 4000:
            answer = answer[:4000]

        await wait_msg.edit_text(answer)

    except Exception as e:

        print(f"Ошибка AI: {e}")

        await wait_msg.edit_text(
            f"❌ Ошибка AI: {e}"
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
