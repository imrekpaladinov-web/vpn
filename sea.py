import asyncio
import random
import time
import os

from telethon import TelegramClient
from telethon.tl.functions.account import CheckUsernameRequest
from telethon.errors import SessionPasswordNeededError

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# --- КОНФИГУРАЦИЯ ЧЕРЕЗ ПЕРЕМЕННЫЕ ОС ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN1")
ADMIN_ID = int(os.environ.get("ADMIN_ID"))

client = TelegramClient('session_ghost', API_ID, API_HASH)

user_settings = {}
user_stats = {}
used_usernames = set()


class SmartGenerator:
    V = "aeiouy"
    C = "bcdfghjklmnpqrstvwxz"
    D = "0123456789"

    @classmethod
    def generate_exact(cls, length, use_digits=False):
        # Генерируем основу
        chars = [random.choice(cls.C if i % 2 == 0 else cls.V) for i in range(length)]

        # Если нужны цифры, вставляем одну цифру в случайную позицию, кроме индекса 0
        if use_digits:
            pos = random.randint(1, length - 1)
            chars[pos] = random.choice(cls.D)

        return "".join(chars)

    @classmethod
    def generate_beauty_fast(cls):
        # Генерация коротких ников типа "слово_hub" - без жестких списков для скорости
        word = "".join(random.choice(cls.C + cls.V) for _ in range(4))
        suffix = random.choice(['hub', 'top', 'pro', 'web', 'link', 'zone'])
        return f"{word}_{suffix}"


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text="5 БУКВ 🔥")
    builder.button(text="6 БУКВ 🌐")
    builder.button(text="Красивый юзернейм 🗒️")
    builder.button(text="Фильтры 🦉")
    builder.adjust(2, 1, 1)
    return builder.as_markup(resize_keyboard=True)


@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    user_settings[m.from_user.id] = {"digits": False}
    await m.answer(
        "<b>⚔️ Приветствуем в Ghost Link Search!\n\nВыберите действие в меню ниже 👻</b>",
        reply_markup=get_main_menu()
    )


@dp.message(F.text == "Фильтры 🦉")
async def cmd_filters(m: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="С цифрами 🔢", callback_data="set_digits_on")
    kb.button(text="Без цифр 🔤", callback_data="set_digits_off")
    kb.adjust(2)

    current = (
        "С цифрами"
        if user_settings.get(m.from_user.id, {}).get("digits")
        else "Без цифр"
    )

    await m.answer(
        f"<b>🗒️ Настройка фильтров\n\nВыберите режим поиска:\n• Текущий: {current}\n\n👻</b>",
        reply_markup=kb.as_markup()
    )


@dp.callback_query(F.data.startswith("set_digits_"))
async def handle_filter_change(c: types.CallbackQuery):
    mode = c.data == "set_digits_on"
    user_settings[c.from_user.id] = {"digits": mode}

    await c.answer("Настройки обновлены")

    await c.message.edit_text(
        f"<b>✅ Настройки обновлены: {'С цифрами 🔢' if mode else 'Без цифр 🔤'}</b>"
    )


async def perform_search(m: types.Message, mode: str):
    user_id = m.from_user.id

    if user_id != ADMIN_ID:
        stats = user_stats.setdefault(user_id, {"count": 0, "reset_time": 0})

        if time.time() > stats["reset_time"] and stats["reset_time"] != 0:
            stats = {"count": 0, "reset_time": 0}
            user_stats[user_id] = stats

        if stats["count"] >= 10:
            await m.answer("<b>❌ Лимит исчерпан. Попробуйте через 1.5 часа.</b>")
            return

    status = await m.answer("<b>🔍 Поиск...</b>")
    start_time = time.time()

    digits = user_settings.get(user_id, {}).get("digits", False)

    found = None

    for _ in range(150):

        if mode == "5":
            name = SmartGenerator.generate_exact(5, digits)

        elif mode == "6":
            name = SmartGenerator.generate_exact(6, digits)

        else:
            name = SmartGenerator.generate_beauty_fast()

        if name not in used_usernames:

            try:
                if await client(CheckUsernameRequest(name)):
                    found = name
                    used_usernames.add(found)
                    break

            except:
                continue

    if found:

        if user_id != ADMIN_ID:
            stats["count"] += 1

            if stats["count"] == 10:
                stats["reset_time"] = time.time() + 5400

        await status.edit_text(
            f"<b>✅ РЕЗУЛЬТАТ: @{found}\n⚡️ Время: {round(time.time() - start_time, 2)} сек.</b>"
        )

    else:
        await status.edit_text("<b>❌ Ничего не найдено, попробуй еще раз!</b>")


@dp.message(F.text.in_(["5 БУКВ 🔥", "6 БУКВ 🌐", "Красивый юзернейм 🗒️"]))
async def handle_menu_buttons(m: types.Message):

    if "5 БУКВ" in m.text:
        await perform_search(m, "5")

    elif "6 БУКВ" in m.text:
        await perform_search(m, "6")

    else:
        await perform_search(m, "beauty")


async def main():

    await client.connect()

    if not await client.is_user_authorized():

        phone = input("Введите номер телефона: ")

        await client.send_code_request(phone)

        try:
            await client.sign_in(phone, input("Код: "))

        except SessionPasswordNeededError:
            await client.sign_in(password=input("Пароль (2FA): "))

    print("--- БОТ ГОТОВ ---")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
