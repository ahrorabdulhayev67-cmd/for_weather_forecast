"""
Gidrometeorologiya xizmati — Ob-havo prognozi xarita generatori
Soddalashtirilgan server: faqat statik fayllar + HTML sahifa
"""
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from models import db, Forecast, init_db

# map_renderer ixtiyoriy (cartopy bo'lmasa ham ishlaydi)
try:
    from map_renderer import render_forecast_map
    HAS_MAP_RENDERER = True
except ImportError:
    HAS_MAP_RENDERER = False

# pro_renderer — o'chirilgan (geopandas kerak, Render'da ishlamaydi)
HAS_PRO_RENDERER = False

# card_renderer — PIL asosida kartochka generatori (fallback)
try:
    from card_renderer import render_forecast_card
    HAS_CARD_RENDERER = True
except ImportError:
    HAS_CARD_RENDERER = False

# text_parser — Telegram matn parser
try:
    from text_parser import parse_forecast_text
    HAS_TEXT_PARSER = True
except ImportError:
    HAS_TEXT_PARSER = False

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

# Output directory (Render'da /tmp ishlatish)
try:
    OUTPUT_DIR = Path("static/output")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Test yozish
    test_f = OUTPUT_DIR / ".test"
    test_f.write_text("ok")
    test_f.unlink()
except (OSError, PermissionError):
    OUTPUT_DIR = Path("/tmp/output")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Database init
init_db(app)

MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun",
             "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_UZ = ["yakshanba","dushanba","seshanba","chorshanba",
           "payshanba","juma","shanba"]

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
    "ochiq": "\u2600\ufe0f", "qisman_bulutli": "\u26c5", "bulutli": "\u2601\ufe0f",
    "tuman": "\ud83c\udf2b", "yomgir": "\ud83c\udf27", "jala": "\ud83c\udf26",
    "momaqaldiroq": "\u26c8", "qor": "\u2744\ufe0f", "dol": "\ud83c\udf28",
    "chang_boroni": "\ud83d\udca8", "qor_boroni": "\ud83c\udf2c",
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate():
    """3 kunlik prognoz ma'lumotlarini saqlaydi va Telegram matnini qaytaradi."""
    try:
        data = request.get_json()

        # Matn rejimi: Telegram matn paste qilingan bo'lsa parse qilish
        raw_text = data.get("raw_text", "")
        if raw_text and HAS_TEXT_PARSER:
            parsed = parse_forecast_text(raw_text)
            days = [{
                "date": data.get("date", ""),
                "day_index": 0,
                "cities": parsed.get("cities", {}),
                "comment": parsed.get("warning", ""),
                "groups": parsed.get("groups", []),
            }]
        else:
            days = data.get("days", [])

        if not days:
            return jsonify({"success": False, "error": "Ma'lumot topilmadi"})

        # Ma'lumotlar bazasiga saqlash
        forecast = Forecast(created_by="sinoptik", status="published")
        for i, day in enumerate(days):
            if i < 3:
                forecast.set_day_data(i, day)

        db.session.add(forecast)
        db.session.flush()  # ID olish uchun

        telegrams = []
        for i, day in enumerate(days):
            if i < 3:
                telegrams.append(build_telegram_text(day, i))

        # Rasm generatsiya: avval pro_renderer, keyin card_renderer (fallback)
        images = []
        for i, day in enumerate(days):
            if i >= 3:
                break
            filename = f"prognoz_{forecast.id}_day{i+1}.png"
            output_path = str(OUTPUT_DIR / filename)

            rendered = False
            # 1) Professional renderer (matplotlib + geopandas)
            if HAS_PRO_RENDERER and not rendered:
                try:
                    render_pro_forecast(day, output_path)
                    rendered = True
                except Exception as e:
                    print(f"[pro_renderer] xatolik: {e}")

            # 2) card_renderer (matplotlib + GeoJSON)
            if HAS_CARD_RENDERER and not rendered:
                try:
                    render_forecast_card(day, output_path)
                    rendered = True
                    # map va table rasmlarni qo'shish
                    map_filename = f"prognoz_{forecast.id}_day{i+1}_map.png"
                    tbl_filename = f"prognoz_{forecast.id}_day{i+1}_table.png"
                    map_path = OUTPUT_DIR / map_filename
                    tbl_path = OUTPUT_DIR / tbl_filename
                    if map_path.exists():
                        images.append(f"/static/output/{map_filename}")
                    if tbl_path.exists():
                        images.append(f"/static/output/{tbl_filename}")
                except Exception as e:
                    print(f"[card_renderer] xatolik: {e}")
                    import traceback
                    traceback.print_exc()

            if rendered:
                if i == 0:
                    forecast.image1_path = output_path
                elif i == 1:
                    forecast.image2_path = output_path
                elif i == 2:
                    forecast.image3_path = output_path

        db.session.add(forecast)
        db.session.commit()

        return jsonify({
            "success": True,
            "telegram": telegrams,
            "forecast_id": forecast.id,
            "images": images,
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def build_telegram_text(day_data, day_index):
    """Telegram uchun formatlangan matn."""
    labels = ["BUGUN", "ERTAGA", "INDINGA"]
    date_str = day_data.get("date", "")
    if date_str:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        header = f"{d.day} {MONTHS_UZ[d.month-1]}, {DAYS_UZ[d.weekday()]}"
    else:
        d = datetime.now() + timedelta(days=day_index)
        header = f"{d.day} {MONTHS_UZ[d.month-1]}, {DAYS_UZ[d.weekday()]}"

    lines = []
    lines.append(f"\ud83c\udf24 OB-HAVO PROGNOZI \u2014 {labels[day_index]}")
    lines.append(f"\ud83d\udcc5 {header}")
    lines.append("\u2500" * 28)
    lines.append("")

    cities = day_data.get("cities", {})
    for city_name, info in cities.items():
        if not info or info.get("temp_max") is None:
            continue
        emoji = WEATHER_EMOJI.get(info.get("weather", ""), "")
        tmin = info.get("temp_min", "")
        tmax = info.get("temp_max", "")
        wind = info.get("wind")
        precip = info.get("precip")

        line = f"{emoji} {city_name}: {tmin}\u00b0\u2026{tmax}\u00b0C"
        if wind:
            line += f", shamol {wind} m/s"
        if precip and precip > 0:
            line += f", yog'in {precip} mm"
        lines.append(line)

    comment = day_data.get("comment", "")
    if comment:
        lines.append("")
        lines.append(f"\ud83d\udccb {comment}")

    lines.append("")
    lines.append("\u2500" * 28)
    lines.append("\ud83d\udce1 Gidrometeorologiya xizmati")
    lines.append("\ud83d\udd17 hydromet.uz")

    return "\n".join(lines)


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


@app.route("/api/render-map/<int:forecast_id>", methods=["POST"])
def render_map_api(forecast_id):
    """Server-side xarita render (cartopy mavjud bo'lsa)."""
    if not HAS_MAP_RENDERER:
        return jsonify({"success": False, "error": "Xarita renderer o'rnatilmagan (cartopy kerak)"})

    forecast = Forecast.query.get_or_404(forecast_id)
    images = []
    for i in range(3):
        day_data = forecast.get_day_data(i)
        if not day_data:
            continue
        filename = f"forecast_{forecast_id}_day{i+1}.png"
        output_path = str(OUTPUT_DIR / filename)
        render_forecast_map(day_data, output_path)
        images.append(f"/static/output/{filename}")

        # DB ga rasm yo'lini saqlash
        if i == 0:
            forecast.image1_path = output_path
        elif i == 1:
            forecast.image2_path = output_path
        elif i == 2:
            forecast.image3_path = output_path

    db.session.commit()
    return jsonify({"success": True, "images": images})


# === SERVER ISHGA TUSHIRISH ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
