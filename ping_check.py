import json
import os
import datetime

# Файл, который читает твой сайт
STATUS_FILE = 'status.json'

def update_status():
    # Данные для сайта
    status_data = {
        "status": "online",
        "last_check": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    try:
        # Пишем файл в корень, чтобы JS его увидел
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=4, ensure_ascii=False)
        print("✅ Status updated successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

if __name__ == "__main__":
    update_status()
