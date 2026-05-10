import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from ctransformers import AutoModelForCausalLM

# Настройки
BOT_TOKEN = os.getenv("BOT_AI")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Загружаем ОЧЕНЬ сжатую, но умную модель
# Она скачается сама, весит около 1.2 ГБ, но в RAM занимает мало
print(">>> ЗАГРУЗКА ИНТЕЛЛЕКТА (GGUF)...")
llm = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Phi-3-mini-4k-instruct-GGUF",
    model_file="phi-3-mini-4k-instruct.Q4_K_M.gguf",
    model_type="phi3"
)
print(">>> НЕЙРОСЕТЬ ACF ГОТОВА <<<")

# Загружаем базу данных
with open("ACF файловое.txt", "r", encoding="utf-8") as f:
    ACF_KNOWLEDGE = f.read()[:1500] # Берем самый важный кусок для контекста

async def get_ai_response(user_query):
    # Промпт, который заставляет бота быть экспертом и говорить по-русски
    prompt = f"<|system|>\nТы эксперт по системе ACF Wiki. Отвечай своими словами, используя знания: {ACF_KNOWLEDGE}<|end|>\n<|user|>\n{user_query}<|end|>\n<|assistant|>\n"
    
    # Генерация (запускаем в потоке, чтобы бот не «висел»)
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, lambda: llm(prompt, max_new_tokens=512, temperature=0.7))
    return response

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я — ИИ-эксперт по ACF. Я не просто копирую базу, я понимаю иерархию уровней. Спрашивай!")

@dp.message()
async def chat(message: types.Message):
    wait = await message.answer("🧠 Анализирую уровни реальности...")
    try:
        reply = await get_ai_response(message.text)
        await wait.edit_text(reply)
    except Exception as e:
        await wait.edit_text(f"Ошибка в нейросетях: {e}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
 
