import os
import json
import base64
import datetime

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
USERS_DIR = "database/users/"
SUBS_DIR = "database/subs/"  # Папка для готовых подписок
CONTROL_FILE = "access_control.json"

def build_subscription():
    # Создаем папку для подписок, если её еще нет
    if not os.path.exists(SUBS_DIR):
        os.makedirs(SUBS_DIR)
        print(f"✅ Создана папка: {SUBS_DIR}")

    if not os.path.exists(CONTROL_FILE): 
        print("❌ Ошибка: Нет файла access_control.json")
        return
    
    with open(CONTROL_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    master_links = config.get("server_list", [])
    
    if not os.path.exists(USERS_DIR): 
        os.makedirs(USERS_DIR)
        
    user_files = [f for f in os.listdir(USERS_DIR) if f.endswith('.json')]
    
    # Твоя последовательность названий
    labels = [
        "Основной",
        "Резерв",
        "Запасной",
        "YouTube",
        "Instagram, TikTok"
    ]

    total_traffic = 109951162777600 
    expire_date = int((datetime.datetime.now() + datetime.timedelta(days=3650)).timestamp())

    for file_name in user_files:
        try:
            u_id_raw = file_name.replace('.json', '')
            u_id_display = u_id_raw.replace('-', '_') 
            
            with open(os.path.join(USERS_DIR, file_name), 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            user_configs = []
            header = f"#profile-title: Ghost Link | {u_id_raw}\n"
            header += f"#profile-update-interval: 1\n"
            header += f"#subscription-userinfo: upload=0; download=0; total={total_traffic}; expire={expire_date}\n\n"
            user_configs.append(header)

            if not user_data.get("active", True):
                user_configs.append(f"vless://expired@0.0.0.0:443?encryption=none#🟥 ДОСТУП ЗАКРЫТ [{u_id_display}]")
            else:
                for i, link in enumerate(master_links):
                    clean_link = link.split('#')[0]
                    tag = labels[i] if i < len(labels) else f"Сервер {i+1}"
                    user_configs.append(f"{clean_link}#Ghost Link | {tag} [{u_id_display}]")

            # Формируем финальный текст и кодируем в Base64
            final_text = "\n".join(user_configs)
            encoded = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
            
            # СОХРАНЯЕМ В ПАПКУ database/subs/
            file_path = os.path.join(SUBS_DIR, f"sub_{u_id_raw}.txt")
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(encoded)
            print(f"🚀 Файл готов: {file_path}")

        except Exception as e:
            print(f"⚠️ Ошибка в файле {file_name}: {e}")

if __name__ == "__main__":
    build_subscription()
    
