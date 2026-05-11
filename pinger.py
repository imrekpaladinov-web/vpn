import time
import requests
import os

KAGGLE_API = os.getenv("KAGGLE_API")

while True:

    try:

        r = requests.get(
            KAGGLE_API,
            timeout=30
        )

        print(
            f"PING OK: {r.status_code}"
        )

    except Exception as e:

        print(
            f"PING ERROR: {e}"
        )

    # каждые 4 минуты
    time.sleep(240)
