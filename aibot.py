import asyncio
import logging
import os
import re

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

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
# SPLIT INTO CHUNKS
# =========================

chunks = []

raw_chunks = ACF_KNOWLEDGE.split("\n\n")

for chunk in raw_chunks:

    chunk = chunk.strip()

    if len(chunk) > 40:
        chunks.append(chunk)

print(f">>> ЗАГРУЖЕНО ЧАНКОВ: {len(chunks)} <<<")

# =========================
# LOAD AI MODEL
# =========================

print(">>> ЗАГРУЖАЕТСЯ SEMANTIC AI МОДЕЛЬ <<<")

model = SentenceTransformer("all-MiniLM-L6-v2")

print(">>> МОДЕЛЬ ЗАГРУЖЕНА <<<")

# =========================
# CREATE EMBEDDINGS
# =========================

print(">>> СОЗДАЮТСЯ EMBEDDINGS <<<")

chunk_embeddings = model.encode(chunks)

print(">>> EMBEDDINGS ГОТОВЫ <<<")

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
# FIND BEST CHUNK
# =========================

def find_best_chunks(query, top_k=3):

    query_embedding = model.encode([query])

    similarities = cosine_similarity(
        query_embedding,
        chunk_embeddings
    )[0]

    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = []

    for idx in top_indices:

        results.append(chunks[idx])

    return results

# =========================
# SIMPLIFY TEXT
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

    return simplified

# =========================
# FORMAT RESPONSE
# =========================

def generate_answer(query, found_chunks):

    combined_text = "\n\n".join(found_chunks)

    query_lower = query.lower()

    # =========================
    # SIMPLE EXPLAIN MODE
    # =========================

    if (
        "простыми словами" in query_lower
        or "объясни" in query_lower
        or "легко" in query_lower
        or "как учитель" in query_lower
    ):

        simplified = simplify_text(combined_text)

        return (
            "📘 Объяснение:\n\n"
            + simplified
        )

    # =========================
    # WHAT IS MODE
    # =========================

    if (
        "что такое" in query_lower
        or "что значит" in query_lower
        or "что означает" in query_lower
    ):

        return (
            "📚 Определение:\n\n"
            + combined_text
        )

    # =========================
    # DEFAULT
    # =========================

    return (
        "📚 Информация из базы знаний:\n\n"
        + combined_text
    )

# =========================
# START
# =========================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):

    await message.answer(
        "🌐 Привет! Я Anime Characters Fight AI.\n\n"
        "Я отвечаю используя базу знаний ACF.\n"
        "Ты можешь спрашивать:\n"
        "- Что такое 1-A\n"
        "- Объясни outerversal\n"
        "- Кто сильнее\n"
        "- Объясни простыми словами\n"
        "- Как работает tiering"
    )

# =========================
# CHAT
# =========================

@dp.message()
async def ai_chat(message: types.Message):

    query = message.text.strip()

    wait_msg = await message.answer(
        "🧠 Анализирую информацию..."
    )

    try:

        best_chunks = find_best_chunks(query)

        answer = generate_answer(
            query,
            best_chunks
        )

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

    await bot.delete_webhook(
        drop_pending_updates=True
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
