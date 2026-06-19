"""
Gidrometeorologiya xizmati — Professional prognoz xaritasi.
Toza, oqilona dizayn — sinoptik xarita standarti.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch
from datetime import datetime, timedelta

# Koordinatalar
CITY_COORDS = {
    "Toshkent":   (41.30, 69.24),
    "Samarqand":  (39.65, 66.96),
    "Buxoro":     (39.77, 64.43),
    "Namangan":   (41.00, 71.67),
    "Andijon":    (40.78, 72.34),
    "Farg'ona":   (40.38, 71.79),
    "Qarshi":     (38.86, 65.80),
    "Nukus":      (42.46, 59.60),
    "Navoiy":     (40.10, 65.38),
    "Termiz":     (37.22, 67.28),
    "Jizzax":     (40.12, 67.84),
    "Urganch":    (41.55, 60.63),
    "Guliston":   (40.49, 68.78),
    "Shahrisabz": (39.06, 66.83),
}

WEATHER_SYMBOLS = {
    "ochiq": "\u2600", "qisman_bulutli": "\u26c5",
    "bulutli": "\u2601", "tuman": "\u2592",
    "yomgir": "\U0001f327", "jala": "\u26c6",
    "momaqaldiroq": "\u26c8", "qor": "\u2744",
    "dol": "\U0001f328", "chang_boroni": "\u224b",
    "qor_boroni": "\u2745",
}

MONTHS = ["yanvar","fevral","mart","aprel","may","iyun",
          "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_W = ["dushanba","seshanba","chorshanba",
          "payshanba","juma","shanba","yakshanba"]



def render_forecast_map(day_data, output_path, dpi=150):
    """Professional prognoz xaritasini PNG sifatida yaratadi."""
    cities_data = day_data.get("cities", {})
    comment = day_data.get("comment", "")
    date_str = day_data.get("date", "")
    day_index = day_data.get("day_index", 0)

    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        dt = datetime.now() + timedelta(days=day_index)

    day_labels = ["I KUN", "II KUN", "III KUN"]
    title_label = day_labels[day_index] if day_index < 3 else ""
    date_label = f"{dt.day} {MONTHS[dt.month-1]} {dt.year}, {DAYS_W[dt.weekday()]}"

    # === FIGURE ===
    fig = plt.figure(figsize=(14, 10), facecolor="white")
    ax = fig.add_axes([0.03, 0.08, 0.94, 0.78])
    ax.set_facecolor("#f0f4f8")
    ax.set_xlim(55.5, 74.0)
    ax.set_ylim(36.5, 46.0)
    ax.set_aspect("equal")

    # Grid chiziqlari
    for lon in range(56, 74, 2):
        ax.axvline(lon, color="#d0d8e0", lw=0.3, zorder=0)
    for lat in range(37, 46):
        ax.axhline(lat, color="#d0d8e0", lw=0.3, zorder=0)

    # Koordinata belgilari
    ax.set_xticks(range(56, 74, 2))
    ax.set_yticks(range(37, 46))
    ax.tick_params(labelsize=7, colors="#8899aa", length=0)
    ax.set_xticklabels([f"{x}\u00b0E" for x in range(56, 74, 2)], fontsize=7, color="#8899aa")
    ax.set_yticklabels([f"{y}\u00b0N" for y in range(37, 46)], fontsize=7, color="#8899aa")

    for spine in ax.spines.values():
        spine.set_color("#bcc8d4")
        spine.set_linewidth(0.5)


    # === SHAHAR MARKERLARI ===
    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        tmax = info.get("temp_max")
        if tmax is None:
            continue
        tmin = info.get("temp_min")
        lat, lon = CITY_COORDS[name]
        wind = info.get("wind", 0)
        precip = info.get("precip", 0)
        weather = info.get("weather", "ochiq")
        symbol = WEATHER_SYMBOLS.get(weather, "\u2022")

        # Rang
        if tmax >= 40: clr = "#d32f2f"
        elif tmax >= 35: clr = "#f57c00"
        elif tmax >= 28: clr = "#f9a825"
        elif tmax >= 18: clr = "#388e3c"
        elif tmax >= 5: clr = "#1976d2"
        else: clr = "#5c6bc0"

        # Marker doira
        ax.plot(lon, lat, "o", color=clr, ms=10,
                mec="white", mew=2, zorder=20)

        # Harorat matni
        tmin_s = f"{tmin}\u00b0/" if tmin is not None else ""
        temp_label = f"{tmin_s}{tmax}\u00b0C"

        ax.annotate(name, (lon, lat),
                   xytext=(0, 14), textcoords="offset points",
                   fontsize=9, fontweight="bold", color="#1a2744",
                   ha="center", va="bottom", zorder=21)

        ax.annotate(temp_label, (lon, lat),
                   xytext=(0, -14), textcoords="offset points",
                   fontsize=9, fontweight="bold", color=clr,
                   ha="center", va="top", zorder=21)

        # Ob-havo belgisi
        ax.annotate(symbol, (lon, lat),
                   xytext=(16, 0), textcoords="offset points",
                   fontsize=12, ha="left", va="center", zorder=21)


    # === SARLAVHA ===
    fig.text(0.5, 0.95,
             "GIDROMETEOROLOGIYA XIZMATI AGENTLIGI",
             fontsize=15, fontweight="bold", color="#1a2744",
             ha="center", va="top")
    fig.text(0.5, 0.915,
             f"Qisqa muddatli ob-havo prognozi  \u2022  {title_label}  \u2022  {date_label}",
             fontsize=10, color="#4a6580", ha="center", va="top")

    # === IZOH (pastda) ===
    if comment:
        fig.text(0.5, 0.035, comment,
                fontsize=9, color="#3d5068", ha="center", va="bottom",
                style="italic", wrap=True,
                bbox=dict(boxstyle="round,pad=0.4", fc="#e8eef4",
                         ec="#bcc8d4", alpha=0.9))

    # === LEGEND ===
    legend_items = [
        mpatches.Patch(fc="#d32f2f", label="40\u00b0C va yuqori"),
        mpatches.Patch(fc="#f57c00", label="35\u201340\u00b0C"),
        mpatches.Patch(fc="#f9a825", label="28\u201335\u00b0C"),
        mpatches.Patch(fc="#388e3c", label="18\u201328\u00b0C"),
        mpatches.Patch(fc="#1976d2", label="5\u201318\u00b0C"),
        mpatches.Patch(fc="#5c6bc0", label="5\u00b0C dan past"),
    ]
    leg = ax.legend(handles=legend_items, loc="lower left",
                   fontsize=7.5, framealpha=0.9,
                   edgecolor="#bcc8d4", title="Harorat",
                   title_fontsize=8)

    # === MANBA ===
    fig.text(0.97, 0.01, "hydromet.uz", fontsize=7,
            color="#8899aa", ha="right", va="bottom")

    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
