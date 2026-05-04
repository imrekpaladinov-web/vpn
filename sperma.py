from telethon import TelegramClient, events

import asyncio

import os

import requests

from io import BytesIO

api_id = int(os.getenv(30820072))

api_hash = os.getenv(08ab3125e509ddb26b2f3baba13426cd)

chat_id = int(os.getenv(-1003777022478))

client = TelegramClient("session", api_id, api_hash)

def search_anime(image_bytes):

    try:

        files = {'image': image_bytes}

        response = requests.post("https://api.trace.moe/search", files=files)

        data = response.json()

        if "result" in data and len(data["result"]) > 0:

            result = data["result"][0]

            anime = result.get("filename", "")

            episode = result.get("episode", "")

            similarity = result.get("similarity", 0)

            print("Найдено:", anime, "эп:", episode, "точность:", similarity)

            # ⚠️ это НЕ имя персонажа, а просто попытка

            return anime.split(".")[0]

    except Exception as e:

        print("Ошибка поиска:", e)

    return None

@client.on(events.NewMessage(chats=chat_id))

async def handler(event):

    if not event.photo:

        return

    try:

        print("📸 Найдена картинка, ищем в интернете...")

        file = await event.download_media(bytes)

        # ⏳ имитация “долгого поиска”

        await asyncio.sleep(5)

        name = search_anime(file)

        # ещё задержка (как ты хотел)

        await asyncio.sleep(10)

        if name:

            print("🎯 Пытаемся словить:", name)

            await event.reply(f"/protecc {name}")

        else:

            print("❌ Не нашли имя")

            await event.reply("/protecc test")

    except Exception as e:

        print("Ошибка:", e)

client.start()

print("🚀 Запущен тестовый бот")

client.run_until_disconnected()