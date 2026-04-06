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
    total_traffic = 109951162777600 
    update_ts = int(time.time())
    
    # Получаем текущую дату для сравнения
    now_dt = datetime.datetime.now()

    for file_name in user_files:
        try:
            u_id_raw = file_name.replace('.json', '')
            
            with open(os.path.join(USERS_DIR, file_name), 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            # 1. ПОЛУЧАЕМ ДАТУ И СТАТУС ИЗ JSON
            exp_date_str = user_data.get("expire_date", "31.12.2099")
            is_active = user_data.get("active", True)
            status_announce = f"✅ Активно до: {exp_date_str}"

            # 2. АВТО-ПРОВЕРКА СРОКА (МАГИЯ БАНА)
            try:
                # Превращаем строку "ДД.ММ.ГГГГ" в дату
                expire_dt = datetime.datetime.strptime(exp_date_str, "%d.%m.%Y")
                
                # Если сегодня больше, чем дата в конфиге — баним
                if now_dt > expire_dt:
                    is_active = False
                    status_announce = f"❌ СРОК ИСТЕК ({exp_date_str})"
            except Exception as e:
                print(f"⚠️ Ошибка формата даты у {u_id_raw}: {e}")

            # 3. ФОРМИРУЕМ КОНТЕНТ
            if not is_active:
                # --- ЕСЛИ ЗАБАНЕН ИЛИ СРОК ВЫШЕЛ ---
                header = f"#profile-title: 🟥 Ghost Link | BANNED\n"
                header += f"#profile-update-interval: 1\n"
                header += f"#version: {update_ts}\n"
                header += f"#announce: {status_announce}. Доступ закрыт. Обратитесь к @admin\n\n"
                
                banned_msg = f"vless://banned-id@127.0.0.1:443?remarks=🟥%20BANNED%20%7C%20ПОДПИСКА%20ИСТЕКЛА#GhostLink_System"
                final_text = header + banned_msg
            else:
                # --- ЕСЛИ ВСЁ ХОРОШО ---
                header = f"#profile-title: Ghost Link | {u_id_raw}\n"
                header += f"#profile-update-interval: 1\n"
                header += f"#version: {update_ts}\n"
                header += f"#subscription-userinfo: upload=0; download=0; total={total_traffic}; expire=253402214400\n"
                header += f"#announce: {status_announce} | ID: {u_id_raw} ⚡️ Приятного пользования!\n\n"
                
                user_configs = [header]
                for i, link in enumerate(master_links):
                    clean_link = link.split('#')[0]
                    tag = labels[i] if i < len(labels) else f"Сервер {i+1}"
                    user_configs.append(f"{clean_link}#GhostLink_{tag}_{u_id_raw}")
                
                final_text = "\n".join(user_configs)
            
            # 4. СОХРАНЯЕМ ФАЙЛ
            file_path = os.path.join(SUBS_DIR, f"sub_{u_id_raw}.txt")
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(final_text)
                
            print(f"🚀 {u_id_raw}: {'BANNED' if not is_active else 'OK'}")

        except Exception as e:
            print(f"⚠️ Ошибка в файле {file_name}: {e}")

if __name__ == "__main__":
    build_subscription()
    
