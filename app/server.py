"""
Gidrometeorologiya xizmati — Prognoz xarita serveri
Flask + Matplotlib backend
"""
import os, json, uuid
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
from map_renderer import render_forecast_map

app = Flask(__name__, static_folder="static", template_folder="templates")
OUTPUT_DIR = Path("static/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun",
             "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_UZ = ["yakshanba","dushanba","seshanba","chorshanba",
           "payshanba","juma","shanba"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    """3 kunlik prognoz xaritalarini yaratadi"""
    try:
        data = request.get_json()
        days = data.get("days", [])
        if not days:
            return jsonify({"success": False, "error": "Ma'lumot topilmadi"})

        images = []
        telegrams = []

        for i, day in enumerate(days):
            # Xarita generatsiyasi
            filename = f"prognoz_{i}_{uuid.uuid4().hex[:6]}.png"
            filepath = OUTPUT_DIR / filename
            render_forecast_map(day, str(filepath))
            images.append(f"/static/output/{filename}")

            # Telegram matn
            telegrams.append(build_telegram_text(day, i))

        return jsonify({
            "success": True,
            "images": images,
            "telegram": telegrams
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})



WEATHER_LABELS = {
    "ochiq": "havo ochiq",
    "qisman_bulutli": "qisman bulutli",
    "bulutli": "bulutli",
    "tuman": "tuman",
    "yomgir": "yomg'ir",
    "jala": "jala",
    "momaqaldiroq": "momaqaldiroq",
    "qor": "qor",
    "dol": "do'l",
    "chang_boroni": "chang bo'roni",
    "qor_boroni": "qor bo'roni",
}

WEATHER_EMOJI = {
    "ochiq": "☀️", "qisman_bulutli": "⛅", "bulutli": "☁️",
    "tuman": "🌫", "yomgir": "🌧", "jala": "🌦",
    "momaqaldiroq": "⛈", "qor": "❄️", "dol": "🌨",
    "chang_boroni": "💨", "qor_boroni": "🌬",
}


def build_telegram_text(day_data, day_index):
    """Telegram uchun formatlangan matn"""
    labels = ["BUGUN", "ERTAGA", "INDINGA"]
    date_str = day_data.get("date", "")
    if date_str:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        header = f"{d.day} {MONTHS_UZ[d.month-1]}, {DAYS_UZ[d.weekday()]}"
    else:
        d = datetime.now() + timedelta(days=day_index)
        header = f"{d.day} {MONTHS_UZ[d.month-1]}, {DAYS_UZ[d.weekday()]}"

    lines = []
    lines.append(f"🌤 OB-HAVO PROGNOZI — {labels[day_index]}")
    lines.append(f"📅 {header}")
    lines.append("─" * 28)
    lines.append("")

    cities = day_data.get("cities", {})
    for city_name, info in cities.items():
        if not info or info.get("temp_max") is None:
            continue
        emoji = WEATHER_EMOJI.get(info.get("weather",""), "")
        tmin = info.get("temp_min", "")
        tmax = info.get("temp_max", "")
        wind = info.get("wind")
        precip = info.get("precip")

        line = f"{emoji} {city_name}: {tmin}°…{tmax}°C"
        if wind:
            line += f", shamol {wind} m/s"
        if precip and precip > 0:
            line += f", yog'in {precip} mm"
        lines.append(line)

    comment = day_data.get("comment", "")
    if comment:
        lines.append("")
        lines.append(f"📋 {comment}")

    lines.append("")
    lines.append("─" * 28)
    lines.append("📡 Gidrometeorologiya xizmati")
    lines.append("🔗 hydromet.uz")

    return "\n".join(lines)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
