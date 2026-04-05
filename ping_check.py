import os
import json
import base64
import datetime

USERS_DIR = "database/users/"
CONTROL_FILE = "access_control.json"
# SUB_FILE больше не нужен как одна переменная, будем делать много файлов

def build_subscription():
    if not os.path.exists(CONTROL_FILE): return
    if not os.path.exists(USERS_DIR): os.makedirs(USERS_DIR)
    
    with open(CONTROL_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    master_links = config.get("server_list", [])

    user_files = [f for f in os.listdir(USERS_DIR) if f.endswith('.json')]
    
    total_traffic = 109951162777600 
    expire_date = int((datetime.datetime.now() + datetime.timedelta(days=3650)).timestamp())

    for file_name in user_files:
        try:
            with open(os.path.join(USERS_DIR, file_name), 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            u_id = file_name.replace('.json', '')
            user_configs = []

            # Личный заголовок для каждого юзера
            header = f"#profile-title: Ghost Link | {u_id}\n"
            header += f"#profile-update-interval: 1\n"
            header += f"#subscription-userinfo: upload=0; download=0; total={total_traffic}; expire={expire_date}\n\n"
            user_configs.append(header)

            if not user_data.get("active", True):
                user_configs.append(f"vless://expired@0.0.0.0:443?encryption=none#🟥 ДОСТУП ЗАКРЫТ [{u_id}]")
            else:
                for link in master_links:
                    clean_link = link.split('#')[0]
                    user_configs.append(f"{clean_link}#Ghost Link | {u_id}")

            # Кодируем и сохраняем в ЛИЧНЫЙ файл (например, sub_GL-9727.txt)
            final_text = "\n".join(user_configs)
            encoded = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
            
            with open(f"sub_{u_id}.txt", 'w', encoding='utf-8') as f:
                f.write(encoded)
                
        except Exception as e:
            print(f"Ошибка юзера {file_name}: {e}")
            continue

    print(f"Готово! Создано подписок: {len(user_files)}")

if __name__ == "__main__":
    build_subscription()
