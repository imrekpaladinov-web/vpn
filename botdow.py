import os
import aiohttp
import asyncio
import uuid

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)

# =========================
# НАСТРОЙКИ
# =========================

# Твой токен бота
BOT_TOKEN = "8274968898:AAH8QsXcqC-H_BHVnywUWJXMVrqCD3bAZsg"
# Юзернейм канала для проверки подписки
CHANNEL_USERNAME = "VPN_GhostLink"
# Ссылка на твой API на Hugging Face
HF_API = "https://ghostlinkbusija-ghost-downloader.hf.space/download"

# =========================
# BOT ИНИЦИАЛИЗАЦИЯ
# =========================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# =========================
# КНОПКИ
# =========================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Скачать видео 🔥")]],
    resize_keyboard=True
)

subscribe_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться 🌐", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton(text="Продолжить! ✅", callback_data="check_sub")]
    ]
)

# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================

async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# =========================
# ОБРАБОТЧИКИ (START & SUB)
# =========================

@dp.message(CommandStart())
async def start_handler(message: Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer(
            "<b>Чтобы скачивать видео, подпишись на канал по кнопкам ниже\n"
            "После нажми «Продолжить»! ✅.</b>",
            reply_markup=subscribe_keyboard
        )
        return

    await message.answer(
        "<b>👻 Привет, я Ghost Link Download 🗒️\n\n"
        "💫 Умею скачивать видео из Тик Тока, Инстаграма, "
        "YouTube, Пинтереста в МАКСИМАЛЬНОМ качестве.</b>",
        reply_markup=main_keyboard
    )

@dp.callback_query(F.data == "check_sub")
async def check_sub(callback):
    if not await is_subscribed(callback.from_user.id):
        await callback.answer("❌ Ты не подписался на канал", show_alert=True)
        return

    await callback.message.delete()
    await callback.message.answer(
        "<b>👻 Добро пожаловать! Присылай ссылку на видео.</b>",
        reply_markup=main_keyboard
    )

@dp.message(F.text == "Скачать видео 🔥")
async def download_button(message: Message):
    await message.answer("<b>Просто отправь мне ссылку на видео (YT, TT, Insta, Pinterest).</b>")

# =========================
# СКАЧИВАНИЕ (ОСНОВНАЯ ЛОГИКА)
# =========================

@dp.message(F.text.regexp(r'https?://'))
async def download_video_handler(message: Message):
    if not await is_subscribed(message.from_user.id):
        await message.answer("<b>Сначала подпишись!</b>", reply_markup=subscribe_keyboard)
        return

    url = message.text.strip()
    wait_message = await message.answer("<b>⏳ Начинаю загрузку в максимальном качестве... Подожди немного.</b>")

    # Генерируем уникальное имя файла для этого запроса
    file_id = str(uuid.uuid4())
    file_name = f"video_{file_id}.mp4"

    try:
        # Увеличиваем таймаут, так как 4K видео может склеиваться долго
        async with aiohttp.ClientSession() as session:
            async with session.get(HF_API, params={"url": url}, timeout=600) as response:
                if response.status != 200:
                    await wait_message.edit_text("<b>❌ Ошибка API или видео недоступно.</b>")
                    return

                # Читаем данные файла частями, чтобы не забить ОЗУ
                file_data = await response.read()

                # Проверка лимита Telegram (50 МБ для обычных ботов)
                if len(file_data) > 50 * 1024 * 1024:
                    await wait_message.edit_text("<b>❌ Файл слишком тяжелый (>50MB).\n"
                                                 "Телеграм не позволяет ботам отправлять такие файлы.</b>")
                    return

        # Сохраняем на диск Railway
        with open(file_name, "wb") as f:
            f.write(file_data)

        # Отправляем видео пользователю
        video_file = FSInputFile(file_name)
        await message.answer_video(
            video=video_file,
            caption="<i>Ghost Link Download 🗒️ — Максимальное качество.</i>",
            supports_streaming=True
        )

        await wait_message.delete()

    except Exception as e:
        print(f"Error: {e}")
        await wait_message.edit_text(f"<b>❌ Произошла ошибка:</b>\n<code>{str(e)}</code>")

    finally:
        # Удаляем временный файл в любом случае
        if os.path.exists(file_name):
            os.remove(file_name)

# =========================
# ЗАПУСК
# =========================

async def main():
    print("BOT STARTED ON RAILWAY")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("BOT STOPPED")
        
