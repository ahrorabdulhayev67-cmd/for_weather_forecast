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



def render_forecast_map(day_data, output_path, dpi=180):
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
    shadow = [pe.withStroke(linewidth=4, foreground="white")]

    # Yog'ingarchilik zonalari (avval chiziladi — markerlar ostida)
    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        precip = info.get("precip", 0)
        if precip and precip > 0:
            lat, lon = CITY_COORDS[name]
            radius = min(0.3 + precip * 0.05, 1.2)
            circle = plt.Circle((lon, lat), radius,
                fc="#64b5f6", alpha=0.15, ec="none",
                transform=proj, zorder=8)
            map_ax.add_patch(circle)

    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        tmax = info.get("temp_max")
        if tmax is None:
            continue
        tmin = info.get("temp_min")
        lat, lon = CITY_COORDS[name]
        wind = info.get("wind", 0)
        weather = info.get("weather", "ochiq")
        clr = get_temp_color(tmax)
        is_capital = (name == CAPITAL)

        # Shamol strelkasi
        if wind and wind > 2:
            arrow_len = min(wind * 0.04, 0.4)
            map_ax.annotate("", xy=(lon + arrow_len, lat),
                xytext=(lon, lat),
                arrowprops=dict(arrowstyle="->", color="#546e7a",
                               lw=1.2, mutation_scale=10),
                transform=proj, zorder=15)

        # Marker — ob-havo hodisasiga qarab shakl
        ms = 11 if is_capital else 8
        marker_shape = "o"
        if weather in ("yomgir", "jala", "momaqaldiroq"):
            marker_shape = "D"  # romb — yog'ingarchilik
        elif weather in ("qor", "qor_boroni", "dol"):
            marker_shape = "^"  # uchburchak — qor/do'l

        map_ax.plot(lon, lat, marker_shape, color=clr, ms=ms,
                    mec="white", mew=2, zorder=20,
                    transform=proj)

        # Nom
        fs = 9.5 if is_capital else 8
        fw = "bold"
        map_ax.annotate(name, (lon, lat),
            xytext=(0, 12), textcoords="offset points",
            fontsize=fs, fontweight=fw, color="#1a2744",
            ha="center", va="bottom", zorder=22,
            path_effects=shadow,
            xycoords=proj._as_mpl_transform(map_ax))

        # Harorat
        if tmin is not None:
            t_str = f"{tmin}\u00b0\u2013{tmax}\u00b0"
        else:
            t_str = f"{tmax}\u00b0"
        map_ax.annotate(t_str, (lon, lat),
            xytext=(0, -12), textcoords="offset points",
            fontsize=8.5, fontweight="bold", color=clr,
            ha="center", va="top", zorder=22,
            path_effects=stroke,
            xycoords=proj._as_mpl_transform(map_ax))

    # Legend (xarita ichida)
    legend_items = [
        mpatches.Patch(fc="#b71c1c", label="38\u00b0C+"),
        mpatches.Patch(fc="#e65100", label="30\u201338\u00b0"),
        mpatches.Patch(fc="#f57f17", label="22\u201330\u00b0"),
        mpatches.Patch(fc="#33691e", label="12\u201322\u00b0"),
        mpatches.Patch(fc="#0d47a1", label="<12\u00b0"),
    ]
    map_ax.legend(handles=legend_items, loc="lower left",
        fontsize=7, framealpha=0.92, edgecolor="#b0bec5",
        title="T\u00b0C", title_fontsize=7.5, fancybox=True)


    # --- JADVAL (o'ng panel) ---
    tbl_ax = fig.add_axes([0.64, 0.10, 0.35, 0.80])
    tbl_ax.set_xlim(0, 1)
    tbl_ax.set_ylim(0, 1)
    tbl_ax.axis("off")

    # Vertikal ajratuvchi chiziq
    sep_ax = fig.add_axes([0.632, 0.10, 0.001, 0.80])
    sep_ax.set_facecolor("#cfd8dc")
    sep_ax.axis("off")

    # Jadval sarlavha
    tbl_ax.text(0.5, 0.97, "Viloyat markazlari bo\u2018yicha",
        fontsize=10, fontweight="bold", color="#0d2137",
        ha="center", va="top")

    # Ustun sarlavhalari
    y = 0.92
    cols = [0.01, 0.35, 0.55, 0.72, 0.88]
    tbl_ax.text(cols[0], y, "Shahar", fontsize=7.5, fontweight="bold", color="#455a64")
    tbl_ax.text(cols[1], y, "T, \u00b0C", fontsize=7.5, fontweight="bold", color="#455a64")
    tbl_ax.text(cols[2], y, "m/s", fontsize=7.5, fontweight="bold", color="#455a64")
    tbl_ax.text(cols[3], y, "mm", fontsize=7.5, fontweight="bold", color="#455a64")
    tbl_ax.text(cols[4], y, "Hodisa", fontsize=7.5, fontweight="bold", color="#455a64")
    tbl_ax.axhline(y=y - 0.012, xmin=0.0, xmax=1.0, color="#b0bec5", lw=0.8)

    # Satrlar (harorat bo'yicha tartiblangan)
    sorted_cities = sorted(
        [(n, d) for n, d in cities_data.items() if d and d.get("temp_max") is not None],
        key=lambda x: x[1]["temp_max"], reverse=True)

    row_y = y - 0.05
    row_h = 0.055

    for idx, (name, info) in enumerate(sorted_cities):
        if row_y < 0.04:
            break
        tmax = info["temp_max"]
        tmin = info.get("temp_min")
        wind = info.get("wind")
        precip = info.get("precip", 0)
        weather = info.get("weather", "ochiq")
        clr = get_temp_color(tmax)
        w_label = WEATHER_LABELS.get(weather, "")

        # Chap rang chizig'i (mini bar)
        bar_width = min(tmax / 50.0 * 0.28, 0.28) if tmax > 0 else 0.02
        tbl_ax.barh(row_y, bar_width, height=0.022, left=cols[1] - 0.02,
                   color=clr, alpha=0.15, zorder=0)

        # Shahar
        tbl_ax.text(cols[0], row_y, name, fontsize=8, color="#263238",
                   va="center", fontweight="medium")

        # Harorat
        if tmin is not None:
            t_str = f"{tmin}\u00b0\u2013{tmax}\u00b0"
        else:
            t_str = f"{tmax}\u00b0"
        tbl_ax.text(cols[1], row_y, t_str, fontsize=8.5, color=clr,
                   va="center", fontweight="bold")

        # Shamol
        if wind:
            tbl_ax.text(cols[2], row_y, str(wind), fontsize=8,
                       color="#546e7a", va="center")

        # Yog'ingarchilik
        if precip and precip > 0:
            tbl_ax.text(cols[3], row_y, f"{precip}", fontsize=8,
                       color="#1565c0", va="center", fontweight="bold")

        # Hodisa
        tbl_ax.text(cols[4], row_y, w_label, fontsize=7,
                   color="#546e7a", va="center")

        # Ajratuvchi chiziq (har 2-satr)
        if idx % 2 == 1:
            tbl_ax.axhline(y=row_y - row_h / 2, xmin=0, xmax=1,
                          color="#eceff1", lw=0.5)

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
