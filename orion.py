import asyncio
import logging
import time
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from aiogram.exceptions import TelegramBadRequest
 
# --- НАСТРОЙКИ ---
TOKEN = os.getenv("BOT_TOKEN1")
CHANNEL_ID = -1002640635653      
MOD_CHAT_ID = -1003911037255     
RULES_LINK = "https://t.me/+wd4SPOWd68MzNGE6"

PUBLISH_INTERVAL = 300 

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

pending_posts = {}
publish_queue = []
last_publish_time = 0
mod_stats = {}

class RegForm(StatesGroup):
    waiting_name = State()
    waiting_universe = State()
    waiting_players = State()
    waiting_conditions = State()
    waiting_photo = State()
    waiting_photo2 = State()

def get_main_kb():
    buttons = [[InlineKeyboardButton(text="📝 Мнение 📝", callback_data="reg_opinion")],
               [InlineKeyboardButton(text="⚔️ ПБ ⚔️", callback_data="reg_pb")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirm_kb():
    buttons = [[InlineKeyboardButton(text="На модерацию ✅", callback_data="confirm_send")],
               [InlineKeyboardButton(text="Отмена ❌", callback_data="cancel")]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

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
                logging.info("Пост успешно опубликован по расписанию.")
            except Exception as e:
                logging.error(f"Ошибка при публикации из очереди: {e}")
        
        await asyncio.sleep(10)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Салам, статюганище! Выбери тип регистрации:", reply_markup=get_main_kb())

@dp.message(Command("reyt"))
async def reyt(message: types.Message):
    if not mod_stats:
        await message.answer("Пока нет статистики.")
        return
    text = "<b>Рейтинг модераторов:</b>\n\n"
    sorted_stats = sorted(mod_stats.items(), key=lambda x: x[1], reverse=True)
    for i, (user, count) in enumerate(sorted_stats, 1):
        text += f"{i}. {user} — {count}\n"
    await message.answer(text, parse_mode="HTML")

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
    await message.answer("Отправь вселенные (каждую с новой строки или через запятую)..")

@dp.message(RegForm.waiting_universe)
async def process_universe(message: types.Message, state: FSMContext):
    await state.update_data(universe=message.text)
    data = await state.get_data()
    if data['reg_type'] == 'reg_pb':
        await state.set_state(RegForm.waiting_players)
        await message.answer("Отправь юзернеймы игроков (каждый с новой строки)..")
    else:
        await state.set_state(RegForm.waiting_conditions)
        await message.answer("Отправь условия (или напиши 'нет')..")

@dp.message(RegForm.waiting_players)
async def process_players(message: types.Message, state: FSMContext):
    await state.update_data(players=message.text)
    await state.set_state(RegForm.waiting_conditions)
    await message.answer("Отправь условия (или напиши 'нет')..")

@dp.message(RegForm.waiting_conditions)
async def process_cond(message: types.Message, state: FSMContext):
    await state.update_data(conditions=message.text)
    await state.set_state(RegForm.waiting_photo)
    await message.answer("Отправь арт или видео (эдит)..")

@dp.message(RegForm.waiting_photo, F.photo | F.video)
async def process_photo1(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    await state.update_data(photo1=file_id, type1='photo' if message.photo else 'video')
    data = await state.get_data()
    if data['reg_type'] == 'reg_pb':
        await state.set_state(RegForm.waiting_photo2)
        await message.answer("Отправь второй арт или видео..")
    else:
        await finalize_preview(message, state)

@dp.message(RegForm.waiting_photo2, F.photo | F.video)
async def process_photo2(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    await state.update_data(photo2=file_id, type2='photo' if message.photo else 'video')
    await finalize_preview(message, state)

async def finalize_preview(message, state):
    data = await state.get_data()
    author_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
    
    if data['reg_type'] == 'reg_opinion':
        unis = "\n".join([f"➤ {u.strip()}" for u in data['universe'].replace(',', '\n').split('\n') if u.strip()])
        conds = "отсутствуют" if data['conditions'].lower() == "нет" else data['conditions']
        custom_footer = "Ꮶᴛᴏ нибудь жᴇᴧᴀᴇᴛ дᴀᴛь ᴇʍу ᴏᴛᴨᴏᴩ ʙ ɸᴏᴩʍᴀᴛᴇ ᴨᴩуɸбᴀᴛᴛᴧ?"
        
        caption = (
            f"<b>— автор мнения:</b> {author_link}\n\n"
            f"<b><u>{data['name']}</u> аннигилирует всех персонажей из ниже представленных вселенных:</b>\n"
            f"<blockquote><b>{unis}</b></blockquote>\n"
            f"<blockquote><b>Условия баттла: {conds}</b></blockquote>\n"
            f"{custom_footer}"
        )
    else:
        chars, universes, players = data['name'].split('\n'), data['universe'].split('\n'), data['players'].split('\n')
        p1, p2 = (chars[0] if len(chars)>0 else "P1"), (chars[1] if len(chars)>1 else "P2")
        u1, u2 = (universes[0] if len(universes)>0 else "U1"), (universes[1] if len(universes)>1 else "U2")
        pl1, pl2 = (players[0].strip() if len(players)>0 else "@id1"), (players[1].strip() if len(players)>1 else "@id2")
        caption = (
            f"<blockquote><b>ПЕРСОНАЛЬНЫЙ ПРУФ-БАТТЛ</b></blockquote>\n\n"
            f"<b>Player 1:</b> {pl1}\n"
            f"<b>{p1} — «{u1}»</b>\n\n"
            f"<b>       * V-E-R-S-U-S *</b>\n\n"
            f"<b>{p2} — «{u2}»</b>\n"
            f"<b>Player 2:</b> {pl2}\n\n"
            f"➥ <b>「<a href='{RULES_LINK}'>Правила боёв</a>」</b>"
        )

    await state.update_data(final_caption=caption)
    if data['reg_type'] == 'reg_opinion':
        if data['type1'] == 'photo':
            await message.answer_photo(data['photo1'], caption=caption, parse_mode="HTML", reply_markup=get_confirm_kb())
        else:
            await message.answer_video(data['photo1'], caption=caption, parse_mode="HTML", reply_markup=get_confirm_kb())
    else:
        m1 = InputMediaPhoto(media=data['photo1'], caption=caption, parse_mode="HTML") if data['type1'] == 'photo' else InputMediaVideo(media=data['photo1'], caption=caption, parse_mode="HTML")
        m2 = InputMediaPhoto(media=data['photo2']) if data['type2'] == 'photo' else InputMediaVideo(media=data['photo2'])
        await message.answer_media_group(media=[m1, m2])
        await message.answer("Проверь ПБ выше. На модерацию?", reply_markup=get_confirm_kb())

@dp.callback_query(F.data == "confirm_send")
async def send_to_mod(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post_id = f"post_{callback.from_user.id}_{int(time.time())}"
    pending_posts[post_id] = data

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Опубликовать 📢", callback_data=f"publish_{post_id}")],
        [InlineKeyboardButton(text="⛔ Отменить публикацию", callback_data=f"decline_{post_id}")]
    ])
    
    if data['reg_type'] == 'reg_opinion':
        await bot.send_photo(MOD_CHAT_ID, data['photo1'], caption=data['final_caption'], parse_mode="HTML", reply_markup=kb) if data['type1'] == 'photo' else await bot.send_video(MOD_CHAT_ID, data['photo1'], caption=data['final_caption'], parse_mode="HTML", reply_markup=kb)
    else:
        m1 = InputMediaPhoto(media=data['photo1'], caption=data['final_caption'], parse_mode="HTML") if data['type1'] == 'photo' else InputMediaVideo(media=data['photo1'], caption=data['final_caption'], parse_mode="HTML")
        m2 = InputMediaPhoto(media=data['photo2']) if data['type2'] == 'photo' else InputMediaVideo(media=data['photo2'])
        await bot.send_media_group(MOD_CHAT_ID, media=[m1, m2])
        await bot.send_message(MOD_CHAT_ID, f"👆 ПБ от {callback.from_user.first_name}", reply_markup=kb)
        
    await callback.message.answer("✅ Отправлено модераторам!")
    await state.clear()

@dp.callback_query(F.data.startswith("decline_"))
async def decline(callback: types.CallbackQuery):
    post_id = callback.data.replace("decline_", "")
    pending_posts.pop(post_id, None)
    await callback.message.delete()
    await callback.answer("❌ Отклонено")

@dp.callback_query(F.data.startswith("publish_"))
async def publish_item(callback: types.CallbackQuery):
    post_id = callback.data.replace("publish_", "")
    data = pending_posts.get(post_id)
    if not data:
        await callback.answer("Ошибка: пост уже в очереди или удален!", show_alert=True)
        return

    publish_queue.append(data)

    user = callback.from_user.first_name
    mod_stats[user] = mod_stats.get(user, 0) + 1

    await callback.message.delete()
    await callback.answer("✅ Добавлено в очередь!")
    del pending_posts[post_id]

@dp.callback_query(F.data == "cancel")
async def cancel_reg(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Отменено.")

async def main():
    print(">>> БОТ ЗАПУЩЕН (ОЧЕРЕДЬ 5 МИНУТ) <<<")
    asyncio.create_task(publication_worker())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
