import asyncio
import os
import logging
import torch
import numpy as np
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# =========================
# CONFIG
# =========================
BOT_TOKEN = os.getenv("BOT_AI")
# Модель для логики (умная и легкая)
LLM_MODEL = "MBZUAI/LaMini-Flan-T5-248M" 
# Модель для поиска по файлу
EMBED_MODEL = "all-MiniLM-L6-v2"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =========================
# ЗАГРУЗКА ИИ (ЭТО ЗАЙМЕТ ВРЕМЯ ПРИ ЗАПУСКЕ)
# =========================
print(">>> ЗАГРУЗКА МОДЕЛЕЙ...")
search_model = SentenceTransformer(EMBED_MODEL)

# Загружаем генератор текста
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL)
model_llm = AutoModelForSeq2SeqLM.from_pretrained(LLM_MODEL)
generator = pipeline("text2text-generation", model=model_llm, tokenizer=tokenizer)
print(">>> ИИ ГОТОВ К БОЮ <<<")

# =========================
# РАБОТА С БАЗОЙ ЗНАНИЙ
# =========================
try:
    with open("ACF файловое.txt", "r", encoding="utf-8") as f:
        content = f.read()
    chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 30]
    chunk_embeddings = search_model.encode(chunks, convert_to_tensor=True)
    print(f">>> БАЗА ЗАГРУЖЕНА: {len(chunks)} ЧАНКОВ")
except Exception as e:
    print(f"Ошибка базы: {e}")
    chunks = []

# =========================
# ЛОГИКА УМНОГО ОТВЕТА
# =========================
def get_best_context(query):
    query_enc = search_model.encode(query, convert_to_tensor=True)
    # Считаем сходство через torch (вместо scikit-learn)
    cos_scores = torch.nn.functional.cosine_similarity(query_enc, chunk_embeddings)
    top_results = torch.topk(cos_scores, k=min(3, len(chunks)))
    indices = top_results.indices.tolist()
    return "\n\n".join([chunks[i] for i in indices])

async def generate_smart_answer(query):
    context = get_best_context(query)
    
    # Инструкция для ИИ (Промпт)
    # Мы просим его отвечать на русском и быть экспертом
    prompt = f"Use the following ACF context to answer the question in Russian. Be expert and conversational.\nContext: {context}\nQuestion: {query}\nAnswer:"
    
    loop = asyncio.get_event_loop()
    # Запускаем тяжелую генерацию в отдельном потоке, чтобы бот не зависал
    result = await loop.run_in_executor(None, lambda: generator(prompt, max_length=512, do_sample=True, temperature=0.7))
    return result[0]['generated_text']

# =========================
# ХЕНДЛЕРЫ
# =========================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я твоя персональная нейросеть по ACF. Спрашивай что угодно, я не просто копирую базу, я её понимаю!")

@dp.message()
async def ai_chat(message: types.Message):
    wait_msg = await message.answer("🧠 Думаю...")
    try:
        answer = await generate_smart_answer(message.text)
        await wait_msg.edit_text(answer)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await wait_msg.edit_text("Ой, что-то в моих нейронных связях замкнуло...")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
