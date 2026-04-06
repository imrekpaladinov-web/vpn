import os
import json
import datetime
import time

# --- КОНФИГУРАЦИЯ ПУТЕЙ ---
USERS_DIR = "database/users/"
SUBS_DIR = "database/subs/"  
CONTROL_FILE = "access_control.json"

def build_subscription():
    if not os.path.exists(SUBS_DIR):
        os.makedirs(SUBS_DIR)

    if not os.path.exists(CONTROL_FILE): 
        print("❌ Ошибка: Нет файла access_control.json")
        return
    
    with open(CONTROL_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    master_links = config.get("server_list", [])
    user_files = [f for f in os.listdir(USERS_DIR) if f.endswith('.json')]
    
    labels = ["Основной", "Резерв", "Запасной", "YouTube", "Social Media"]

    # Лимиты трафика (бесконечность)
    total_traffic = 109951162777600 
    
    # Метка времени для пробития кэша на iPhone
    update_ts = int(time.time())

    for file_name in user_files:
        try:
            u_id_raw = file_name.replace('.json', '')
            
            with open(os.path.join(USERS_DIR, file_name), 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # Берем дату из JSON или ставим 100 лет вперед
            exp_date_raw = user_data.get("expire_date", "31.12.2099")
            
            # Шапка профиля
            header = f"#profile-title: Ghost Link | {u_id_raw}\n"
            header += f"#profile-update-interval: 1\n"
            header += f"#version: {update_ts}\n" # Магия против кэша
            
            # Проверяем СТАТУС (Бан или Активен)
            is_active = user_data.get("active", True)

            if not is_active:
                # --- ЛОГИКА БАНА ---
                header = f"#profile-title: 🟥 ПОДПИСКА НЕДОСТУПНА | BANNED\n"
                header += f"#announce: ⚠️ ДОСТУП ЗАКРЫТ. Обратитесь к @admin для продления.\n\n"
                
                # Одна нерабочая ссылка с жирным текстом
                banned_msg = f"vless://banned-id@127.0.0.1:443?remarks=🟥%20BANNED%20%7C%20ПОДПИСКА%20ИСТЕКЛА#GhostLink_System"
                final_text = header + banned_msg
            else:
                # --- ЛОГИКА РАБОЧЕЙ ПОДПИСКИ ---
                header += f"#subscription-userinfo: upload=0; download=0; total={total_traffic}; expire=253402214400\n"
                header += f"#announce: ✅ Активно до: {exp_date_raw} | ID: {u_id_raw}\n\n"
                
                user_configs = [header]
                for i, link in enumerate(master_links):
                    clean_link = link.split('#')[0]
                    tag = labels[i] if i < len(labels) else f"Сервер {i+1}"
                    # Формируем красивую ссылку без лишних пробелов
                    user_configs.append(f"{clean_link}#GhostLink_{tag}_{u_id_raw}")
                
                final_text = "\n".join(user_configs)
            
            # Сохраняем файл (sub_GL-4150.txt)
            file_path = os.path.join(SUBS_DIR, f"sub_{u_id_raw}.txt")
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(final_text)
                
            print(f"🚀 {'BANNED' if not is_active else 'ACTIVE'} -> {file_path}")

        except Exception as e:
            print(f"⚠️ Ошибка в файле {file_name}: {e}")

if __name__ == "__main__":
    build_subscription()
    
