import os
import json
import base64
import datetime

USERS_DIR = "database/users/"
CONTROL_FILE = "access_control.json"

def build_subscription():
    if not os.path.exists(CONTROL_FILE): 
        print("Ошибка: Нет файла access_control.json")
        return
    
    with open(CONTROL_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    master_links = config.get("server_list", [])
    
    if not os.path.exists(USERS_DIR): 
        os.makedirs(USERS_DIR)
        
    user_files = [f for f in os.listdir(USERS_DIR) if f.endswith('.json')]
    
    # ТВОЯ ПОСЛЕДОВАТЕЛЬНОСТЬ НАЗВАНИЙ
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
            # Форматируем ID для названия (заменяем дефис на нижнее подчеркивание для стиля GL_4150)
            u_id_raw = file_name.replace('.json', '')
            u_id_display = u_id_raw.replace('-', '_') 
            
            with open(os.path.join(USERS_DIR, file_name), 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            user_configs = []
            # Заголовок профиля (здесь оставляем GL-XXXX для системы)
            header = f"#profile-title: Ghost Link | {u_id_raw}\n"
            header += f"#profile-update-interval: 1\n"
            header += f"#subscription-userinfo: upload=0; download=0; total={total_traffic}; expire={expire_date}\n\n"
            user_configs.append(header)

            if not user_data.get("active", True):
                user_configs.append(f"vless://expired@0.0.0.0:443?encryption=none#🟥 ДОСТУП ЗАКРЫТ [{u_id_display}]")
            else:
                for i, link in enumerate(master_links):
                    clean_link = link.split('#')[0]
                    # Берем название из твоего списка по индексу
                    tag = labels[i] if i < len(labels) else f"Сервер {i+1}"
                    # Итог: Ghost Link | Название [GL_XXXX]
                    user_configs.append(f"{clean_link}#Ghost Link | {tag} [{u_id_display}]")

            # Сохраняем в персональный файл (sub_GL-XXXX.txt)
            final_text = "\n".join(user_configs)
            encoded = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
            
            with open(f"sub_{u_id_raw}.txt", "w", encoding='utf-8') as f:
                f.write(encoded)
            print(f"Обновлена подписка для: {u_id_raw}")

        except Exception as e:
            print(f"Ошибка в файле {file_name}: {e}")

if __name__ == "__main__":
    build_subscription()
    
