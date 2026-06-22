"""
O'zgidromet — Professional prognoz kartochka generatori.
matplotlib + GeoJSON (geopandas'siz!) asosida sifatli xarita.

Layout (1400x900):
+------------------------------------------------------+
| HEADER: Logo + Sarlavha + Sana                       |
+---------------------------+--------------------------+
| CHAP: O'zbekiston xaritasi| O'NG: 8 guruh jadvali   |
| (GeoJSON poligonlar,      | Kechasi/Kunduzi/Shamol  |
|  rangli, nomi + harorat)  | Ob-havo belgisi         |
+---------------------------+--------------------------+
| DIQQAT XABARI                                        |
+------------------------------------------------------+
| FOOTER: sana + @uzgidromet + belgilar izohi          |
+------------------------------------------------------+
"""
import json
import urllib.request
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
from matplotlib.collections import PatchCollection
from PIL import Image

# === KONFIGURATSIYA ===
GEOJSON_URL = "https://raw.githubusercontent.com/akbartus/GeoJSON-Uzbekistan/main/Uzbekistan_regions.json"
CACHE_DIR = Path(__file__).parent / "data"
GEOJSON_CACHE = CACHE_DIR / "uzbekistan_regions.geojson"
LOGO_PATH = Path(__file__).parent / "static" / "uzhydromet-logo.jpg"

MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun",
             "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_UZ = ["dushanba","seshanba","chorshanba","payshanba","juma","shanba","yakshanba"]

# Viloyat nomi mapping: GeoJSON -> input shahar
REGION_CITY_MAP = {
    "Toshkent": "Toshkent",
    "Tashkent": "Toshkent",
    "Samarqand": "Samarqand",
    "Samarkand": "Samarqand",
    "Buxoro": "Buxoro",
    "Bukhara": "Buxoro",
    "Namangan": "Namangan",
    "Andijon": "Andijon",
    "Andijan": "Andijon",
    "Farg'ona": "Farg'ona",
    "Fergana": "Farg'ona",
    "Fargona": "Farg'ona",
    "Qashqadaryo": "Qarshi",
    "Kashkadarya": "Qarshi",
    "Qoraqalpog'iston": "Nukus",
    "Karakalpakstan": "Nukus",
    "Navoiy": "Navoiy",
    "Navoi": "Navoiy",
    "Surxondaryo": "Termiz",
    "Surkhandarya": "Termiz",
    "Jizzax": "Jizzax",
    "Jizzakh": "Jizzax",
    "Xorazm": "Urganch",
    "Khorezm": "Urganch",
    "Sirdaryo": "Guliston",
    "Syrdarya": "Guliston",
}

# Harorat ranglari (professional gradient)
def temp_to_color(t):
    if t is None: return "#EEEEEE"
    if t >= 42: return "#7F0000"
    if t >= 40: return "#B30000"
    if t >= 38: return "#D32F2F"
    if t >= 36: return "#FF5722"
    if t >= 34: return "#FF7A00"
    if t >= 32: return "#FF9800"
    if t >= 30: return "#FFE600"
    if t >= 28: return "#CDDC39"
    if t >= 25: return "#8DE04F"
    if t >= 20: return "#1FA187"
    if t >= 15: return "#2B59C3"
    return "#7B3FB2"


def download_geojson():
    """GeoJSON yuklab cache qilish."""
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
    """GeoJSON viloyat nomini input shahar nomiga aylantirish."""
    for key, city in REGION_CITY_MAP.items():
        if key.lower() in region_name.lower() or region_name.lower() in key.lower():
            return city
    return None


def polygon_centroid(coords):
    """Oddiy centroid hisoblash."""
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    return (sum(xs)/len(xs), sum(ys)/len(ys))


def render_forecast_card(day_data, output_path, dpi=150):
    """Professional prognoz kartochkasi."""
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

    # GeoJSON yuklash
    geojson_path = download_geojson()

    # === FIGURE ===
    fig = plt.figure(figsize=(14, 9), facecolor="white", dpi=dpi)

    # === HEADER ===
    fig.patches.append(FancyBboxPatch(
        (0.0, 0.92), 1.0, 0.08, transform=fig.transFigure,
        facecolor="#0B3D8F", edgecolor="none", zorder=0,
        boxstyle="square,pad=0"))

    # Logo
    if LOGO_PATH.exists():
        try:
            logo_ax = fig.add_axes([0.01, 0.925, 0.05, 0.065], zorder=30)
            logo_img = Image.open(str(LOGO_PATH))
            logo_ax.imshow(logo_img)
            logo_ax.axis("off")
        except Exception:
            pass

    fig.text(0.07, 0.96, "O'ZGIDROMET", fontsize=14, fontweight="bold",
             color="white", va="center", zorder=30)
    fig.text(0.07, 0.935, "Gidrometeorologiya xizmati agentligi",
             fontsize=8, color="#CCDDFF", va="center", zorder=30)

    fig.text(0.50, 0.955, "QISQA MUDDATLI OB-HAVO PROGNOZI",
             fontsize=16, fontweight="bold", color="white",
             ha="center", va="center", zorder=30)
    fig.text(0.50, 0.93, date_label, fontsize=9, color="#CCDDFF",
             ha="center", va="center", zorder=30)

    fig.text(0.97, 0.95, "hydromet.uz", fontsize=8, color="#AAC4E8",
             ha="right", va="center", zorder=30)

    # === CHAP: XARITA ===
    ax_map = fig.add_axes([0.02, 0.12, 0.50, 0.78])
    ax_map.set_aspect("equal")
    ax_map.axis("off")
    ax_map.set_title("HARORAT XARITASI", fontsize=11, fontweight="bold",
                     color="#0B3D8F", pad=6)

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
            fill_color = temp_to_color(tmax) if tmax else "#E8EEF4"

            # Poligonlarni chizish
            if geom_type == "Polygon":
                for ring in geom.get("coordinates", []):
                    coords = np.array(ring)
                    poly = Polygon(coords, closed=True,
                                   facecolor=fill_color, edgecolor="#0B4EA2",
                                   linewidth=0.6, zorder=5)
                    ax_map.add_patch(poly)

                    # Harorat va nom yozish
                    if tmax is not None:
                        cx, cy = polygon_centroid(ring)
                        tmin = info.get("temp_min")
                        t_str = f"{tmin}\u00b0-{tmax}\u00b0" if tmin else f"{tmax}\u00b0"
                        ax_map.text(cx, cy, t_str, ha="center", va="center",
                                    fontsize=6.5, fontweight="bold", color="#0B3D91",
                                    path_effects=[pe.withStroke(linewidth=2.2, foreground="white")],
                                    zorder=20)

            elif geom_type == "MultiPolygon":
                for polygon in geom.get("coordinates", []):
                    for ring in polygon:
                        coords = np.array(ring)
                        poly = Polygon(coords, closed=True,
                                       facecolor=fill_color, edgecolor="#0B4EA2",
                                       linewidth=0.6, zorder=5)
                        ax_map.add_patch(poly)

                # Nom + harorat (birinchi polygon'ning centroid'ida)
                if tmax is not None and polygon:
                    first_ring = polygon[0] if polygon else []
                    if first_ring:
                        cx, cy = polygon_centroid(first_ring)
                        tmin = info.get("temp_min")
                        t_str = f"{tmin}\u00b0-{tmax}\u00b0" if tmin else f"{tmax}\u00b0"
                        ax_map.text(cx, cy, t_str, ha="center", va="center",
                                    fontsize=6.5, fontweight="bold", color="#0B3D91",
                                    path_effects=[pe.withStroke(linewidth=2.2, foreground="white")],
                                    zorder=20)

        ax_map.autoscale_view()
    else:
        ax_map.text(0.5, 0.5, "GeoJSON yuklanmadi", ha="center",
                    transform=ax_map.transAxes, fontsize=12, color="red")

    # Colorbar
    from matplotlib.colors import ListedColormap, BoundaryNorm
    levels = [15, 20, 25, 28, 30, 32, 34, 36, 38, 40, 42]
    colors = ["#7B3FB2","#2B59C3","#1FA187","#8DE04F","#CDDC39",
              "#FFE600","#FF9800","#FF7A00","#FF5722","#D32F2F","#B30000"]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(levels, ncolors=len(colors), clip=True)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cax = fig.add_axes([0.08, 0.10, 0.38, 0.015])
    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal",
                        boundaries=levels, ticks=levels)
    cbar.ax.tick_params(labelsize=6)
    cbar.set_label("Harorat, \u00b0C", fontsize=7)

    # === O'NG: GURUHLAR JADVALI ===
    ax_tbl = fig.add_axes([0.54, 0.12, 0.44, 0.78])
    ax_tbl.axis("off")
    ax_tbl.set_xlim(0, 1)
    ax_tbl.set_ylim(0, 1)

    ax_tbl.text(0.5, 0.97, "VILOYATLAR BO\u2018YICHA PROGNOZ",
                ha="center", fontsize=11, fontweight="bold",
                color="#0B3D8F", transform=ax_tbl.transAxes)

    # Guruhlar
    GROUPS = [
        {"name": "Toshkent shahri", "cities": ["Toshkent"]},
        {"name": "Qoraqalpog\u2018iston R., Xorazm", "cities": ["Nukus", "Urganch"]},
        {"name": "Buxoro viloyati", "cities": ["Buxoro"]},
        {"name": "Navoiy viloyati", "cities": ["Navoiy"]},
        {"name": "Toshkent, Samarqand,\nJizzax, Sirdaryo vil.", "cities": ["Toshkent", "Samarqand", "Jizzax", "Guliston"]},
        {"name": "Qashqadaryo,\nSurxondaryo vil.", "cities": ["Qarshi", "Termiz"]},
        {"name": "Andijon, Namangan,\nFarg\u2018ona vil.", "cities": ["Andijon", "Namangan", "Farg'ona"]},
        {"name": "Tog\u2018 oldi va tog\u2018li\nhududlar", "cities": ["Toshkent", "Namangan"]},
    ]

    # Jadval sarlavhasi
    cols = [0.01, 0.48, 0.66, 0.84]
    y_hdr = 0.92
    ax_tbl.text(cols[0], y_hdr, "Hudud", fontsize=8, fontweight="bold", color="#0B3D8F",
                transform=ax_tbl.transAxes)
    ax_tbl.text(cols[1], y_hdr, "Kechasi", fontsize=8, fontweight="bold", color="#1565C0",
                transform=ax_tbl.transAxes)
    ax_tbl.text(cols[2], y_hdr, "Kunduzi", fontsize=8, fontweight="bold", color="#C22A00",
                transform=ax_tbl.transAxes)
    ax_tbl.text(cols[3], y_hdr, "Shamol", fontsize=8, fontweight="bold", color="#455A64",
                transform=ax_tbl.transAxes)

    # Chiziq
    ax_tbl.axhline(y=0.91, xmin=0.01, xmax=0.99, color="#CFE0EE",
                   linewidth=0.8, transform=ax_tbl.transAxes)

    y0 = 0.87
    row_h = 0.105
    for i, group in enumerate(GROUPS):
        y = y0 - i * row_h

        # Zebra
        if i % 2 == 0:
            ax_tbl.add_patch(Rectangle((0.0, y - 0.03), 1.0, row_h,
                                       transform=ax_tbl.transAxes,
                                       facecolor="#F6FBFF", edgecolor="none", zorder=1))

        # Ma'lumotlarni yig'ish
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

        ax_tbl.text(cols[0], y, group["name"], fontsize=7.5, color="#1A2332",
                    fontweight="bold", va="center", transform=ax_tbl.transAxes, zorder=5)
        ax_tbl.text(cols[1], y, night, fontsize=8, color="#1565C0",
                    va="center", transform=ax_tbl.transAxes, zorder=5)
        ax_tbl.text(cols[2], y, day_t, fontsize=9, color="#C22A00",
                    fontweight="bold", va="center", transform=ax_tbl.transAxes, zorder=5)
        ax_tbl.text(cols[3], y, wind, fontsize=7, color="#455A64",
                    va="center", transform=ax_tbl.transAxes, zorder=5)

    # === DIQQAT XABARI ===
    if comment:
        ax_tbl.add_patch(FancyBboxPatch(
            (0.0, 0.01), 1.0, 0.08, transform=ax_tbl.transAxes,
            boxstyle="round,pad=0.01", facecolor="#FCEBEB",
            edgecolor="#F09595", linewidth=1, zorder=10))
        ax_tbl.text(0.02, 0.05, f"\u26a0 {comment}", fontsize=7.5,
                    color="#791F1F", va="center", transform=ax_tbl.transAxes,
                    fontweight="bold", zorder=11)

    # === FOOTER ===
    fig.text(0.02, 0.02, f"\u00a9 {dt.year} Gidrometeorologiya xizmati agentligi",
             fontsize=7, color="#78909C")
    fig.text(0.97, 0.02, "@uzgidromet  |  hydromet.uz",
             fontsize=7, color="#78909C", ha="right")

    # === SAQLASH ===
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", pad_inches=0.03)
    plt.close(fig)
    return output_path
