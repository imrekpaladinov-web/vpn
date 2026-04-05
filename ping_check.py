import os
import json
import base64

USERS_DIR = "database/users/"
CONTROL_FILE = "access_control.json"
SUB_FILE = "sub.txt"

def build_subscription():
    try:
        with open(CONTROL_FILE, 'r') as f:
            config = json.load(f)
        # Берем список серверов
        master_links = config.get("server_list", [])
    except Exception as e:
        print(f"Ошибка чтения контроллера: {e}")
        return

    if not os.path.exists(USERS_DIR):
        os.makedirs(USERS_DIR)
    
    final_configs = []
    user_files = [f for f in os.listdir(USERS_DIR) if f.endswith('.json')]
    
    # Темы для названий серверов (чтобы юзер понимал что где)
    labels = ["Основной ⚡", "Резерв ⚡", "Запасной ⚡", "YouTube 🎬", "TikTok/Insta 📱"]

    for file_name in user_files:
        try:
            with open(os.path.join(USERS_DIR, file_name), 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            u_id = user_data.get("id", "Unknown")
            is_active = user_data.get("active", True)

            if is_active:
                # Генерируем для юзера весь пак серверов
                for i, link in enumerate(master_links):
                    label = labels[i] if i < len(labels) else "Server"
                    personalized = f"{link}#GhostLink | {label} [{u_id}]"
                    final_configs.append(personalized)
            else:
                # Если забанен — только один нерабочий конфиг
                expired = f"vless://expired@0.0.0.0:443?encryption=none#🟥 Подписка истекла [{u_id}]"
                final_configs.append(expired)
        except:
            continue

    # Упаковка в Base64
    final_text = "\n".join(final_configs)
    encoded = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')

    with open(SUB_FILE, 'w') as f:
        f.write(encoded)
    print(f"Обновлено! Всего строк в подписке: {len(final_configs)}")

if __name__ == "__main__":
    build_subscription()
