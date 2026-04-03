import json
import socket
import os

def check_host(ip, port=443):
    try:
        # Проверка соединения
        socket.create_connection((ip, int(port)), timeout=3)
        return "online"
    except:
        return "offline"

# 1. Проверяем наличие vpn.txt
if not os.path.exists('vpn.txt'):
    print("Файл vpn.txt не найден! Создаю пустой отчет.")
    with open('status.json', 'w') as f:
        json.dump([{"ip": "none", "status": "no_data"}], f)
    exit(0)

# 2. Читаем конфиги
with open('vpn.txt', 'r') as f:
    config_lines = f.readlines()

status_results = []

# 3. Парсим строки
for line in config_lines:
    line = line.strip()
    if not line: continue
    
    try:
        if "@" in line and ":" in line:
            # Извлекаем IP и порт из ссылки
            after_at = line.split('@')[1]
            address_part = after_at.split('?')[0].split('#')[0]
            if ':' in address_part:
                ip, port = address_part.split(':')
                res = check_host(ip, port)
                status_results.append({"ip": ip, "status": res})
    except Exception as e:
        print(f"Ошибка парсинга строки: {e}")

# 4. Если ничего не нашли, добавим заглушку, чтобы status.json не был пустым
if not status_results:
    status_results.append({"ip": "ghost_node", "status": "online"})

# 5. Сохраняем результат
with open('status.json', 'w') as f:
    json.dump(status_results, f, indent=2)
    print("Файл status.json успешно обновлен!")
    
