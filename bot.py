import asyncio
import logging
import time
import os
import random
import google.generativeai as genai

with open("ACF файловое.md", "r", encoding="utf-8") as f:
    ACF_KNOWLEDGE = f.read()

from aiogram import Bot, Dispatcher, types, F, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from aiogram.enums import PollType
from aiogram.exceptions import TelegramBadRequest

TOKEN = "7967554585:AAGWNP1kF9u2Tbs0-JbpHPGkmYmdCHIiCn0"

CHANNEL_ID = -1003822775225
MOD_CHAT_ID = -1003987317286
RULES_LINK = "https://t.me/RulesOfSpaceRealm"
COMMENTS_CHAT_ID = -1003777022478

PUBLISH_INTERVAL = 180

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

gemini_model = genai.GenerativeModel("gemini-2.5-flash")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

pending_posts = {}
publish_queue = []
last_publish_time = 0

moderator_stats = {}

class RegForm(StatesGroup):
    waiting_name = State()
    waiting_universe = State()
    waiting_players = State()
    waiting_conditions = State()
    waiting_photo = State()
    waiting_photo2 = State()
    waiting_acf_question = State()

user_acf_chats = {}

def get_main_kb():
    buttons = [
        [InlineKeyboardButton(text="📝 Мнение ", callback_data="reg_opinion")],
        [InlineKeyboardButton(text="⚔️ ПБ ⚔️", callback_data="reg_pb")],
        [InlineKeyboardButton(text="ACF Онлайн 🔥", callback_data="acf_online")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_kb():
    buttons = [
        [InlineKeyboardButton(text="На модерацию ✅", callback_data="confirm_send")],
        [InlineKeyboardButton(text="Отмена ❌", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def publication_worker():
    global last_publish_time

    while True:
        current_time = time.time()

        if publish_queue and (current_time - last_publish_time >= PUBLISH_INTERVAL):

            data = publish_queue.pop(0)

            try:
                sent_msg = None

                if data['reg_type'] == 'reg_opinion':

                    if data['type1'] == 'photo':
                        sent_msg = await bot.send_photo(
                            CHANNEL_ID,
                            data['photo1'],
                            caption=data['final_caption'],
                            parse_mode="HTML"
                        )
                    else:
                        sent_msg = await bot.send_video(
                            CHANNEL_ID,
                            data['photo1'],
                            caption=data['final_caption'],
                            parse_mode="HTML"
                        )

                else:

                    m1 = InputMediaPhoto(
                        media=data['photo1'],
                        caption=data['final_caption'],
                        parse_mode="HTML"
                    ) if data['type1'] == 'photo' else InputMediaVideo(
                        media=data['photo1'],
                        caption=data['final_caption'],
                        parse_mode="HTML"
                    )

                    m2 = InputMediaPhoto(
                        media=data['photo2']
                    ) if data['type2'] == 'photo' else InputMediaVideo(
                        media=data['photo2']
                    )

                    media_group = await bot.send_media_group(
                        CHANNEL_ID,
                        media=[m1, m2]
                    )

                    sent_msg = media_group[0]

                last_publish_time = time.time()

                logging.info("Пост успешно опубликован.")

                if data['reg_type'] == 'reg_pb' and sent_msg:

                    message_id = sent_msg.message_id

                    players_raw = data.get('players', '').split('\n')
                    names_raw = data.get('name', '').split('\n')
                    conditions = data.get('conditions', 'Нет условий')

                    clean_players = [p.strip() for p in players_raw if p.strip()]
                    clean_names = [n.strip() for n in names_raw if n.strip()]

                    walker_idx = random.randint(0, len(clean_players) - 1) if clean_players else 0
                    walker_user = clean_players[walker_idx] if clean_players else "@unknown"

                    poll_options = []

                    for name in clean_names:
                        if name:
                            poll_options.append(name)

                    if not poll_options:
                        poll_options = ["Player 1", "Player 2"]

                    try:
                        await bot.send_poll(
                            chat_id=CHANNEL_ID,
                            question="Кто победит?",
                            options=poll_options,
                            is_anonymous=True,
                            type=PollType.REGULAR,
                            reply_to_message_id=message_id
                        )

                    except Exception as e:
                        logging.error(f"Ошибка создания опроса: {e}")

                    channel_id_clean = str(CHANNEL_ID)[4:]
                    post_link = f"https://t.me/c/{channel_id_clean}/{message_id}"

                    comment_text = (
                        f" <a href='{post_link}'>Пост ПБ</a>\n\n"
                        f"<b>Бот определил, ходит — {walker_user}. Удачи в пруфбаттле! 🔥</b>\n\n"
                        f"<b>Условие пруфбаттла: {conditions}</b>"
                    )

                    kb_comment = InlineKeyboardMarkup(
                        inline_keyboard=[[
                            InlineKeyboardButton(
                                text="👉 Перейти к посту",
                                url=post_link
                            )
                        ]]
                    )

                    try:
                        await bot.send_message(
                            chat_id=COMMENTS_CHAT_ID,
                            text=comment_text,
                            parse_mode="HTML",
                            reply_markup=kb_comment,
                            disable_web_page_preview=False
                        )

                    except Exception as e:
                        logging.error(f"Ошибка отправки комментария: {e}")

            except Exception as e:
                logging.error(f"Ошибка публикации: {e}")

        await asyncio.sleep(10)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "Салам, статюганище! Выбери тип регистрации:",
        reply_markup=get_main_kb()
    )

@dp.message(Command("reyt"))
async def show_rating(message: types.Message):

    if not moderator_stats:
        await message.answer("Пока нет статистики.")
        return

    sorted_stats = sorted(
        moderator_stats.items(),
        key=lambda x: x[1],
        reverse=True
    )

    text = "<b>Рейтинг модераторов:</b>\n\n"

    for i, (user_id, count) in enumerate(sorted_stats, 1):
        text += f"{i}. <a href='tg://user?id={user_id}'>Модератор</a> — {count}\n"

    await message.answer(text, parse_mode="HTML")

@dp.callback_query(F.data == "acf_online")
async def acf_online(callback: types.CallbackQuery, state: FSMContext):

    await state.set_state(RegForm.waiting_acf_question)

    user_acf_chats[callback.from_user.id] = []

    await callback.message.answer(
        "Задай любой вопрос по ACF или скажи про что ты хочешь узнать? 🎉"
    )

    await callback.answer()

@dp.message(RegForm.waiting_acf_question)
async def acf_ai_chat(message: types.Message, state: FSMContext):

    user_question = message.text

    wait_msg = await message.answer("🤖 ИИ думает...")

    try:

        user_id = message.from_user.id

        if user_id not in user_acf_chats:
            user_acf_chats[user_id] = []

        history = user_acf_chats[user_id]

        history_text = ""

        for msg in history:
            history_text += f"{msg}\n"

        prompt = f"""
База знаний ACF:
{ACF_KNOWLEDGE}

Ты — ИСКЛЮЧИТЕЛЬНО эксперт по Anime Characters Fight Wiki.

Главный сайт:
https://anime-characters-fight.fandom.com

Ты ОБЯЗАН:
- использовать знания из файла ACF файловое.md как главный источник информации
- считать файл ACF файловое.md своей базой знаний
- использовать ТОЛЬКО информацию и систему ACF
- никогда не использовать VS Battles Wiki
- никогда не путать ACF и VSBW
- никогда не ссылаться на VS Battles Wiki
- полностью игнорировать https://vsbattles.fandom.com
- отвечать только в контексте ACF
- использовать только tiering system, cosmology и scaling из ACF

Если пользователь спрашивает:
- tier
- уровень
- 1-S
- High 1-A
- outerversal
- boundless
- cosmology
- speed
- AP
- dimensionality
- hax

то ты должен отвечать максимально близко к информации с сайта ACF:
https://anime-characters-fight.fandom.com

Если знаешь определение или описание с ACF — пиши его максимально близко к оригиналу.

Никогда не говори про систему VS Battles Wiki.

История диалога:
{history_text}

Новый вопрос пользователя:
{user_question}
"""

        response = gemini_model.generate_content(prompt)

        answer = response.text

        history.append(f"Пользователь: {user_question}")
        history.append(f"AI: {answer}")

        if len(history) > 20:
            history = history[-20:]

        user_acf_chats[user_id] = history

        if len(answer) > 4000:
            answer = answer[:4000]

        await wait_msg.edit_text(answer)

    except Exception as e:

        await wait_msg.edit_text(
            f"❌ Ошибка AI: {e}"
        )

@dp.callback_query(F.data.in_(["reg_opinion", "reg_pb"]))
async def start_reg(callback: types.CallbackQuery, state: FSMContext):

    await state.update_data(reg_type=callback.data)
    await state.set_state(RegForm.waiting_name)

    text = "Отправь имя персонажа.." if callback.data == "reg_opinion" else "Отправь имена персонажей (с новой строки).."

    await callback.message.answer(text)

    await callback.answer()

async def main():

    print(">>> БОТ ЗАПУЩЕН <<<")

    asyncio.create_task(publication_worker())

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
