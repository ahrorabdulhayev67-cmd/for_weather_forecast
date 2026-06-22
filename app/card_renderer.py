"""
O'zgidromet — Professional prognoz kartochka generatori v3.
matplotlib + GeoJSON. Barcha UX muammolari tuzatilgan.

Dizayn prinsipi:
- CHAP PANEL: Xaritada FAQAT viloyat nomi (qisqa) — overlap yo'q
- O'NG PANEL: 8 ta guruh jadvali (O'zgidromet TG formati)
- Kontrast: to'q fonda OQ matn, och fonda to'q matn
- Sana faqat 1 marta (header)
"""
import json
import urllib.request
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
from PIL import Image

# === KONFIGURATSIYA ===
GEOJSON_URL = "https://raw.githubusercontent.com/akbartus/GeoJSON-Uzbekistan/main/Uzbekistan_regions.json"
CACHE_DIR = Path(__file__).parent / "data"
GEOJSON_CACHE = CACHE_DIR / "uzbekistan_regions.geojson"
LOGO_PATH = Path(__file__).parent / "static" / "uzhydromet-logo.jpg"

MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun",
             "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_UZ = ["dushanba","seshanba","chorshanba","payshanba","juma","shanba","yakshanba"]

# GeoJSON viloyat nomi -> input shahar
REGION_CITY_MAP = {
    "Toshkent": "Toshkent", "Tashkent": "Toshkent",
    "Samarqand": "Samarqand", "Samarkand": "Samarqand",
    "Buxoro": "Buxoro", "Bukhara": "Buxoro",
    "Namangan": "Namangan",
    "Andijon": "Andijon", "Andijan": "Andijon",
    "Farg'ona": "Farg'ona", "Fergana": "Farg'ona", "Fargona": "Farg'ona",
    "Qashqadaryo": "Qarshi", "Kashkadarya": "Qarshi",
    "Qoraqalpog'iston": "Nukus", "Karakalpakstan": "Nukus",
    "Navoiy": "Navoiy", "Navoi": "Navoiy",
    "Surxondaryo": "Termiz", "Surkhandarya": "Termiz",
    "Jizzax": "Jizzax", "Jizzakh": "Jizzax",
    "Xorazm": "Urganch", "Khorezm": "Urganch",
    "Sirdaryo": "Guliston", "Syrdarya": "Guliston",
}

# Xaritada ko'rsatiladigan QISQA nom (overlap oldini olish)
SHORT_NAMES = {
    "Toshkent": "Tosh.", "Samarqand": "Sam.", "Buxoro": "Bux.",
    "Namangan": "Nam.", "Andijon": "And.", "Farg'ona": "Far.",
    "Qarshi": "Qar.", "Nukus": "Nuk.", "Navoiy": "Nav.",
    "Termiz": "Ter.", "Jizzax": "Jiz.", "Urganch": "Urg.",
    "Guliston": "Gul.",
}


def temp_to_color(t):
    """Harorat -> rang. Och ranglar (label o'qilishi uchun)."""
    if t is None: return "#E8EEF4"
    if t >= 42: return "#FFCDD2"
    if t >= 40: return "#FFAB91"
    if t >= 38: return "#FFCC80"
    if t >= 36: return "#FFE082"
    if t >= 34: return "#FFF59D"
    if t >= 32: return "#E6EE9C"
    if t >= 30: return "#C5E1A5"
    if t >= 28: return "#A5D6A7"
    if t >= 25: return "#80CBC4"
    if t >= 20: return "#80DEEA"
    if t >= 15: return "#90CAF9"
    return "#B39DDB"


def download_geojson():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if GEOJSON_CACHE.exists():
        return GEOJSON_CACHE
    try:
        urllib.request.urlretrieve(GEOJSON_URL, str(GEOJSON_CACHE))
        return GEOJSON_CACHE
    except Exception as e:
        print(f"GeoJSON yuklanmadi: {e}")
        return None


def get_city_for_region(region_name):
    for key, city in REGION_CITY_MAP.items():
        if key.lower() in region_name.lower() or region_name.lower() in key.lower():
            return city
    return None


def polygon_centroid(coords):
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    return (sum(xs)/len(xs), sum(ys)/len(ys))


def render_forecast_card(day_data, output_path, dpi=150):
    cities_data = day_data.get("cities", {})
    comment = day_data.get("comment", "")
    date_str = day_data.get("date", "")

    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            dt = datetime.now()
    else:
        dt = datetime.now()
    date_label = f"{dt.day} {MONTHS_UZ[dt.month-1]} {dt.year}, {DAYS_UZ[dt.weekday()]}"

    geojson_path = download_geojson()

    # === FIGURE ===
    fig = plt.figure(figsize=(15, 9.5), facecolor="white", dpi=dpi)

    # === HEADER (ko'k panel) ===
    fig.patches.append(Rectangle((0, 0.92), 1, 0.08,
        transform=fig.transFigure, facecolor="#0B3D8F",
        edgecolor="none", zorder=0))

    # Logo (albatta ko'rsatiladi)
    if LOGO_PATH.exists():
        try:
            logo_ax = fig.add_axes([0.01, 0.925, 0.045, 0.06], zorder=30)
            logo_img = Image.open(str(LOGO_PATH))
            logo_ax.imshow(logo_img)
            logo_ax.axis("off")
        except Exception:
            pass

    fig.text(0.065, 0.965, "O\u2018ZGIDROMET",
             fontsize=13, fontweight="bold", color="white", va="center", zorder=30)
    fig.text(0.065, 0.94, "Gidrometeorologiya xizmati agentligi",
             fontsize=7.5, color="#B0C4DE", va="center", zorder=30)
    fig.text(0.50, 0.96, "OB-HAVO PROGNOZI",
             fontsize=16, fontweight="bold", color="white",
             ha="center", va="center", zorder=30)
    fig.text(0.50, 0.935, date_label,
             fontsize=9, color="#B0C4DE", ha="center", va="center", zorder=30)

    # === CHAP: XARITA (kattalashtirilgan) ===
    ax_map = fig.add_axes([0.01, 0.10, 0.55, 0.80])
    ax_map.set_aspect("equal")
    ax_map.axis("off")

    # Xarita chizish
    centroids = {}  # city -> (cx, cy) saqlash
    if geojson_path and geojson_path.exists():
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson = json.load(f)

        for feature in geojson.get("features", []):
            props = feature.get("properties", {})
            region_name = props.get("name") or props.get("NAME_1") or ""
            geom = feature.get("geometry", {})
            geom_type = geom.get("type", "")

            city = get_city_for_region(region_name)
            info = cities_data.get(city, {}) if city else {}
            tmax = info.get("temp_max") if info else None
            fill_color = temp_to_color(tmax)

            all_rings = []
            if geom_type == "Polygon":
                all_rings = geom.get("coordinates", [])
            elif geom_type == "MultiPolygon":
                for mp in geom.get("coordinates", []):
                    all_rings.extend(mp)

            largest_ring = None
            largest_area = 0
            for ring in all_rings:
                coords = np.array(ring)
                poly = Polygon(coords, closed=True,
                               facecolor=fill_color, edgecolor="#2C3E50",
                               linewidth=0.7, zorder=5)
                ax_map.add_patch(poly)
                # Eng katta polygon uchun centroid
                area = abs(np.sum(coords[:-1,0]*coords[1:,1] - coords[1:,0]*coords[:-1,1])/2)
                if area > largest_area:
                    largest_area = area
                    largest_ring = ring

            if city and largest_ring:
                centroids[city] = polygon_centroid(largest_ring)

        ax_map.autoscale_view()

        # Viloyat nomlari — FAQAT qisqa nom (overlap yo'q)
        stroke = [pe.withStroke(linewidth=3, foreground="white")]
        for city, (cx, cy) in centroids.items():
            short = SHORT_NAMES.get(city, city[:4])
            ax_map.text(cx, cy, short, ha="center", va="center",
                        fontsize=6, fontweight="bold", color="#1A2332",
                        path_effects=stroke, zorder=25)

    # === O'NG: GURUHLAR JADVALI ===
    ax_tbl = fig.add_axes([0.57, 0.10, 0.41, 0.80])
    ax_tbl.axis("off")
    ax_tbl.set_xlim(0, 1)
    ax_tbl.set_ylim(0, 1)

    ax_tbl.text(0.5, 0.97, "VILOYATLAR BO\u2018YICHA",
                ha="center", fontsize=10, fontweight="bold",
                color="#0B3D8F", transform=ax_tbl.transAxes)

    GROUPS = [
        {"name": "Toshkent shahri", "cities": ["Toshkent"]},
        {"name": "Qoraqalpog\u2018iston R., Xorazm", "cities": ["Nukus", "Urganch"]},
        {"name": "Buxoro viloyati", "cities": ["Buxoro"]},
        {"name": "Navoiy viloyati", "cities": ["Navoiy"]},
        {"name": "Toshkent, Samarqand,\nJizzax, Sirdaryo", "cities": ["Toshkent", "Samarqand", "Jizzax", "Guliston"]},
        {"name": "Qashqadaryo, Surxondaryo", "cities": ["Qarshi", "Termiz"]},
        {"name": "Andijon, Namangan,\nFarg\u2018ona", "cities": ["Andijon", "Namangan", "Farg'ona"]},
        {"name": "Tog\u2018 oldi va tog\u2018li hududlar", "cities": ["Toshkent", "Namangan"]},
    ]

    # Sarlavha qatori
    cols = [0.0, 0.50, 0.68, 0.85]
    y_h = 0.93
    ax_tbl.text(cols[0], y_h, "Hudud", fontsize=7.5, fontweight="bold",
                color="#455A64", transform=ax_tbl.transAxes)
    ax_tbl.text(cols[1], y_h, "Kechasi", fontsize=7.5, fontweight="bold",
                color="#1565C0", transform=ax_tbl.transAxes)
    ax_tbl.text(cols[2], y_h, "Kunduzi", fontsize=7.5, fontweight="bold",
                color="#C62828", transform=ax_tbl.transAxes)
    ax_tbl.text(cols[3], y_h, "Shamol", fontsize=7.5, fontweight="bold",
                color="#455A64", transform=ax_tbl.transAxes)
    ax_tbl.axhline(y=0.915, xmin=0, xmax=1, color="#B0BEC5",
                   linewidth=0.6, transform=ax_tbl.transAxes)

    y0 = 0.88
    row_h = 0.105
    for i, group in enumerate(GROUPS):
        y = y0 - i * row_h

        # Zebra
        if i % 2 == 0:
            ax_tbl.add_patch(Rectangle((0, y-0.035), 1, row_h,
                transform=ax_tbl.transAxes, facecolor="#F5F9FC",
                edgecolor="none", zorder=1))

        # Ma'lumot yig'ish
        tmins, tmaxs, winds = [], [], []
        for city in group["cities"]:
            info = cities_data.get(city, {})
            if not info: continue
            if info.get("temp_min") is not None: tmins.append(info["temp_min"])
            if info.get("temp_max") is not None: tmaxs.append(info["temp_max"])
            if info.get("wind") is not None: winds.append(info["wind"])

        night = f"{min(tmins)}-{max(tmins)}\u00b0" if tmins else "\u2014"
        day_t = f"{min(tmaxs)}-{max(tmaxs)}\u00b0" if tmaxs else "\u2014"
        wind = f"{min(winds)}-{max(winds)} m/s" if winds else "\u2014"

        # Hudud nomi
        ax_tbl.text(cols[0], y, group["name"], fontsize=7, color="#1A2332",
                    fontweight="bold", va="center", transform=ax_tbl.transAxes, zorder=5,
                    linespacing=1.1)
        # Kechasi
        ax_tbl.text(cols[1], y, night, fontsize=8.5, color="#1565C0",
                    fontweight="bold", va="center", transform=ax_tbl.transAxes, zorder=5)
        # Kunduzi
        ax_tbl.text(cols[2], y, day_t, fontsize=9.5, color="#C62828",
                    fontweight="bold", va="center", transform=ax_tbl.transAxes, zorder=5)
        # Shamol
        ax_tbl.text(cols[3], y, wind, fontsize=7, color="#455A64",
                    va="center", transform=ax_tbl.transAxes, zorder=5)

    # DIQQAT xabari
    if comment:
        warn_y = y0 - len(GROUPS) * row_h - 0.02
        ax_tbl.add_patch(FancyBboxPatch(
            (0, warn_y - 0.01), 1, 0.06, transform=ax_tbl.transAxes,
            boxstyle="round,pad=0.008", facecolor="#FFF3E0",
            edgecolor="#FF6F00", linewidth=0.8, zorder=10))
        ax_tbl.text(0.02, warn_y + 0.02, f"\u26a0 {comment}",
                    fontsize=7, color="#E65100", va="center",
                    fontweight="bold", transform=ax_tbl.transAxes, zorder=11)

    # === FOOTER (ijtimoiy tarmoqlar bilan) ===
    fig.patches.append(Rectangle((0, 0), 1, 0.065,
        transform=fig.transFigure, facecolor="#F5F7FA",
        edgecolor="#E0E5EC", linewidth=0.5, zorder=0))

    fig.text(0.02, 0.04, f"\u00a9 {dt.year} Gidrometeorologiya xizmati agentligi",
             fontsize=8, fontweight="bold", color="#37474F")
    fig.text(0.02, 0.015,
             "\U0001F310 uzgidromet.uz    "
             "\U0001F4F1 t.me/uzgidromet    "
             "\U0001F4F7 instagram.com/uzgidromet.uz    "
             "\U0001F44D facebook.com/uzgidromet.uz    "
             "\U0001F3AC youtube.com/@uzgidromet_",
             fontsize=7, color="#546E7A")

    # === SAQLASH ===
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", pad_inches=0.02)
    plt.close(fig)
    return output_path
