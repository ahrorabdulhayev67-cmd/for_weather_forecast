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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("static", filename)


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
