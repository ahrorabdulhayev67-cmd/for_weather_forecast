"""
Professional ob-havo xaritasi generatori.
Matplotlib + SciPy IDW interpolatsiya.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata
from datetime import datetime, timedelta

# Koordinatalar
CITY_COORDS = {
    "Toshkent":     (41.30, 69.24),
    "Samarqand":    (39.65, 66.96),
    "Buxoro":       (39.77, 64.43),
    "Namangan":     (41.00, 71.67),
    "Andijon":      (40.78, 72.34),
    "Farg'ona":     (40.38, 71.79),
    "Qarshi":       (38.86, 65.80),
    "Nukus":        (42.46, 59.60),
    "Navoiy":       (40.10, 65.38),
    "Termiz":       (37.22, 67.28),
    "Jizzax":       (40.12, 67.84),
    "Urganch":      (41.55, 60.63),
    "Guliston":     (40.49, 68.78),
    "Shahrisabz":   (39.06, 66.83),
}

WEATHER_SYMBOLS = {
    "ochiq": "☀", "qisman_bulutli": "⛅", "bulutli": "☁",
    "tuman": "▒", "yomgir": "🌧", "jala": "⛆",
    "momaqaldiroq": "⛈", "qor": "❄", "dol": "⛰",
    "chang_boroni": "≋", "qor_boroni": "❅",
}

MONTHS = ["yanvar","fevral","mart","aprel","may","iyun",
          "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS = ["dushanba","seshanba","chorshanba","payshanba","juma","shanba","yakshanba"]



def temp_colormap():
    """Meteorologik harorat rang skalasi"""
    colors = [
        (0.00, "#1a237e"),  # < -5°C
        (0.10, "#1565c0"),  # -5…0°C
        (0.20, "#42a5f5"),  # 0…10°C
        (0.35, "#66bb6a"),  # 10…18°C
        (0.45, "#c0ca33"),  # 18…24°C
        (0.55, "#ffee58"),  # 24…28°C
        (0.65, "#ffa726"),  # 28…33°C
        (0.75, "#f44336"),  # 33…38°C
        (0.85, "#c62828"),  # 38…42°C
        (1.00, "#6a1b9a"),  # 42°C+
    ]
    positions = [c[0] for c in colors]
    rgb_colors = []
    for _, h in colors:
        r, g, b = int(h[1:3],16)/255, int(h[3:5],16)/255, int(h[5:7],16)/255
        rgb_colors.append((r, g, b))
    return LinearSegmentedColormap.from_list("temp", list(zip(positions, rgb_colors)))


def render_forecast_map(day_data, output_path, dpi=180):
    """
    Prognoz xaritasini yaratadi va PNG sifatida saqlaydi.
    """
    cities_data = day_data.get("cities", {})
    comment = day_data.get("comment", "")
    date_str = day_data.get("date", "")
    day_index = day_data.get("day_index", 0)

    # Sanani aniqlash
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        dt = datetime.now() + timedelta(days=day_index)

    day_labels = ["I KUN", "II KUN", "III KUN"]
    title_label = day_labels[day_index] if day_index < 3 else ""
    date_label = f"{dt.day} {MONTHS[dt.month-1]} {dt.year}, {DAYS[dt.weekday()]}"

    # Ma'lumotlarni tayyorlash
    lats, lons, temps = [], [], []
    city_info = {}
    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        tmax = info.get("temp_max")
        if tmax is None:
            continue
        lat, lon = CITY_COORDS[name]
        lats.append(lat)
        lons.append(lon)
        temps.append(tmax)
        city_info[name] = info

    if not lats:
        # Bo'sh xarita
        fig = plt.figure(figsize=(14, 9), facecolor="#0d1b2a")
        fig.text(0.5, 0.5, "Ma'lumot kiritilmagan", ha="center", va="center",
                fontsize=20, color="white")
        plt.savefig(output_path, dpi=dpi, facecolor=fig.get_facecolor())
        plt.close()
        return

    lats = np.array(lats)
    lons = np.array(lons)
    temps = np.array(temps)

    # Interpolatsiya gridi
    grid_lon = np.linspace(57.0, 73.5, 280)
    grid_lat = np.linspace(36.5, 45.5, 180)
    glon, glat = np.meshgrid(grid_lon, grid_lat)

    try:
        grid_t = griddata((lons, lats), temps, (glon, glat), method="cubic")
        mask = np.isnan(grid_t)
        if mask.any():
            nearest = griddata((lons, lats), temps, (glon, glat), method="nearest")
            grid_t[mask] = nearest[mask]
    except Exception:
        grid_t = griddata((lons, lats), temps, (glon, glat), method="nearest")


    # ========== XARITA CHIZISH ==========
    fig = plt.figure(figsize=(14, 9), facecolor="#0d1b2a")
    ax = fig.add_axes([0.04, 0.06, 0.82, 0.82])
    ax.set_facecolor("#0d1b2a")
    ax.set_xlim(57.0, 73.5)
    ax.set_ylim(36.5, 45.5)
    ax.set_aspect("equal")
    ax.axis("off")

    # Harorat gradient
    cmap = temp_colormap()
    im = ax.pcolormesh(glon, glat, grid_t, cmap=cmap,
                       vmin=-5, vmax=48, alpha=0.6, shading="auto", zorder=1)

    # Soddalashtirilgan O'zbekiston chegarasi
    border = np.array([
        [56.5,41.3],[58.0,42.5],[59.5,42.0],[60.5,41.7],[62.0,41.5],
        [64.0,41.0],[66.0,39.5],[67.0,37.3],[68.0,38.0],[69.0,37.1],
        [70.5,38.4],[71.5,39.9],[72.5,40.8],[73.1,40.4],[72.0,41.0],
        [70.5,41.5],[69.0,41.3],[67.0,41.2],[65.0,42.0],[63.0,43.5],
        [60.0,44.5],[58.5,45.5],[56.5,44.5],[56.5,41.3]
    ])
    ax.plot(border[:,0], border[:,1], color="white", lw=1.8, alpha=0.7, zorder=5)

    # Shahar markerlari
    stroke = [pe.withStroke(linewidth=3, foreground="#0d1b2a")]

    for name, info in city_info.items():
        lat, lon = CITY_COORDS[name]
        tmax = info["temp_max"]
        tmin = info.get("temp_min")
        weather = info.get("weather", "ochiq")
        symbol = WEATHER_SYMBOLS.get(weather, "•")

        # Rang (haroratga qarab)
        if tmax >= 40: clr = "#ff1744"
        elif tmax >= 35: clr = "#ff6d00"
        elif tmax >= 28: clr = "#ffab00"
        elif tmax >= 18: clr = "#76ff03"
        elif tmax >= 5: clr = "#00e5ff"
        else: clr = "#448aff"

        # Marker nuqta
        ax.plot(lon, lat, "o", color=clr, ms=8, mec="white", mew=1.2, zorder=10)

        # Shahar nomi + harorat
        tmin_str = f"{tmin}°/" if tmin is not None else ""
        label = f"{name}  {tmin_str}{tmax}°C"
        ax.annotate(label, (lon, lat), xytext=(8, -3), textcoords="offset points",
                   fontsize=9.5, color="white", fontweight="bold",
                   path_effects=stroke, zorder=11)

        # Ob-havo belgisi
        ax.annotate(symbol, (lon, lat), xytext=(-14, -3), textcoords="offset points",
                   fontsize=11, color=clr, path_effects=stroke, zorder=11)

    # ===== SARLAVHA =====
    fig.text(0.44, 0.94,
             "GIDROMETEOROLOGIYA XIZMATI AGENTLIGI",
             fontsize=16, fontweight="bold", color="white", ha="center",
             path_effects=[pe.withStroke(linewidth=1, foreground="#0d1b2a")])
    fig.text(0.44, 0.905,
             f"Qisqa muddatli ob-havo prognozi  •  {title_label}  •  {date_label}",
             fontsize=11, color="#b0bec5", ha="center")

    # ===== IZOH =====
    if comment:
        fig.text(0.44, 0.025, comment,
                fontsize=10, color="#e0e0e0", ha="center", va="bottom", wrap=True,
                bbox=dict(boxstyle="round,pad=0.4", fc="#1a2e44", ec="#3d5a80", alpha=0.9))

    # ===== RANG SKALASI =====
    cbar_ax = fig.add_axes([0.88, 0.12, 0.015, 0.55])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label("Harorat, °C", color="white", fontsize=9)
    cbar.ax.tick_params(colors="white", labelsize=8)

    # ===== MANBA =====
    fig.text(0.97, 0.01, "hydromet.uz", fontsize=8, color="#5a7a9a",
            ha="right", va="bottom")

    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
