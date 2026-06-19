"""
Gidrometeorologiya xizmati — Prognoz xarita serveri
Flask + SQLite backend
"""
import os, json, uuid
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask import send_from_directory
from models import db, Forecast, init_db

# map_renderer ixtiyoriy (cartopy bo'lmasa ham ishlaydi)
try:
    from map_renderer import render_forecast_map
    HAS_MAP_RENDERER = True
except ImportError:
    HAS_MAP_RENDERER = False

# PDF va Telegram ixtiyoriy
try:
    from pdf_export import export_forecast_pdf
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    from telegram_bot import publish_forecast
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False

app = Flask(__name__, static_folder="static", template_folder="templates")
OUTPUT_DIR = Path("static/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Database init
init_db(app)

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

        # Ma'lumotlar bazasiga saqlash
        forecast = Forecast(created_by="sinoptik", status="published")
        for i, day in enumerate(days):
            forecast.set_day_data(i, day)
        
        telegrams = []
        for i, day in enumerate(days):
            telegrams.append(build_telegram_text(day, i))

        db.session.add(forecast)
        db.session.commit()

        return jsonify({
            "success": True,
            "telegram": telegrams,
            "forecast_id": forecast.id,
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


@app.route("/api/export-pdf/<int:forecast_id>")
def export_pdf(forecast_id):
    """Prognozni PDF sifatida eksport qilish."""
    forecast = Forecast.query.get_or_404(forecast_id)
    images = [p for p in [forecast.image1_path, forecast.image2_path,
              forecast.image3_path] if p]
    # Yo'llarni to'g'rilash
    full_paths = []
    for img in images:
        p = Path(img.lstrip("/"))
        if p.exists():
            full_paths.append(str(p))
        else:
            alt = Path("static/output") / p.name
            if alt.exists():
                full_paths.append(str(alt))

    telegrams = []
    for i in range(3):
        day = forecast.get_day_data(i)
        if day:
            telegrams.append(build_telegram_text(day, i))

    pdf_filename = f"prognoz_{forecast_id}.pdf"
    pdf_path = str(OUTPUT_DIR / pdf_filename)
    export_forecast_pdf(full_paths, telegrams, output_path=pdf_path)
    return jsonify({"success": True, "pdf_url": f"/static/output/{pdf_filename}"})


@app.route("/api/publish-telegram/<int:forecast_id>", methods=["POST"])
def publish_tg(forecast_id):
    """Prognozni Telegram kanalga yuborish."""
    forecast = Forecast.query.get_or_404(forecast_id)
    telegrams = []
    for i in range(3):
        day = forecast.get_day_data(i)
        if day:
            telegrams.append(build_telegram_text(day, i))
    result = publish_forecast(forecast, telegrams)
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


# === API: Arxiv ===
@app.route("/api/latest")
def api_latest():
    """Oxirgi prognozni JSON formatda qaytaradi."""
    forecast = Forecast.query.order_by(Forecast.created_at.desc()).first()
    if not forecast:
        return jsonify({"error": "Hali prognoz mavjud emas"}), 404
    result = forecast.to_dict()
    result["days"] = []
    for i in range(3):
        day_data = forecast.get_day_data(i)
        if day_data:
            result["days"].append(day_data)
    return jsonify(result)


@app.route("/api/archive")
def api_archive():
    """Barcha prognozlar ro'yxati."""
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    forecasts = Forecast.query.order_by(
        Forecast.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "total": forecasts.total,
        "page": page,
        "per_page": per_page,
        "items": [f.to_dict() for f in forecasts.items]
    })


@app.route("/api/forecast/<int:forecast_id>")
def api_forecast_detail(forecast_id):
    """Bitta prognoz tafsiloti."""
    forecast = Forecast.query.get_or_404(forecast_id)
    result = forecast.to_dict()
    result["days"] = []
    for i in range(3):
        day_data = forecast.get_day_data(i)
        if day_data:
            result["days"].append(day_data)
    return jsonify(result)
