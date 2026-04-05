import os
import json
import base64
import datetime

USERS_DIR = "database/users/"
CONTROL_FILE = "access_control.json"
SUB_FILE = "sub.txt"

def build_subscription():
    if not os.path.exists(CONTROL_FILE): return
    with open(CONTROL_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    master_links = config.get("server_list", [])

    user_files = [f for f in os.listdir(USERS_DIR) if f.endswith('.json')]
    
    # 100 ТБ и дата 2036 год
    total_traffic = 109951162777600 
    expire_date = int((datetime.datetime.now() + datetime.timedelta(days=3650)).timestamp())

    all_configs = []

    # ВАЖНО: Добавляем общий заголовок в самый верх ОДИН РАЗ
    # Это уберет "4150" и поставит общее имя для всей группы
    header = f"#profile-title: Ghost Link | Premium\n"
    header += f"#profile-update-interval: 1\n"
    header += f"#subscription-userinfo: upload=0; download=0; total={total_traffic}; expire={expire_date}\n\n"
    all_configs.append(header)

    for file_name in user_files:
        try:
            with open(os.path.join(USERS_DIR, file_name), 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            u_id = file_name.replace('.json', '')
            if not user_data.get("active", True):
                all_configs.append(f"vless://expired@0.0.0.0:443?encryption=none#🟥 ДОСТУП ЗАКРЫТ [{u_id}]")
                continue

            for link in master_links:
                clean_link = link.split('#')[0]
                # Добавляем ID в название сервера, чтобы юзер видел свой ID там
                all_configs.append(f"{clean_link}#Ghost Link | {u_id}")
        except: continue

    final_text = "\n".join(all_configs)
    encoded = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')

    with open(SUB_FILE, 'w', encoding='utf-8') as f:
        f.write(encoded)
    print(f"Готово! Юзеров в базе: {len(user_files)}")

if __name__ == "__main__":
    build_subscription()
