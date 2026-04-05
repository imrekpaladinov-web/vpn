import os
import json
import base64
import datetime

USERS_DIR = "database/users/"
CONTROL_FILE = "access_control.json"
SUB_FILE = "sub.txt"

def build_subscription():
    try:
        if not os.path.exists(CONTROL_FILE):
            print("Файл access_control.json не найден!")
            return
            
        with open(CONTROL_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        master_links = config.get("server_list", [])
    except Exception as e:
        print(f"Ошибка чтения контроллера: {e}")
        return

    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)
    
    user_files = [f for f in os.listdir(USERS_DIR) if f.endswith('.json')]
    
    # Темы для названий серверов
    labels = ["Основной ⚡", "Резерв 🚀", "Запасной 🛡️", "Media 🎬", "Social 📱"]
    
    # Параметры "Бесконечности"
    # 100 ТБ в байтах
    total_traffic = 109951162777600 
    # Дата через 10 лет (timestamp)
    expire_date = int((datetime.datetime.now() + datetime.timedelta(days=3650)).timestamp())

    all_users_content = []

    for file_name in user_files:
        try:
            with open(os.path.join(USERS_DIR, file_name), 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            u_id = user_data.get("id", "Unknown")
            is_active = user_data.get("active", True)

            # Формируем заголовок для каждого пользователя
            # Это магия, которая делает красивое название и трафик
            header = f"#profile-title: Ghost Link | {u_id}\n"
            header += f"#profile-update-interval: 1\n"
            header += f"#subscription-userinfo: upload=0; download=0; total={total_traffic}; expire={expire_date}\n"

            user_configs = [header]

            if is_active:
                for i, link in enumerate(master_links):
                    label = labels[i] if i < len(labels) else f"Node-{i}"
                    # Убираем старые метки из ссылки если они были, и ставим свои
                    clean_link = link.split('#')[0] 
                    personalized = f"{clean_link}#Ghost Link | {label}"
                    user_configs.append(personalized)
            else:
                expired = f"vless://expired@0.0.0.0:443?encryption=none#🟥 ПОДПИСКА ИСТЕКЛА [{u_id}]"
                user_configs.append(expired)
            
            # Добавляем конфиг этого пользователя в общий список (разделив пустой строкой)
            all_users_content.append("\n".join(user_configs))
            
        except Exception as e:
            print(f"Ошибка обработки файла {file_name}: {e}")
            continue

    # Склеиваем всех пользователей в один большой текст
    final_text = "\n\n".join(all_users_content)
    
    # Упаковка всего этого в Base64
    try:
        encoded = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
        with open(SUB_FILE, 'w', encoding='utf-8') as f:
            f.write(encoded)
        print(f"Успех! Сгенерирована подписка для {len(user_files)} пользователей.")
    except Exception as e:
        print(f"Ошибка при сохранении sub.txt: {e}")

if __name__ == "__main__":
    build_subscription()
