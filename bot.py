import telebot
import time

# Твои данные уже вшиты
TOKEN = '8719021837:AAHjnjO8duDlIA3U9fIySo2KpllrRAltMbA'
ADMIN_GROUP_ID = -1003939085278

bot = telebot.TeleBot(TOKEN)

def run_loop():
    start_time = time.time()
    print("Бот запущен. Мониторинг начат...")

    # Работаем 5 минут (300 секунд), чтобы не вылетать
    while time.time() - start_time < 300:
        try:
            # Запрашиваем обновления
            updates = bot.get_updates(offset=None, timeout=1)
            
            for update in updates:
                if update.message and update.message.text:
                    chat_id = update.message.chat.id
                    text = update.message.text
                    
                    if text == "/start":
                        bot.send_message(chat_id, "Салам! Я на связи. Пришли инфу, и я перекину её в репозиторий.")
                    else:
                        # Формируем отчет для группы
                        user_info = f"👤 От: @{update.message.from_user.username or 'Аноним'}\n"
                        report = f"📩 <b>Новое поступление:</b>\n\n{text}\n\n{user_info}"
                        
                        # Отправляем в твою группу
                        bot.send_message(ADMIN_GROUP_ID, report, parse_mode="HTML")
                        bot.send_message(chat_id, "✅ Красава, улетело в группу!")
                    
                    # Помечаем сообщение как прочитанное
                    bot.get_updates(offset=update.update_id + 1)

            # Проверка каждые 5 секунд (как ты просил)
            time.sleep(5) 
            
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_loop()
          
