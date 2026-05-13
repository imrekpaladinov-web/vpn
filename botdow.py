import os
import aiohttp
import asyncio

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

BOT_TOKEN = "8274968898:AAH8QsXcqC-H_BHVnywUWJXMVrqCD3bAZsg"

CHANNEL_USERNAME = "VPN_GhostLink"

HF_API = "https://ghostlinkbusija-ghost-downloader.hf.space/download"

# =========================
# BOT
# =========================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()

# =========================
# КНОПКИ
# =========================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Скачать видео 🔥")]
    ],
    resize_keyboard=True
)

subscribe_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Подписаться 🌐",
                url=f"https://t.me/{CHANNEL_USERNAME}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Продолжить! ✅",
                callback_data="check_sub"
            )
        ]
    ]
)

# =========================
# ПРОВЕРКА ПОДПИСКИ
# =========================

async def is_subscribed(user_id):

    try:

        member = await bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME}",
            user_id=user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False

# =========================
# START
# =========================

@dp.message(CommandStart())
async def start_handler(message: Message):

    subscribed = await is_subscribed(message.from_user.id)

    if not subscribed:

        await message.answer(
            "<b>Чтобы скачивать видео, подпишись на канал по кнопкам ниже\n"
            "После нажми «Продолжить»! ✅.</b>",
            reply_markup=subscribe_keyboard
        )

        return

    await message.answer(
        "<b>👻 Привет, я Ghost Link Download 🗒️\n\n"
        "💫 Умею скачивать видео из Тик Тока, Инстаграма, "
        "YouTube, Пинтереста без водяного знака.</b>",
        reply_markup=main_keyboard
    )

# =========================
# ПРОДОЛЖИТЬ
# =========================

@dp.callback_query(F.data == "check_sub")
async def check_sub(callback):

    subscribed = await is_subscribed(callback.from_user.id)

    if not subscribed:

        await callback.answer(
            "❌ Ты не подписался на канал",
            show_alert=True
        )

        return

    await callback.message.delete()

    await callback.message.answer(
        "<b>👻 Привет, я Ghost Link Download 🗒️\n\n"
        "💫 Умею скачивать видео из Тик Тока, Инстаграма, "
        "YouTube, Пинтереста без водяного знака.</b>",
        reply_markup=main_keyboard
    )

    await callback.answer()

# =========================
# КНОПКА СКАЧАТЬ
# =========================

@dp.message(F.text == "Скачать видео 🔥")
async def download_button(message: Message):

    await message.answer(
        "<b>Скопируй ссылку видео и отправь ее в наш чат.\n\n"
        "Я скачаю видео и скину тебе его. "
        "Видео скачается в максимальном качестве. 🎉</b>"
    )

# =========================
# СКАЧИВАНИЕ
# =========================

@dp.message(F.text.regexp(r'https?://'))
async def download_video(message: Message):

    subscribed = await is_subscribed(message.from_user.id)

    if not subscribed:

        await message.answer(
            "<b>Чтобы скачивать видео, подпишись на канал по кнопкам ниже\n"
            "После нажми «Продолжить»! ✅.</b>",
            reply_markup=subscribe_keyboard
        )

        return

    url = message.text.strip()

    wait_message = await message.answer(
        "<b>Подожди пожалуйста, бот скачивает видео. ⭐</b>"
    )

    try:

        async with aiohttp.ClientSession() as session:

            async with session.get(
                HF_API,
                params={"url": url},
                timeout=300
            ) as response:

                if response.status != 200:

                    await wait_message.edit_text(
                        "<b>❌ Ошибка API Hugging Face.</b>"
                    )

                    return

                file_data = await response.read()

        file_name = "video.mp4"

        with open(file_name, "wb") as f:
            f.write(file_data)

        video = FSInputFile(file_name)

        await message.answer_video(
            video=video,
            caption="<i>Скачано с помощью Ghost Link Download 🗒️.</i>",
            supports_streaming=True
        )

        os.remove(file_name)

        await wait_message.delete()

    except Exception as e:

        print(e)

        await wait_message.edit_text(
            f"<b>❌ Ошибка:\n{e}</b>"
        )

# =========================
# START POLLING
# =========================

async def main():

    print("BOT STARTED")

    while True:

        try:

            await dp.start_polling(bot)

        except Exception as e:

            print(f"ERROR: {e}")

            await asyncio.sleep(5)

# =========================

if __name__ == "__main__":

    asyncio.run(main())
