"""
Telegram Bot — Ob-havo prognozini avtomatik yuborish.

Buyruqlar:
  /prognoz  — Bugungi prognoz xaritasini yuboradi
  /arxiv    — Oxirgi 5 ta prognoz
  /start    — Bot haqida ma'lumot

Sozlash:
  BOT_TOKEN muhit o'zgaruvchisi orqali beriladi.
  CHANNEL_ID — prognoz yuboriladigan kanal.

Ishga tushirish:
  python telegram_bot.py
  yoki server.py ichidan import qilib ishlatiladi.
"""
import os
import requests
from pathlib import Path

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@uzhydromet")
API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text, parse_mode="HTML"):
    """Matn yuborish."""
    url = f"{API_BASE}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    return requests.post(url, json=payload)


def send_photo(chat_id, photo_path, caption=""):
    """Rasm yuborish."""
    url = f"{API_BASE}/sendPhoto"
    with open(photo_path, "rb") as photo:
        files = {"photo": photo}
        data = {"chat_id": chat_id, "caption": caption}
        return requests.post(url, data=data, files=files)


def send_media_group(chat_id, photo_paths, caption=""):
    """Bir nechta rasm yuborish (album)."""
    url = f"{API_BASE}/sendMediaGroup"
    media = []
    files = {}
    for i, path in enumerate(photo_paths):
        file_key = f"photo{i}"
        media.append({
            "type": "photo",
            "media": f"attach://{file_key}",
            "caption": caption if i == 0 else "",
        })
        files[file_key] = open(path, "rb")

    import json
    data = {"chat_id": chat_id, "media": json.dumps(media)}
    response = requests.post(url, data=data, files=files)

    for f in files.values():
        f.close()
    return response


def publish_forecast(forecast, telegram_texts):
    """Prognozni Telegram kanalga yuborish."""
    if not BOT_TOKEN:
        return {"error": "TELEGRAM_BOT_TOKEN sozlanmagan"}

    results = []

    # 3 kunlik matnni yuborish
    full_text = "\n\n".join(telegram_texts)
    r = send_message(CHANNEL_ID, full_text)
    results.append(r.status_code)

    # Rasmlarni album sifatida yuborish
    image_paths = []
    for attr in ["image1_path", "image2_path", "image3_path"]:
        path = getattr(forecast, attr, None)
        if path:
            full_path = Path("static/output") / Path(path).name
            if full_path.exists():
                image_paths.append(str(full_path))

    if image_paths:
        r = send_media_group(CHANNEL_ID, image_paths,
                            caption="Qisqa muddatli ob-havo prognozi")
        results.append(r.status_code)

    return {"status": "sent", "responses": results}
