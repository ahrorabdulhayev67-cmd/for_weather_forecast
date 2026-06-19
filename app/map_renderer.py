"""
Gidrometeorologiya xizmati agentligi
Qisqa muddatli ob-havo prognozi — professional kompozit rasm generatori.

Natija: PNG rasm (1600x1100 px) quyidagi tarkibda:
  ┌────────────────────────────────────────────┐
  │  HEADER: sarlavha + sana                   │
  ├──────────────────────┬─────────────────────┤
  │                      │                     │
  │   XARITA (chap)      │  JADVAL (o'ng)      │
  │   Chegaralar,        │  Shahar | T | Hodisa│
  │   markerlar,         │                     │
  │   ob-havo belgilari  │                     │
  │                      │                     │
  ├──────────────────────┴─────────────────────┤
  │  FOOTER: izoh + ijtimoiy tarmoq linklari   │
  └────────────────────────────────────────────┘
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch
from matplotlib import font_manager
from datetime import datetime, timedelta

# === KONFIGURATSIYA ===
COLORS = {
    "bg":       "#ffffff",
    "header":   "#0d2137",
    "accent":   "#1976d2",
    "text":     "#1a2744",
    "muted":    "#5a7085",
    "border":   "#c5d1dc",
    "grid":     "#e4eaf0",
    "land":     "#f5f8fb",
    "land_fill":"#eaf2f8",
    "footer":   "#0d2137",
}

TEMP_COLORS = {
    45: "#7b1fa2", 40: "#c62828", 35: "#e65100",
    30: "#f57f17", 25: "#9e9d24", 20: "#2e7d32",
    15: "#00838f", 10: "#1565c0", 0: "#283593",
}


def get_temp_color(t):
    """Haroratga mos professional rang."""
    if t >= 42: return "#7b1fa2"
    if t >= 38: return "#c62828"
    if t >= 34: return "#e65100"
    if t >= 30: return "#ef6c00"
    if t >= 26: return "#f9a825"
    if t >= 22: return "#9e9d24"
    if t >= 18: return "#2e7d32"
    if t >= 12: return "#00838f"
    if t >= 5:  return "#1565c0"
    return "#283593"


# O'zbekiston davlat chegarasi (soddalashtirilgan, ~55 nuqta)
UZB_BORDER = np.array([
    [55.97,41.32],[57.02,41.26],[57.10,41.22],[58.16,42.18],
    [58.60,42.56],[59.46,42.30],[59.86,42.10],[60.07,41.81],
    [60.47,41.86],[60.93,41.87],[61.55,41.27],[61.88,41.09],
    [62.49,39.95],[63.52,39.36],[64.17,38.95],[65.22,38.40],
    [66.54,38.01],[66.71,37.67],[67.07,37.36],[67.33,37.21],
    [67.72,37.23],[68.07,36.95],[68.61,37.34],[68.87,37.34],
    [69.30,37.12],[69.52,37.60],[70.14,37.60],[70.56,38.00],
    [70.49,38.42],[70.76,38.46],[71.05,38.42],[71.28,38.61],
    [70.95,39.00],[70.63,39.11],[69.37,39.53],[69.17,39.66],
    [68.57,39.56],[67.78,39.65],[67.44,39.48],[68.18,40.09],
    [68.63,40.18],[69.01,40.09],[69.07,40.67],[68.44,40.60],
    [68.64,40.85],[69.55,40.73],[69.98,40.85],[70.45,40.05],
    [70.67,40.08],[70.97,40.24],[71.77,40.15],[73.06,40.80],
    [71.77,42.17],[60.17,44.06],[58.60,45.57],[56.00,45.00],
    [55.97,41.32]
])

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

WEATHER_LABELS = {
    "ochiq": ("Ochiq", "\u2600\ufe0f"),
    "qisman_bulutli": ("Qisman bulutli", "\u26c5"),
    "bulutli": ("Bulutli", "\u2601\ufe0f"),
    "tuman": ("Tuman", "\U0001f32b\ufe0f"),
    "yomgir": ("Yomg\u2018ir", "\U0001f327\ufe0f"),
    "jala": ("Jala", "\U0001f326\ufe0f"),
    "momaqaldiroq": ("Momaqaldiroq", "\u26c8\ufe0f"),
    "qor": ("Qor", "\u2744\ufe0f"),
    "dol": ("Do\u2018l", "\U0001f328\ufe0f"),
    "chang_boroni": ("Chang bo\u2018roni", "\U0001f4a8"),
    "qor_boroni": ("Qor bo\u2018roni", "\U0001f32c\ufe0f"),
}

MONTHS = ["yanvar","fevral","mart","aprel","may","iyun",
          "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_W = ["dushanba","seshanba","chorshanba",
          "payshanba","juma","shanba","yakshanba"]



def render_forecast_map(day_data, output_path, dpi=150):
    """Kompozit prognoz rasmini yaratadi (xarita + jadval + footer)."""
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

    # === FIGURE (kompozit layout) ===
    fig = plt.figure(figsize=(16, 11), facecolor=COLORS["bg"])

    # --- HEADER ---
    header_ax = fig.add_axes([0, 0.91, 1, 0.09])
    header_ax.set_xlim(0, 1)
    header_ax.set_ylim(0, 1)
    header_ax.set_facecolor(COLORS["header"])
    header_ax.axis("off")

    header_ax.text(0.5, 0.65,
        "GIDROMETEOROLOGIYA XIZMATI AGENTLIGI",
        fontsize=16, fontweight="bold", color="white",
        ha="center", va="center")
    header_ax.text(0.5, 0.25,
        f"Qisqa muddatli ob-havo prognozi  \u2022  {title_label}  \u2022  {date_label}",
        fontsize=10, color="#90b4d4", ha="center", va="center")

    # --- XARITA (chap qism: 60%) ---
    map_ax = fig.add_axes([0.02, 0.12, 0.58, 0.77])
    draw_map(map_ax, cities_data)

    # --- JADVAL (o'ng qism: 38%) ---
    table_ax = fig.add_axes([0.62, 0.12, 0.36, 0.77])
    draw_table(table_ax, cities_data)

    # --- FOOTER ---
    footer_ax = fig.add_axes([0, 0, 1, 0.11])
    footer_ax.set_xlim(0, 1)
    footer_ax.set_ylim(0, 1)
    footer_ax.set_facecolor(COLORS["header"])
    footer_ax.axis("off")

    # Izoh
    if comment:
        footer_ax.text(0.5, 0.70, comment,
            fontsize=9, color="#c5d6e6", ha="center", va="center",
            style="italic", wrap=True)

    # Ijtimoiy tarmoqlar
    footer_ax.text(0.5, 0.22,
        "hydromet.uz  \u2022  t.me/uzhydromet  \u2022  facebook.com/uzhydromet  \u2022  instagram.com/uzhydromet",
        fontsize=8, color="#6a8eaa", ha="center", va="center")

    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor=COLORS["bg"], edgecolor="none")
    plt.close()



def draw_map(ax, cities_data):
    """Xaritani chizadi — chegaralar, markerlar, ob-havo belgilari."""
    ax.set_facecolor(COLORS["grid"])
    ax.set_xlim(55.5, 74.0)
    ax.set_ylim(36.5, 46.0)
    ax.set_aspect("equal")

    # Fon — xarita atrofi (tashqi hudud)
    ax.fill_between([55.5, 74.0], 36.5, 46.0, color="#dce6f0", zorder=0)

    # O'zbekiston hududi
    ax.fill(UZB_BORDER[:, 0], UZB_BORDER[:, 1],
            fc=COLORS["land_fill"], ec="none", zorder=2)
    ax.plot(UZB_BORDER[:, 0], UZB_BORDER[:, 1],
            color=COLORS["header"], lw=2.2, zorder=4, solid_capstyle="round")

    # Grid
    for lon in range(56, 74, 2):
        ax.axvline(lon, color="#c5d1dc", lw=0.3, zorder=1, alpha=0.5)
    for lat in range(37, 46):
        ax.axhline(lat, color="#c5d1dc", lw=0.3, zorder=1, alpha=0.5)

    # Koordinata belgilari
    ax.set_xticks(range(57, 74, 3))
    ax.set_yticks(range(37, 46, 2))
    ax.set_xticklabels([f"{x}\u00b0" for x in range(57, 74, 3)],
                       fontsize=7, color=COLORS["muted"])
    ax.set_yticklabels([f"{y}\u00b0" for y in range(37, 46, 2)],
                       fontsize=7, color=COLORS["muted"])
    ax.tick_params(length=0, pad=3)

    for spine in ax.spines.values():
        spine.set_visible(False)

    # === SHAHARLAR ===
    stroke = [pe.withStroke(linewidth=2.5, foreground="white")]

    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        tmax = info.get("temp_max")
        if tmax is None:
            continue
        tmin = info.get("temp_min")
        lat, lon = CITY_COORDS[name]
        weather = info.get("weather", "ochiq")
        clr = get_temp_color(tmax)

        # Marker
        ax.plot(lon, lat, "o", color=clr, ms=9,
                mec="white", mew=1.8, zorder=20)

        # Nom (tepada)
        ax.annotate(name, (lon, lat),
            xytext=(0, 11), textcoords="offset points",
            fontsize=8, fontweight="bold", color=COLORS["text"],
            ha="center", va="bottom", zorder=22,
            path_effects=stroke)

        # Harorat (pastda) — tire bilan
        if tmin is not None:
            temp_str = f"{tmin}\u00b0\u2013{tmax}\u00b0"
        else:
            temp_str = f"{tmax}\u00b0"

        ax.annotate(temp_str, (lon, lat),
            xytext=(0, -11), textcoords="offset points",
            fontsize=8.5, fontweight="bold", color=clr,
            ha="center", va="top", zorder=22,
            path_effects=stroke)



def draw_table(ax, cities_data):
    """O'ng panelda shaharlar jadvali."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor("white")
    ax.axis("off")

    # Jadval sarlavhasi
    ax.text(0.5, 0.97, "Viloyat markazlari bo\u2018yicha prognoz",
            fontsize=10, fontweight="bold", color=COLORS["text"],
            ha="center", va="top")

    # Ustun sarlavhalari
    y_start = 0.93
    col_x = [0.02, 0.38, 0.62, 0.82]
    headers = ["Shahar", "T\u00b0C", "Shamol", "Hodisa"]

    for i, h in enumerate(headers):
        ax.text(col_x[i], y_start, h,
                fontsize=8, fontweight="bold", color=COLORS["muted"],
                va="top")

    # Chiziq
    ax.axhline(y=y_start - 0.015, xmin=0.01, xmax=0.99,
               color=COLORS["border"], lw=0.8)

    # Shaharlar
    sorted_cities = sorted(cities_data.items(),
                          key=lambda x: x[1].get("temp_max", 0) if x[1] else 0,
                          reverse=True)

    row_h = 0.058
    y = y_start - 0.04

    for name, info in sorted_cities:
        if not info or info.get("temp_max") is None:
            continue
        if y < 0.02:
            break

        tmax = info["temp_max"]
        tmin = info.get("temp_min")
        wind = info.get("wind", 0)
        weather = info.get("weather", "ochiq")
        clr = get_temp_color(tmax)
        wlabel, wicon = WEATHER_LABELS.get(weather, ("", "\u2022"))

        # Rang chizig'i (chap tomonda)
        ax.plot([0.0], [y - 0.005], "s", color=clr, ms=5, mec="none",
                transform=ax.transAxes, clip_on=False)

        # Shahar nomi
        ax.text(col_x[0], y, name, fontsize=8.5, color=COLORS["text"],
                va="center", fontweight="500")

        # Harorat
        if tmin is not None:
            t_str = f"{tmin}\u00b0\u2013{tmax}\u00b0"
        else:
            t_str = f"{tmax}\u00b0"
        ax.text(col_x[1], y, t_str, fontsize=8.5, color=clr,
                va="center", fontweight="bold")

        # Shamol
        if wind:
            ax.text(col_x[2], y, f"{wind} m/s", fontsize=8,
                    color=COLORS["muted"], va="center")

        # Hodisa
        ax.text(col_x[3], y, wlabel, fontsize=7.5,
                color=COLORS["muted"], va="center")

        y -= row_h

    # Legend (pastda)
    y_leg = 0.03
    ax.text(0.5, y_leg, "Ranglar: harorat darajasiga mos", fontsize=7,
            color=COLORS["muted"], ha="center", va="bottom", style="italic")
