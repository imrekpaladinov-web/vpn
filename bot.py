import telebot
from telebot import types

# --- ТВОИ ДАННЫЕ ---
TOKEN = '8719021837:AAHjnjO8duDlIA3U9fIySo2KpllrRAltMbA'
ADMIN_GROUP_ID = -1003939085278

bot = telebot.TeleBot(TOKEN)

# Временное хранилище данных (в памяти)
user_data = {}

# --- КНОПКИ ---
def main_keyboard():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="📝 Мнение", callback_data="reg_opinion"))
    markup.add(types.InlineKeyboardButton(text="⚔️ ПБ", callback_data="reg_pb"))
    return markup

# --- ОБРАБОТКА КОМАНД ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "👋 Салам! Я помогу тебе зарегистрировать мнение или ПБ для канала.",
        reply_markup=main_keyboard()
    )

# --- ЛОГИКА ОПРОСА ---
@bot.callback_query_handler(func=lambda call: call.data == "reg_opinion")
def start_opinion(call):
    user_data[call.from_user.id] = {'step': 1, 'type': 'Мнение'}
    bot.send_message(call.message.chat.id, "💬 <b>Мнение — 1/4</b>\n\nВведите имя вашего статюганчика:", parse_mode="HTML")

@bot.message_handler(func=lambda m: m.from_user.id in user_data)
def handle_steps(message):
    user_id = message.from_user.id
    step = user_data[user_id].get('step')

    if step == 1:
        user_data[user_id]['name'] = message.text
        user_data[user_id]['step'] = 2
        bot.send_message(message.chat.id, "💬 <b>2/4 — Оппоненты</b>\n\nИмена персонажей, которые слабее вашего (каждый с новой строки):", parse_mode="HTML")

    elif step == 2:
        user_data[user_id]['opps'] = message.text
        user_data[user_id]['step'] = 3
        bot.send_message(message.chat.id, "💬 <b>3/4 — Условия</b>\n\nУсловия или ограничения. Если нет — пиши «нет»:", parse_mode="HTML")

    elif step == 3:
        user_data[user_id]['cond'] = message.text
        user_data[user_id]['step'] = 4
        bot.send_message(message.chat.id, "💬 <b>4/4 — Арт персонажа</b>\n\nОтправь фото вашего персонажа:", parse_mode="HTML")

    elif step == 4 and message.content_type == 'text':
        bot.send_message(message.chat.id, "Нужно отправить именно <b>фото</b>!", parse_mode="HTML")

# --- ОБРАБОТКА ФОТО (ФИНАЛ) ---
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    if user_id in user_data and user_data[user_id].get('step') == 4:
        # Собираем все данные
        data = user_data[user_id]
        photo_id = message.photo[-1].file_id # Берем самое качественное фото
        
        # Формируем пост для группы
        caption = (
            f"🗳 <b>Новое мнение на модерацию!</b>\n\n"
            f"👤 <b>Статюганчик:</b> {data['name']}\n"
            f"⚔️ <b>Слабее его:</b>\n{data['opps']}\n"
            f"📝 <b>Условия:</b> {data['cond']}\n\n"
            f"От: @{message.from_user.username or 'Аноним'}"
        )

        # Отправляем в твою закрытую группу
        bot.send_photo(ADMIN_GROUP_ID, photo_id, caption=caption, parse_mode="HTML")
        
        # Отвечаем пользователю
        bot.send_message(message.chat.id, "✅ Мнение отправлено в репозиторий на модерацию!")
        
        # Очищаем данные пользователя
        del user_data[user_id]

# --- ЗАПУСК ---
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()
    
