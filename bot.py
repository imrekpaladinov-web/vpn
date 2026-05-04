import asyncio
import logging
import time
import os

from aiogram import Bot, Dispatcher, types, F, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from aiogram.exceptions import TelegramBadRequest


# 🔐 Токен теперь через переменные (ВАЖНО для Railway)
TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_ID = -1003822775225      
MOD_CHAT_ID = -1003987317286     
RULES_LINK = "https://t.me/RulesOfSpaceRealm"

PUBLISH_INTERVAL = 180 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

pending_posts = {}
publish_queue = [] 
last_publish_time = 0 


class RegForm(StatesGroup):
    waiting_name = State()
    waiting_universe = State()
    waiting_players = State()
    waiting_conditions = State()
    waiting_photo = State()
    waiting_photo2 = State()


def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Мнение 📝", callback_data="reg_opinion")],
        [InlineKeyboardButton(text="⚔️ ПБ ⚔️", callback_data="reg_pb")]
    ])


def get_confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="На модерацию ✅", callback_data="confirm_send")],
        [InlineKeyboardButton(text="Отмена ❌", callback_data="cancel")]
    ])


async def publication_worker():
    global last_publish_time
    while True:
        current_time = time.time()
        if publish_queue and (current_time - last_publish_time >= PUBLISH_INTERVAL):
            data = publish_queue.pop(0)
            try:
                if data['reg_type'] == 'reg_opinion':
                    if data['type1'] == 'photo':
                        await bot.send_photo(CHANNEL_ID, data['photo1'], caption=data['final_caption'], parse_mode="HTML")
                    else:
                        await bot.send_video(CHANNEL_ID, data['photo1'], caption=data['final_caption'], parse_mode="HTML")
                else:
                    m1 = InputMediaPhoto(media=data['photo1'], caption=data['final_caption'], parse_mode="HTML") if data['type1'] == 'photo' else InputMediaVideo(media=data['photo1'], caption=data['final_caption'], parse_mode="HTML")
                    m2 = InputMediaPhoto(media=data['photo2']) if data['type2'] == 'photo' else InputMediaVideo(media=data['photo2'])
                    await bot.send_media_group(CHANNEL_ID, media=[m1, m2])
                
                last_publish_time = time.time()
                logging.info("Пост опубликован")
            except Exception as e:
                logging.error(f"Ошибка публикации: {e}")
        await asyncio.sleep(10)


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Салам, статюганище! Выбери тип регистрации:", reply_markup=get_main_kb())


@dp.callback_query(F.data.in_(["reg_opinion", "reg_pb"]))
async def start_reg(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(reg_type=callback.data)
    await state.set_state(RegForm.waiting_name)

    text = "Отправь имя персонажа.." if callback.data == "reg_opinion" else "Отправь имена персонажей (с новой строки).."
    await callback.message.answer(text)
    await callback.answer()


@dp.message(RegForm.waiting_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegForm.waiting_universe)
    await message.answer("Отправь вселенные..")


@dp.message(RegForm.waiting_universe)
async def process_universe(message: types.Message, state: FSMContext):
    await state.update_data(universe=message.text)
    data = await state.get_data()

    if data['reg_type'] == 'reg_pb':
        await state.set_state(RegForm.waiting_players)
        await message.answer("Юзернеймы игроков..")
    else:
        await state.set_state(RegForm.waiting_conditions)
        await message.answer("Условия или 'нет'")


@dp.message(RegForm.waiting_players)
async def process_players(message: types.Message, state: FSMContext):
    await state.update_data(players=message.text)
    await state.set_state(RegForm.waiting_conditions)
    await message.answer("Условия или 'нет'")


@dp.message(RegForm.waiting_conditions)
async def process_cond(message: types.Message, state: FSMContext):
    await state.update_data(conditions=message.text)
    await state.set_state(RegForm.waiting_photo)
    await message.answer("Отправь арт/видео")


@dp.message(RegForm.waiting_photo, F.photo | F.video)
async def process_photo1(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    await state.update_data(photo1=file_id, type1='photo' if message.photo else 'video')

    data = await state.get_data()
    if data['reg_type'] == 'reg_pb':
        await state.set_state(RegForm.waiting_photo2)
        await message.answer("Второй арт")
    else:
        await finalize_preview(message, state)


@dp.message(RegForm.waiting_photo2, F.photo | F.video)
async def process_photo2(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    await state.update_data(photo2=file_id, type2='photo' if message.photo else 'video')
    await finalize_preview(message, state)


async def finalize_preview(message, state):
    data = await state.get_data()

    author = f'<a href="tg://user?id={message.from_user.id}">{html.quote(message.from_user.first_name)}</a>'

    if data['reg_type'] == 'reg_opinion':
        caption = f"<b>Автор:</b> {author}"
    else:
        caption = "<b>ПРУФ-БАТТЛ</b>"

    await state.update_data(final_caption=caption)

    await bot.send_message(message.chat.id, "Проверь и отправь", reply_markup=get_confirm_kb())


@dp.callback_query(F.data == "confirm_send")
async def send_to_mod(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    publish_queue.append(data)

    await callback.message.answer("✅ В очередь")
    await state.clear()


async def main():
    print(">>> BOT STARTED <<<")

    asyncio.create_task(publication_worker())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
 
