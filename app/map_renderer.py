"""
Gidrometeorologiya xizmati — Professional kartografik prognoz generatori.
Cartopy + Natural Earth ma'lumotlari = haqiqiy xarita.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# === SHAHARLAR ===
CITY_COORDS = {
    "Toshkent":   (41.30, 69.24),
    "Samarqand":  (39.65, 66.96),
    "Buxoro":     (39.77, 64.43),
    "Namangan":   (41.00, 71.67),
    "Andijon":    (40.78, 72.34),
    "Farg\u2018ona": (40.38, 71.79),
    "Qarshi":     (38.86, 65.80),
    "Nukus":      (42.46, 59.60),
    "Navoiy":     (40.10, 65.38),
    "Termiz":     (37.22, 67.28),
    "Jizzax":     (40.12, 67.84),
    "Urganch":    (41.55, 60.63),
    "Guliston":   (40.49, 68.78),
    "Shahrisabz": (39.06, 66.83),
}


# Poytaxt alohida
CAPITAL = "Toshkent"

WEATHER_LABELS = {
    "ochiq": "Ochiq",
    "qisman_bulutli": "Qis.bulutli",
    "bulutli": "Bulutli",
    "tuman": "Tuman",
    "yomgir": "Yomg\u2018ir",
    "jala": "Jala",
    "momaqaldiroq": "Momaq.",
    "qor": "Qor",
    "dol": "Do\u2018l",
    "chang_boroni": "Ch.bo\u2018roni",
    "qor_boroni": "Q.bo\u2018roni",
}

MONTHS = ["yanvar","fevral","mart","aprel","may","iyun",
          "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_W = ["dushanba","seshanba","chorshanba",
          "payshanba","juma","shanba","yakshanba"]


def get_temp_color(t):
    if t >= 42: return "#880e4f"
    if t >= 38: return "#b71c1c"
    if t >= 34: return "#d84315"
    if t >= 30: return "#e65100"
    if t >= 26: return "#f57f17"
    if t >= 22: return "#827717"
    if t >= 18: return "#33691e"
    if t >= 12: return "#006064"
    if t >= 5:  return "#0d47a1"
    if t >= 0:  return "#1a237e"
    return "#311b92"



def render_forecast_map(day_data, output_path, dpi=150):
    """Professional kompozit prognoz rasmi: xarita + jadval."""
    cities_data = day_data.get("cities", {})
    comment = day_data.get("comment", "")
    date_str = day_data.get("date", "")
    day_index = day_data.get("day_index", 0)

    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        dt = datetime.now() + timedelta(days=day_index)

    day_labels = ["I kun", "II kun", "III kun"]
    title_label = day_labels[day_index] if day_index < 3 else ""
    date_label = f"{dt.day} {MONTHS[dt.month-1]} {dt.year}, {DAYS_W[dt.weekday()]}"

    # ============ FIGURE ============
    fig = plt.figure(figsize=(16, 10.5), facecolor="white")

    # --- HEADER ---
    fig.text(0.50, 0.965,
        "GIDROMETEOROLOGIYA XIZMATI AGENTLIGI",
        fontsize=14, fontweight="bold", color="#0d2137",
        ha="center", va="top",
        fontfamily="sans-serif")
    fig.text(0.50, 0.935,
        f"Qisqa muddatli ob-havo prognozi  \u2014  {title_label}  \u2014  {date_label}",
        fontsize=10, color="#455a64", ha="center", va="top")

    # Chiziq
    line_ax = fig.add_axes([0.03, 0.925, 0.94, 0.002])
    line_ax.set_facecolor("#1976d2")
    line_ax.axis("off")


    # --- XARITA (cartopy) ---
    proj = ccrs.PlateCarree()
    map_ax = fig.add_axes([0.01, 0.10, 0.62, 0.80], projection=proj)
    map_ax.set_extent([56.0, 73.5, 36.5, 45.8], crs=proj)

    # Natural Earth xususiyatlari
    map_ax.add_feature(cfeature.LAND, facecolor="#f5f0e8", zorder=0)
    map_ax.add_feature(cfeature.OCEAN, facecolor="#dce9f5", zorder=0)
    map_ax.add_feature(cfeature.LAKES, facecolor="#c4ddf0",
                       edgecolor="#7ba7cc", linewidth=0.4, zorder=1)
    map_ax.add_feature(cfeature.RIVERS, edgecolor="#7ba7cc",
                       linewidth=0.4, zorder=1)
    map_ax.add_feature(cfeature.BORDERS, linewidth=1.4,
                       edgecolor="#37474f", linestyle="-", zorder=3)

    # Gridlines
    gl = map_ax.gridlines(draw_labels=True, linewidth=0.3,
                          color="#b0bec5", alpha=0.6,
                          linestyle="--", zorder=2)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 7, "color": "#607d8b"}
    gl.ylabel_style = {"size": 7, "color": "#607d8b"}

    # --- SHAHAR MARKERLARI ---
    stroke = [pe.withStroke(linewidth=3, foreground="white")]

    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        tmax = info.get("temp_max")
        if tmax is None:
            continue
        tmin = info.get("temp_min")
        lat, lon = CITY_COORDS[name]
        clr = get_temp_color(tmax)
        is_capital = (name == CAPITAL)

        # Marker
        ms = 10 if is_capital else 7
        map_ax.plot(lon, lat, "o", color=clr, ms=ms,
                    mec="white", mew=1.5, zorder=20,
                    transform=proj)

        # Nom
        fs = 9 if is_capital else 8
        fw = "bold" if is_capital else "medium"
        map_ax.annotate(name, (lon, lat),
            xytext=(0, 10), textcoords="offset points",
            fontsize=fs, fontweight=fw, color="#263238",
            ha="center", va="bottom", zorder=22,
            path_effects=stroke,
            xycoords=proj._as_mpl_transform(map_ax))

        # Harorat
        if tmin is not None:
            t_str = f"{tmin}\u00b0\u2013{tmax}\u00b0"
        else:
            t_str = f"{tmax}\u00b0"
        map_ax.annotate(t_str, (lon, lat),
            xytext=(0, -10), textcoords="offset points",
            fontsize=8, fontweight="bold", color=clr,
            ha="center", va="top", zorder=22,
            path_effects=stroke,
            xycoords=proj._as_mpl_transform(map_ax))


    # --- JADVAL (o'ng panel) ---
    tbl_ax = fig.add_axes([0.64, 0.10, 0.35, 0.80])
    tbl_ax.set_xlim(0, 1)
    tbl_ax.set_ylim(0, 1)
    tbl_ax.axis("off")

    # Jadval sarlavha
    tbl_ax.text(0.5, 0.97, "Viloyat markazlari",
        fontsize=11, fontweight="bold", color="#0d2137",
        ha="center", va="top")

    # Ustun sarlavhalari
    y = 0.92
    tbl_ax.text(0.02, y, "Shahar", fontsize=8, fontweight="bold", color="#455a64")
    tbl_ax.text(0.42, y, "T, \u00b0C", fontsize=8, fontweight="bold", color="#455a64")
    tbl_ax.text(0.65, y, "m/s", fontsize=8, fontweight="bold", color="#455a64")
    tbl_ax.text(0.80, y, "Hodisa", fontsize=8, fontweight="bold", color="#455a64")
    tbl_ax.axhline(y=y - 0.012, xmin=0.01, xmax=0.99, color="#b0bec5", lw=0.8)

    # Satrlar (harorat bo'yicha tartiblangan)
    sorted_cities = sorted(
        [(n, d) for n, d in cities_data.items() if d and d.get("temp_max") is not None],
        key=lambda x: x[1]["temp_max"], reverse=True)

    row_y = y - 0.05
    row_h = 0.055

    for name, info in sorted_cities:
        if row_y < 0.04:
            break
        tmax = info["temp_max"]
        tmin = info.get("temp_min")
        wind = info.get("wind")
        weather = info.get("weather", "ochiq")
        clr = get_temp_color(tmax)
        w_label = WEATHER_LABELS.get(weather, "")

        # Rang chizig'i
        tbl_ax.plot(0.0, row_y, "s", color=clr, ms=6, mec="none",
                   transform=tbl_ax.transAxes, clip_on=False)

        # Shahar
        tbl_ax.text(0.02, row_y, name, fontsize=8.5, color="#263238",
                   va="center")

        # Harorat
        if tmin is not None:
            t_str = f"{tmin}\u00b0\u2013{tmax}\u00b0"
        else:
            t_str = f"{tmax}\u00b0"
        tbl_ax.text(0.42, row_y, t_str, fontsize=8.5, color=clr,
                   va="center", fontweight="bold")

        # Shamol
        if wind:
            tbl_ax.text(0.65, row_y, str(wind), fontsize=8,
                       color="#546e7a", va="center")

        # Hodisa
        tbl_ax.text(0.80, row_y, w_label, fontsize=7.5,
                   color="#546e7a", va="center")

        row_y -= row_h

    # --- FOOTER ---
    if comment:
        fig.text(0.50, 0.055, comment,
            fontsize=9, color="#37474f", ha="center", va="center",
            style="italic", wrap=True,
            bbox=dict(boxstyle="round,pad=0.3", fc="#eceff1", ec="#b0bec5"))

    fig.text(0.50, 0.015,
        "hydromet.uz   \u2022   t.me/uzhydromet   \u2022   facebook.com/uzhydromet",
        fontsize=8, color="#78909c", ha="center", va="center")

    # === SAQLASH ===
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none",
                pad_inches=0.1)
    plt.close()
