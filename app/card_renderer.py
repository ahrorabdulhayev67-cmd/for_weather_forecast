"""
O'zgidromet — 2 ta alohida rasm generatori.
1-RASM: Xarita (to'liq ekran, sifatli)
2-RASM: Jadval (guruhlar + footer)
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

# === CONFIG ===
GEOJSON_URL = "https://raw.githubusercontent.com/akbartus/GeoJSON-Uzbekistan/main/Uzbekistan_regions.json"
CACHE_DIR = Path(__file__).parent / "data"
GEOJSON_CACHE = CACHE_DIR / "uzbekistan_regions.geojson"
LOGO_PATH = Path(__file__).parent / "static" / "uzhydromet-logo.jpg"

MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun",
             "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_UZ = ["dushanba","seshanba","chorshanba","payshanba","juma","shanba","yakshanba"]

REGION_CITY_MAP = {
    "Toshkent":"Toshkent","Tashkent":"Toshkent",
    "Samarqand":"Samarqand","Samarkand":"Samarqand",
    "Buxoro":"Buxoro","Bukhara":"Buxoro",
    "Namangan":"Namangan",
    "Andijon":"Andijon","Andijan":"Andijon",
    "Farg'ona":"Farg'ona","Fergana":"Farg'ona","Fargona":"Farg'ona",
    "Qashqadaryo":"Qarshi","Kashkadarya":"Qarshi",
    "Qoraqalpog'iston":"Nukus","Karakalpakstan":"Nukus",
    "Navoiy":"Navoiy","Navoi":"Navoiy",
    "Surxondaryo":"Termiz","Surkhandarya":"Termiz",
    "Jizzax":"Jizzax","Jizzakh":"Jizzax",
    "Xorazm":"Urganch","Khorezm":"Urganch",
    "Sirdaryo":"Guliston","Syrdarya":"Guliston",
}

SHORT_NAMES = {
    "Toshkent":"Toshkent","Samarqand":"Samarqand","Buxoro":"Buxoro",
    "Namangan":"Namangan","Andijon":"Andijon","Farg'ona":"Farg'ona",
    "Qarshi":"Qarshi","Nukus":"Nukus","Navoiy":"Navoiy",
    "Termiz":"Termiz","Jizzax":"Jizzax","Urganch":"Urganch",
    "Guliston":"Guliston",
}


def temp_to_color(t):
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
    except Exception:
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


# ===========================================================
# 1-RASM: XARITA
# ===========================================================
def render_map_image(day_data, output_path, dpi=180):
    """To'liq ekran xarita — sifatli, katta."""
    cities_data = day_data.get("cities", {})
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

    fig = plt.figure(figsize=(12, 9), facecolor="white", dpi=dpi)

    # HEADER
    fig.patches.append(Rectangle((0, 0.92), 1, 0.08,
        transform=fig.transFigure, facecolor="#0B3D8F", edgecolor="none", zorder=0))

    if LOGO_PATH.exists():
        try:
            logo_ax = fig.add_axes([0.01, 0.925, 0.05, 0.065], zorder=30)
            logo_ax.imshow(Image.open(str(LOGO_PATH)))
            logo_ax.axis("off")
        except Exception:
            pass

    fig.text(0.07, 0.965, "O\u2018ZGIDROMET", fontsize=14, fontweight="bold",
             color="white", va="center", zorder=30)
    fig.text(0.07, 0.935, "Gidrometeorologiya xizmati agentligi",
             fontsize=8, color="#B0C4DE", va="center", zorder=30)
    fig.text(0.55, 0.955, "HARORAT XARITASI", fontsize=14, fontweight="bold",
             color="white", ha="center", va="center", zorder=30)
    fig.text(0.55, 0.93, date_label, fontsize=9, color="#B0C4DE",
             ha="center", va="center", zorder=30)

    # XARITA
    ax = fig.add_axes([0.02, 0.08, 0.96, 0.82])
    ax.set_aspect("equal")
    ax.axis("off")

    centroids = {}
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
                poly = Polygon(coords, closed=True, facecolor=fill_color,
                               edgecolor="#2C3E50", linewidth=0.8, zorder=5)
                ax.add_patch(poly)
                area = abs(np.sum(coords[:-1,0]*coords[1:,1] - coords[1:,0]*coords[:-1,1])/2)
                if area > largest_area:
                    largest_area = area
                    largest_ring = ring

            if city and largest_ring:
                centroids[city] = polygon_centroid(largest_ring)

        ax.autoscale_view()

        # Viloyat nomlari + harorat (katta shrift, oq stroke)
        stroke = [pe.withStroke(linewidth=3.5, foreground="white")]
        for city, (cx, cy) in centroids.items():
            info = cities_data.get(city, {})
            tmax = info.get("temp_max") if info else None
            name = SHORT_NAMES.get(city, city)

            # Nom
            ax.text(cx, cy + 0.08, name, ha="center", va="center",
                    fontsize=7, fontweight="bold", color="#1A2332",
                    path_effects=stroke, zorder=25)
            # Harorat
            if tmax is not None:
                tmin = info.get("temp_min")
                t_str = f"{tmin}\u00b0\u2013{tmax}\u00b0" if tmin else f"{tmax}\u00b0"
                ax.text(cx, cy - 0.12, t_str, ha="center", va="center",
                        fontsize=8, fontweight="bold", color="#C62828",
                        path_effects=stroke, zorder=25)

    # Colorbar
    from matplotlib.colors import ListedColormap, BoundaryNorm
    levels = [15, 20, 25, 28, 30, 32, 34, 36, 38, 40, 42]
    colors = ["#B39DDB","#90CAF9","#80DEEA","#80CBC4","#A5D6A7",
              "#C5E1A5","#E6EE9C","#FFF59D","#FFE082","#FFCC80","#FFAB91"]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(levels, ncolors=len(colors), clip=True)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cax = fig.add_axes([0.15, 0.04, 0.70, 0.018])
    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal",
                        boundaries=levels, ticks=levels)
    cbar.ax.tick_params(labelsize=7)
    cbar.set_label("Kunduzgi harorat, \u00b0C", fontsize=8)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", pad_inches=0.02)
    plt.close(fig)
    return output_path


# ===========================================================
# 2-RASM: JADVAL + FOOTER
# ===========================================================
def render_table_image(day_data, output_path, dpi=180):
    """Guruhlar jadvali + ijtimoiy tarmoqlar."""
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

    fig = plt.figure(figsize=(10, 8), facecolor="white", dpi=dpi)

    # HEADER
    fig.patches.append(Rectangle((0, 0.91), 1, 0.09,
        transform=fig.transFigure, facecolor="#0B3D8F", edgecolor="none", zorder=0))

    if LOGO_PATH.exists():
        try:
            logo_ax = fig.add_axes([0.01, 0.92, 0.055, 0.07], zorder=30)
            logo_ax.imshow(Image.open(str(LOGO_PATH)))
            logo_ax.axis("off")
        except Exception:
            pass

    fig.text(0.08, 0.965, "O\u2018ZGIDROMET", fontsize=13, fontweight="bold",
             color="white", va="center", zorder=30)
    fig.text(0.08, 0.935, "Gidrometeorologiya xizmati agentligi",
             fontsize=7.5, color="#B0C4DE", va="center", zorder=30)
    fig.text(0.55, 0.955, "VILOYATLAR BO\u2018YICHA PROGNOZ", fontsize=13,
             fontweight="bold", color="white", ha="center", va="center", zorder=30)
    fig.text(0.55, 0.925, date_label, fontsize=9, color="#B0C4DE",
             ha="center", va="center", zorder=30)

    # JADVAL
    ax = fig.add_axes([0.03, 0.18, 0.94, 0.70])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    GROUPS = [
        {"name": "Toshkent shahri", "cities": ["Toshkent"]},
        {"name": "Qoraqalpog\u2018iston Resp., Xorazm viloyati", "cities": ["Nukus", "Urganch"]},
        {"name": "Buxoro viloyati", "cities": ["Buxoro"]},
        {"name": "Navoiy viloyati", "cities": ["Navoiy"]},
        {"name": "Toshkent, Samarqand, Jizzax, Sirdaryo viloyatlari", "cities": ["Toshkent", "Samarqand", "Jizzax", "Guliston"]},
        {"name": "Qashqadaryo va Surxondaryo viloyatlari", "cities": ["Qarshi", "Termiz"]},
        {"name": "Andijon, Namangan, Farg\u2018ona viloyatlari", "cities": ["Andijon", "Namangan", "Farg'ona"]},
        {"name": "Tog\u2018 oldi va tog\u2018li hududlar", "cities": ["Toshkent", "Namangan"]},
    ]

    # Jadval sarlavhasi
    cols = [0.01, 0.52, 0.68, 0.85]
    y_h = 0.96
    ax.text(cols[0], y_h, "HUDUD", fontsize=9, fontweight="bold",
            color="#0B3D8F", transform=ax.transAxes)
    ax.text(cols[1], y_h, "KECHASI", fontsize=9, fontweight="bold",
            color="#1565C0", transform=ax.transAxes)
    ax.text(cols[2], y_h, "KUNDUZI", fontsize=9, fontweight="bold",
            color="#C62828", transform=ax.transAxes)
    ax.text(cols[3], y_h, "SHAMOL", fontsize=9, fontweight="bold",
            color="#37474F", transform=ax.transAxes)

    ax.axhline(y=0.94, xmin=0.01, xmax=0.99, color="#B0BEC5",
               linewidth=1, transform=ax.transAxes)

    y0 = 0.90
    row_h = 0.11
    for i, group in enumerate(GROUPS):
        y = y0 - i * row_h

        # Zebra
        if i % 2 == 0:
            ax.add_patch(Rectangle((0, y-0.04), 1, row_h,
                transform=ax.transAxes, facecolor="#F5F9FC",
                edgecolor="none", zorder=1))

        # Ma'lumot
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

        ax.text(cols[0], y, group["name"], fontsize=8.5, color="#1A2332",
                fontweight="bold", va="center", transform=ax.transAxes, zorder=5)
        ax.text(cols[1], y, night, fontsize=10, color="#1565C0",
                fontweight="bold", va="center", transform=ax.transAxes, zorder=5)
        ax.text(cols[2], y, day_t, fontsize=11, color="#C62828",
                fontweight="bold", va="center", transform=ax.transAxes, zorder=5)
        ax.text(cols[3], y, wind, fontsize=8.5, color="#37474F",
                va="center", transform=ax.transAxes, zorder=5)

    # DIQQAT
    if comment:
        warn_y = y0 - len(GROUPS) * row_h - 0.02
        ax.add_patch(FancyBboxPatch(
            (0.01, warn_y-0.015), 0.98, 0.055, transform=ax.transAxes,
            boxstyle="round,pad=0.008", facecolor="#FFF3E0",
            edgecolor="#FF6F00", linewidth=1, zorder=10))
        ax.text(0.03, warn_y + 0.01, f"\u26a0\ufe0f {comment}",
                fontsize=8.5, color="#E65100", va="center",
                fontweight="bold", transform=ax.transAxes, zorder=11)

    # FOOTER — ijtimoiy tarmoqlar
    fig.patches.append(Rectangle((0, 0), 1, 0.14,
        transform=fig.transFigure, facecolor="#F0F4F8",
        edgecolor="#CFD8DC", linewidth=0.5, zorder=0))

    fig.text(0.50, 0.115, f"\u00a9 {dt.year} O\u2018zbekiston Respublikasi Gidrometeorologiya xizmati agentligi",
             fontsize=9, fontweight="bold", color="#263238", ha="center")

    # Ijtimoiy tarmoqlar (katta, aniq)
    links_y = 0.07
    fig.text(0.10, links_y, "\U0001F310  uzgidromet.uz", fontsize=9, color="#0B3D8F", ha="center")
    fig.text(0.30, links_y, "\U0001F4F1  t.me/uzgidromet", fontsize=9, color="#0088CC", ha="center")
    fig.text(0.52, links_y, "\U0001F4F7  instagram.com/uzgidromet.uz", fontsize=9, color="#C13584", ha="center")
    fig.text(0.77, links_y, "\U0001F44D  facebook.com/uzgidromet.uz", fontsize=9, color="#1877F2", ha="center")

    fig.text(0.50, 0.025, "\U0001F3AC  youtube.com/@uzgidromet_", fontsize=9,
             color="#FF0000", ha="center")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", pad_inches=0.02)
    plt.close(fig)
    return output_path


# ===========================================================
# ASOSIY FUNKSIYA (server.py uchun)
# ===========================================================
def render_forecast_card(day_data, output_path, dpi=180):
    """2 ta rasm generatsiya: xarita + jadval."""
    base = Path(output_path)
    stem = base.stem
    parent = base.parent

    # 1-rasm: xarita
    map_path = str(parent / f"{stem}_map.png")
    render_map_image(day_data, map_path, dpi=dpi)

    # 2-rasm: jadval
    tbl_path = str(parent / f"{stem}_table.png")
    render_table_image(day_data, tbl_path, dpi=dpi)

    # Asosiy faylga xaritani saqlash (preview uchun)
    render_map_image(day_data, output_path, dpi=dpi)

    return output_path
