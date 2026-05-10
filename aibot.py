import asyncio
import logging
import os
import time
import re
from difflib import SequenceMatcher

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_AI")

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
# LOAD KNOWLEDGE FILE
# =========================

try:

    with open("ACF файловое.txt", "r", encoding="utf-8") as f:
        ACF_KNOWLEDGE = f.read()

    print(">>> БАЗА ЗНАНИЙ ЗАГРУЖЕНА <<<")

except Exception as e:

    print(f"Ошибка загрузки файла: {e}")

    ACF_KNOWLEDGE = ""

# =========================
# SPLIT TEXT
# =========================

chunks = []

raw_chunks = ACF_KNOWLEDGE.split("\n\n")

for chunk in raw_chunks:

    chunk = chunk.strip()

    if len(chunk) > 30:
        chunks.append(chunk)

print(f">>> ЗАГРУЖЕНО ЧАНКОВ: {len(chunks)} <<<")

# =========================
# USER LIMITS
# =========================

user_cooldowns = {}

daily_limits = {}

# =========================
# SIMPLE WORD REPLACEMENTS
# =========================

simple_words = {
    "трансцендентный": "стоящий выше всего",
    "концептуальный": "связанный с идеями",
    "измерение": "уровень пространства",
    "иерархия": "система уровней",
    "метафизический": "существующий вне обычного мира",
    "бесконечность": "без конца",
    "пространство-время": "мир и время",
    "гиперверсальный": "намного выше мультивселенных",
    "аутер": "существующий вне измерений",
    "димензиональность": "уровень измерений"
}

# =========================
# START
# =========================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):

    await message.answer(
        "Привет я Anime Characters Fight AI 🌐\n\n"
        "Я отвечаю используя базу знаний ACF файловое.txt.\n"
        "Ты можешь спрашивать про tier'ы, scaling, cosmology и другое."
    )

# =========================
# SEARCH FUNCTION
# =========================

def similarity(a, b):

    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_best_chunk(query):

    best_score = 0
    best_chunk = None

    for chunk in chunks:

        score = similarity(query, chunk)

        if query.lower() in chunk.lower():
            score += 1

        if score > best_score:
            best_score = score
            best_chunk = chunk

    return best_chunk

# =========================
# SIMPLE EXPLAINER
# =========================

def simplify_text(text):

    simplified = text

    for hard_word, easy_word in simple_words.items():

        simplified = re.sub(
            hard_word,
            easy_word,
            simplified,
            flags=re.IGNORECASE
        )

    return (
        "📘 Простыми словами:\n\n"
        + simplified
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
                f"⏳ Подождите {wait_time} секунд."
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
            "❌ Вы исчерпали лимит запросов на сегодня."
        )

        return

    daily_limits[user_id]["count"] += 1

    # =========================
    # QUESTION
    # =========================

    query = message.text.strip()

    wait_msg = await message.answer("🔍 Ищу информацию...")

    # =========================
    # FIND BEST ANSWER
    # =========================

    best_chunk = find_best_chunk(query)

    if not best_chunk:

        await wait_msg.edit_text(
            "❌ Я не нашёл информацию в базе знаний."
        )

        return

    # =========================
    # SIMPLE MODE
    # =========================

    simple_keywords = [
        "простыми словами",
        "объясни легко",
        "объясни просто",
        "легко объясни",
        "как учитель"
    ]

    if any(word in query.lower() for word in simple_keywords):

        answer = simplify_text(best_chunk)

    else:

        answer = (
            "📚 Информация из базы знаний:\n\n"
            + best_chunk
        )

    if len(answer) > 4000:
        answer = answer[:4000]

    await wait_msg.edit_text(answer)

# =========================
# MAIN
# =========================

async def main():

    print(">>> ACF AI ЗАПУЩЕН <<<")

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
