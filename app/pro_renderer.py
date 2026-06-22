"""
O'zgidromet — Professional 4-blokli ob-havo infografika generatori.
matplotlib + geopandas asosida.

Uzgidromet.txt skriptidan server-side ga moslashtirilgan versiya.

Layout (A4 landscape):
+----------------------------------------------------+
|  HEADER: QISQA MUDDATLI OB-HAVO PROGNOZI          |
+------------------------+---------------------------+
|  1-BLOK: HARORAT       |  2-BLOK: SHAMOL VA       |
|  XARITASI (rangli      |  YOG'INGARCHILIK         |
|  viloyatlar + temp)    |  (rangli + iconlar)      |
+------------------------+---------------------------+
|  3-BLOK: MUHIM         |  4-BLOK: VILOYATLAR      |
|  OGOHLANTIRISH         |  BO'YICHA JADVAL         |
|  (sel, issiqlik)       |  (harorat + icon)        |
+------------------------+---------------------------+
|  FOOTER: sana + @uzgidromet                        |
+----------------------------------------------------+

Kerakli kutubxonalar: matplotlib, geopandas, numpy
GeoJSON: runtime da GitHub'dan yuklanadi va cache qilinadi.
"""
import os
import re
import json
import urllib.request
from pathlib import Path
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Polygon
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap, BoundaryNorm

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False


# === KONFIGURATSIYA ===
GEOJSON_URL = "https://raw.githubusercontent.com/akbartus/GeoJSON-Uzbekistan/main/Uzbekistan_regions.json"
CACHE_DIR = Path(__file__).parent / "data"
GEOJSON_CACHE = CACHE_DIR / "uzbekistan_regions.geojson"

MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun",
             "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_UZ = ["dushanba","seshanba","chorshanba","payshanba","juma","shanba","yakshanba"]

# Viloyat nomi -> xaritadagi nom
REGION_NAME_MAP = {
    "Toshkent": ["Toshkent", "Tashkent"],
    "Samarqand": ["Samarqand", "Samarkand"],
    "Buxoro": ["Buxoro", "Bukhara", "Bukhoro"],
    "Namangan": ["Namangan"],
    "Andijon": ["Andijon", "Andijan"],
    "Farg'ona": ["Farg'ona", "Fergana", "Fargona"],
    "Qarshi": ["Qashqadaryo", "Kashkadarya"],
    "Nukus": ["Qoraqalpog'iston", "Karakalpakstan"],
    "Navoiy": ["Navoiy", "Navoi"],
    "Termiz": ["Surxondaryo", "Surkhandarya"],
    "Jizzax": ["Jizzax", "Jizzakh"],
    "Urganch": ["Xorazm", "Khorezm"],
    "Guliston": ["Sirdaryo", "Syrdarya"],
}

# Harorat ranglari
TEMP_LEVELS = [10, 15, 20, 25, 30, 35, 40, 45]
TEMP_COLORS = [
    "#7B3FB2",  # 10-15 sovuq
    "#2B59C3",  # 15-20 salqin
    "#1FA187",  # 20-25 mo'tadil
    "#8DE04F",  # 25-30 iliq
    "#FFE600",  # 30-35 issiq
    "#FF7A00",  # 35-40 juda issiq
    "#B30000",  # 40-45 ekstremal
]


def temp_to_color(value):
    """Harorat qiymatiga rang berish."""
    if value is None or np.isnan(value):
        return "#EEEEEE"
    if value < 15: return TEMP_COLORS[0]
    if value < 20: return TEMP_COLORS[1]
    if value < 25: return TEMP_COLORS[2]
    if value < 30: return TEMP_COLORS[3]
    if value < 35: return TEMP_COLORS[4]
    if value < 40: return TEMP_COLORS[5]
    return TEMP_COLORS[6]


def download_geojson():
    """GeoJSON ni yuklab olish va cache qilish."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if GEOJSON_CACHE.exists():
        return GEOJSON_CACHE
    try:
        urllib.request.urlretrieve(GEOJSON_URL, str(GEOJSON_CACHE))
        return GEOJSON_CACHE
    except Exception as e:
        print(f"GeoJSON yuklanmadi: {e}")
        return None


def find_region_match(gdf_name, city_name):
    """GeoJSON dagi viloyat nomini shahar nomi bilan solishtirish."""
    gdf_lower = gdf_name.lower()
    candidates = REGION_NAME_MAP.get(city_name, [city_name])
    for cand in candidates:
        if cand.lower() in gdf_lower or gdf_lower in cand.lower():
            return True
    return False


# === OB-HAVO IKONALARNI CHIZISH ===
def draw_sun(ax, x, y, s=1, transform=None, z=100):
    tr = transform or ax.transData
    r = 0.035 * s
    for a in np.linspace(0, 2*np.pi, 12, endpoint=False):
        ax.add_line(Line2D(
            [x + np.cos(a)*r*1.3, x + np.cos(a)*r*1.9],
            [y + np.sin(a)*r*1.3, y + np.sin(a)*r*1.9],
            color="#FFC400", linewidth=1.5, transform=tr, zorder=z))
    ax.add_patch(Circle((x, y), r, facecolor="#FFD21A",
                         edgecolor="#FF9900", linewidth=0.8, transform=tr, zorder=z+1))


def draw_cloud(ax, x, y, s=1, transform=None, z=100):
    tr = transform or ax.transData
    r = 0.035 * s
    ax.add_patch(Circle((x-r, y), r*0.8, facecolor="#6F8390",
                         edgecolor="none", transform=tr, zorder=z))
    ax.add_patch(Circle((x, y+r*0.3), r, facecolor="#B7C6D0",
                         edgecolor="#6D7D86", linewidth=0.4, transform=tr, zorder=z+1))
    ax.add_patch(Circle((x+r, y), r*0.8, facecolor="#6F8390",
                         edgecolor="none", transform=tr, zorder=z))


def draw_rain(ax, x, y, s=1, transform=None, z=100):
    draw_cloud(ax, x, y, s=s, transform=transform, z=z)
    tr = transform or ax.transData
    r = 0.035 * s
    for dx in [-r*0.8, 0, r*0.8]:
        ax.add_line(Line2D(
            [x+dx, x+dx-r*0.2], [y-r, y-r*1.7],
            color="#009CFF", linewidth=1.5, transform=tr, zorder=z+5))


def draw_storm(ax, x, y, s=1, transform=None, z=100):
    draw_rain(ax, x, y, s=s, transform=transform, z=z)
    tr = transform or ax.transData
    r = 0.035 * s
    bolt = np.array([
        [x+r*0.1, y-r*0.6], [x-r*0.4, y-r*1.9],
        [x+r*0.0, y-r*1.7], [x-r*0.2, y-r*2.6],
        [x+r*0.7, y-r*1.3], [x+r*0.2, y-r*1.5]])
    ax.add_patch(Polygon(bolt, closed=True, facecolor="#FFC400",
                          edgecolor="#E09800", linewidth=0.5, transform=tr, zorder=z+8))


def put_icon(ax, kind, x, y, s=1, transform=None, z=100):
    if kind in ("sun", "ochiq"):
        draw_sun(ax, x, y, s=s, transform=transform, z=z)
    elif kind in ("rain", "yomgir", "jala"):
        draw_rain(ax, x, y, s=s, transform=transform, z=z)
    elif kind in ("storm", "momaqaldiroq", "dol"):
        draw_storm(ax, x, y, s=s, transform=transform, z=z)
    else:
        draw_cloud(ax, x, y, s=s, transform=transform, z=z)


# === ASOSIY RENDER FUNKSIYASI ===
def render_pro_forecast(day_data, output_path, dpi=200):
    """
    Professional 4-blokli prognoz rasmini yaratadi.

    day_data = {
        "date": "2026-06-17",
        "day_index": 0,
        "cities": {"Toshkent": {"temp_min":22,"temp_max":35,"weather":"ochiq","wind":5,"precip":0}, ...},
        "comment": "Tog' hududlarida sel xavfi"
    }
    """
    if not HAS_GEOPANDAS:
        raise ImportError("geopandas o'rnatilmagan")

    # GeoJSON yuklab olish
    geojson_path = download_geojson()
    if not geojson_path or not geojson_path.exists():
        raise FileNotFoundError("GeoJSON topilmadi")

    gdf = gpd.read_file(str(geojson_path))
    cities_data = day_data.get("cities", {})
    comment = day_data.get("comment", "")
    date_str = day_data.get("date", "")

    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        dt = datetime.now()
    date_label = f"{dt.day} {MONTHS_UZ[dt.month-1]} {dt.year}, {DAYS_UZ[dt.weekday()]}"

    # Viloyatlarni shahar ma'lumotlari bilan bog'lash
    def get_city_data_for_region(region_name):
        for city, info in cities_data.items():
            if find_region_match(region_name, city):
                return city, info
        return None, None

    # Rang berish
    fill_colors = []
    for _, row in gdf.iterrows():
        name = row.get("name") or row.get("NAME_1") or ""
        city, info = get_city_data_for_region(name)
        if info and info.get("temp_max") is not None:
            fill_colors.append(temp_to_color(info["temp_max"]))
        else:
            fill_colors.append("#EEEEEE")
    gdf["fill_color"] = fill_colors

    # EPSG:3857 ga aylantirish
    gdf_plot = gdf.to_crs(epsg=3857)
    gdf_plot["centroid"] = gdf_plot.geometry.representative_point()
    minx, miny, maxx, maxy = gdf_plot.total_bounds

    # === FIGURE ===
    fig = plt.figure(figsize=(14, 9), facecolor="white")

    # --- HEADER ---
    fig.text(0.50, 0.96, "QISQA MUDDATLI OB-HAVO PROGNOZI",
             ha="center", fontsize=18, fontweight="bold", color="#0B3D8F", zorder=30)
    fig.text(0.50, 0.93, date_label,
             ha="center", fontsize=10, color="#455A64", zorder=30)
    fig.text(0.92, 0.96, "O'ZGIDROMET", ha="right",
             fontsize=12, fontweight="bold", color="#0B3D8F", zorder=30)
    fig.text(0.92, 0.93, "hydromet.uz", ha="right",
             fontsize=8, color="#78909C", zorder=30)

    # === 1-BLOK: HARORAT XARITASI ===
    ax1 = fig.add_axes([0.03, 0.45, 0.46, 0.44], zorder=10)
    ax1.set_title("HARORAT XARITASI", fontsize=11, fontweight="bold",
                  color="#0B3D8F", pad=8)

    gdf_plot.plot(ax=ax1, color=gdf_plot["fill_color"],
                  edgecolor="white", linewidth=0.8)
    gdf_plot.boundary.plot(ax=ax1, color="#0B4EA2", linewidth=0.4)

    # Harorat yozuvlari
    for _, row in gdf_plot.iterrows():
        name = row.get("name") or row.get("NAME_1") or ""
        city, info = get_city_data_for_region(name)
        if not info or info.get("temp_max") is None:
            continue
        pt = row["centroid"]
        x, y = pt.x, pt.y
        tmax = info["temp_max"]
        tmin = info.get("temp_min")
        t_str = f"{tmin}\u00b0\u2013{tmax}\u00b0" if tmin else f"{tmax}\u00b0"

        ax1.text(x, y - 15000, t_str, ha="center", va="center",
                 fontsize=7, fontweight="bold", color="#0B3D91",
                 path_effects=[pe.withStroke(linewidth=2, foreground="white")],
                 zorder=130)

        # Ob-havo icon
        weather = info.get("weather", "ochiq")
        put_icon(ax1, weather, x, y + 18000, s=0.35)

    ax1.set_xlim(minx - 40000, maxx + 40000)
    ax1.set_ylim(miny - 50000, maxy + 50000)
    ax1.axis("off")

    # Colorbar
    cmap = ListedColormap(TEMP_COLORS)
    norm = BoundaryNorm(TEMP_LEVELS, ncolors=cmap.N, clip=True)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cax = fig.add_axes([0.10, 0.44, 0.30, 0.012], zorder=50)
    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal",
                        boundaries=TEMP_LEVELS, ticks=TEMP_LEVELS)
    cbar.ax.tick_params(labelsize=6)
    cbar.set_label("Harorat, \u00b0C", fontsize=7)

    # === 2-BLOK: SHAMOL ===
    ax2 = fig.add_axes([0.52, 0.45, 0.46, 0.44], zorder=10)
    ax2.set_title("SHAMOL VA YOG\u2018INGARCHILIK", fontsize=11,
                  fontweight="bold", color="#0B3D8F", pad=8)

    gdf_plot.plot(ax=ax2, color="#EEF7E9", edgecolor="#9AB7A7", linewidth=0.7)

    # Yomg'irli viloyatlarni ajratib ko'rsatish
    for _, row in gdf_plot.iterrows():
        name = row.get("name") or row.get("NAME_1") or ""
        city, info = get_city_data_for_region(name)
        if info and info.get("precip") and info["precip"] > 0:
            gpd.GeoDataFrame([row], crs=gdf_plot.crs).plot(
                ax=ax2, color="#9BD8FF", alpha=0.7,
                edgecolor="#4A9BC7", linewidth=0.6)

    # Shamol ko'rsatkichlari
    for _, row in gdf_plot.iterrows():
        name = row.get("name") or row.get("NAME_1") or ""
        city, info = get_city_data_for_region(name)
        if not info:
            continue
        pt = row["centroid"]
        x, y = pt.x, pt.y
        wind = info.get("wind", 0)
        if wind and wind >= 5:
            ax2.text(x, y, f"{wind} m/s", ha="center", va="center",
                     fontsize=6, color="#0B4EA2", fontweight="bold",
                     path_effects=[pe.withStroke(linewidth=1.5, foreground="white")],
                     zorder=100)

    ax2.set_xlim(minx - 40000, maxx + 40000)
    ax2.set_ylim(miny - 50000, maxy + 50000)
    ax2.axis("off")

    # === 3-BLOK: OGOHLANTIRISH ===
    ax3 = fig.add_axes([0.03, 0.05, 0.46, 0.35], zorder=10)
    ax3.axis("off")
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)

    ax3.text(0.5, 0.95, "MUHIM OGOHLANTIRISH", ha="center",
             fontsize=11, fontweight="bold", color="#0B3D8F",
             transform=ax3.transAxes)

    # Alert box
    if comment:
        ax3.add_patch(FancyBboxPatch(
            (0.02, 0.30), 0.96, 0.55, transform=ax3.transAxes,
            boxstyle="round,pad=0.02", facecolor="#FCEBEB",
            edgecolor="#F09595", linewidth=1.2, zorder=5))
        ax3.text(0.06, 0.75, "\u26a0 DIQQAT!", transform=ax3.transAxes,
                 fontsize=13, fontweight="bold", color="#B71C1C", zorder=10)
        ax3.text(0.06, 0.45, comment, transform=ax3.transAxes,
                 fontsize=9, color="#791F1F", wrap=True, zorder=10)
    else:
        ax3.add_patch(FancyBboxPatch(
            (0.02, 0.30), 0.96, 0.55, transform=ax3.transAxes,
            boxstyle="round,pad=0.02", facecolor="#E6F1FB",
            edgecolor="#85B7EB", linewidth=1, zorder=5))
        ax3.text(0.06, 0.60, "Hozircha muhim ogohlantirishlar yo\u2018q",
                 transform=ax3.transAxes, fontsize=10, color="#0C447C", zorder=10)

    # Issiqlik ogohlantirishlari
    hot_cities = [c for c, info in cities_data.items()
                  if info and info.get("temp_max") and info["temp_max"] >= 40]
    if hot_cities:
        ax3.text(0.06, 0.20, f"\ud83d\udd25 Issiqlik xavfi: {', '.join(hot_cities)}",
                 transform=ax3.transAxes, fontsize=8, color="#B71C1C", zorder=10)

    # === 4-BLOK: VILOYATLAR JADVALI ===
    ax4 = fig.add_axes([0.52, 0.05, 0.46, 0.35], zorder=10)
    ax4.axis("off")
    ax4.set_xlim(0, 1)
    ax4.set_ylim(0, 1)

    ax4.text(0.5, 0.95, "VILOYATLAR BO\u2018YICHA PROGNOZ", ha="center",
             fontsize=11, fontweight="bold", color="#0B3D8F",
             transform=ax4.transAxes)

    # Jadval
    cols = [0.02, 0.40, 0.60, 0.80]
    ax4.text(cols[0], 0.88, "Hudud", transform=ax4.transAxes,
             fontsize=7, fontweight="bold", color="#0B3D8F")
    ax4.text(cols[1], 0.88, "Kechasi", transform=ax4.transAxes,
             fontsize=7, fontweight="bold", color="#0B3D8F")
    ax4.text(cols[2], 0.88, "Kunduzi", transform=ax4.transAxes,
             fontsize=7, fontweight="bold", color="#0B3D8F")
    ax4.text(cols[3], 0.88, "Holat", transform=ax4.transAxes,
             fontsize=7, fontweight="bold", color="#0B3D8F")

    sorted_cities = sorted(cities_data.items(),
                           key=lambda x: x[1].get("temp_max", 0) if x[1] else 0,
                           reverse=True)

    y0 = 0.82
    row_h = 0.058
    for i, (city, info) in enumerate(sorted_cities[:13]):
        if not info or info.get("temp_max") is None:
            continue
        y = y0 - i * row_h
        if y < 0.05:
            break

        # Zebra fon
        if i % 2 == 0:
            ax4.add_patch(Rectangle((0.01, y-0.02), 0.98, row_h,
                                    transform=ax4.transAxes,
                                    facecolor="#F6FBFF", edgecolor="none", zorder=1))

        tmax = info["temp_max"]
        tmin = info.get("temp_min")
        weather = info.get("weather", "ochiq")

        ax4.text(cols[0], y, city, transform=ax4.transAxes,
                 fontsize=7, color="#1A2332", fontweight="bold", va="center", zorder=3)
        ax4.text(cols[1], y, f"{tmin}\u00b0" if tmin else "\u2014",
                 transform=ax4.transAxes, fontsize=7, color="#1565C0", va="center", zorder=3)
        ax4.text(cols[2], y, f"{tmax}\u00b0", transform=ax4.transAxes,
                 fontsize=7, color="#C22A00", fontweight="bold", va="center", zorder=3)

        # Ob-havo icon
        put_icon(ax4, weather, cols[3]+0.06, y, s=0.20,
                 transform=ax4.transAxes, z=90)

    # === FOOTER ===
    fig.text(0.03, 0.01, f"\u00a9 {dt.year} Gidrometeorologiya xizmati agentligi",
             fontsize=7, color="#78909C")
    fig.text(0.97, 0.01, "@uzgidromet  |  hydromet.uz",
             fontsize=7, color="#78909C", ha="right")

    # === SAQLASH ===
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", pad_inches=0.05)
    plt.close(fig)
    return output_path
