"""
Gidrometeorologiya xizmati — Multipanel prognoz xarita generatori.
3 xarita: Harorat | Yog'ingarchilik | Shamol
+ Jadval + Header/Footer

Layout:
┌──────────────────────────────────────────┐
│        SARLAVHA + SANA                   │
├─────────────┬─────────────┬──────────────┤
│  HARORAT    │ YOG'INGARCHI│   SHAMOL     │
│  (ranglar)  │   (ranglar) │ (strelkalar) │
├─────────────┴─────────────┴──────────────┤
│         JADVAL (kompakt)                 │
├──────────────────────────────────────────┤
│  IZOH + IJTIMOIY TARMOQLAR              │
└──────────────────────────────────────────┘
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata
from datetime import datetime, timedelta

import cartopy.crs as ccrs
import cartopy.feature as cfeature


# === KONFIGURATSIYA ===
CITY_COORDS = {
    "Toshkent":     (41.30, 69.24),
    "Samarqand":    (39.65, 66.96),
    "Buxoro":       (39.77, 64.43),
    "Namangan":     (41.00, 71.67),
    "Andijon":      (40.78, 72.34),
    "Farg\u2018ona":(40.38, 71.79),
    "Qarshi":       (38.86, 65.80),
    "Nukus":        (42.46, 59.60),
    "Navoiy":       (40.10, 65.38),
    "Termiz":       (37.22, 67.28),
    "Jizzax":       (40.12, 67.84),
    "Urganch":      (41.55, 60.63),
    "Guliston":     (40.49, 68.78),
    "Shahrisabz":   (39.06, 66.83),
}

WEATHER_LABELS = {
    "ochiq":"Ochiq", "qisman_bulutli":"Qis.bulutli",
    "bulutli":"Bulutli", "tuman":"Tuman",
    "yomgir":"Yomg\u2018ir", "jala":"Jala",
    "momaqaldiroq":"Momaq.", "qor":"Qor",
    "dol":"Do\u2018l", "chang_boroni":"Chang",
    "qor_boroni":"Q.bo\u2018ron",
}

MONTHS = ["yanvar","fevral","mart","aprel","may","iyun",
          "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_W = ["dushanba","seshanba","chorshanba",
          "payshanba","juma","shanba","yakshanba"]

MAP_EXTENT = [56.0, 73.5, 36.5, 45.8]



# === RANG SKALARI ===
def temp_cmap():
    """Harorat uchun rang skalasi: ko'k → yashil → sariq → qizil → binafsha"""
    colors = [
        (0.00, (0.10, 0.10, 0.55)),  # -10: to'q ko'k
        (0.15, (0.08, 0.40, 0.75)),  # 0: ko'k
        (0.30, (0.20, 0.70, 0.70)),  # 10: ko'k-yashil
        (0.40, (0.20, 0.60, 0.20)),  # 18: yashil
        (0.50, (0.60, 0.75, 0.10)),  # 24: sariq-yashil
        (0.60, (0.95, 0.85, 0.10)),  # 30: sariq
        (0.70, (0.95, 0.55, 0.05)),  # 34: to'q sariq
        (0.80, (0.85, 0.20, 0.05)),  # 38: qizil
        (0.90, (0.65, 0.05, 0.05)),  # 42: to'q qizil
        (1.00, (0.45, 0.05, 0.30)),  # 46+: binafsha
    ]
    return LinearSegmentedColormap.from_list("temp",
        [(p, c) for p, c in colors])


def precip_cmap():
    """Yog'ingarchilik: oq → yashil → ko'k → to'q ko'k"""
    colors = [
        (0.0, (1.0, 1.0, 1.0)),      # 0mm: oq
        (0.1, (0.85, 0.95, 0.85)),    # 0.5mm: juda och
        (0.25, (0.55, 0.85, 0.55)),   # 2mm: och yashil
        (0.45, (0.20, 0.70, 0.30)),   # 5mm: yashil
        (0.65, (0.10, 0.50, 0.70)),   # 10mm: ko'k-yashil
        (0.80, (0.05, 0.30, 0.75)),   # 15mm: ko'k
        (1.0, (0.10, 0.10, 0.50)),    # 20+mm: to'q ko'k
    ]
    return LinearSegmentedColormap.from_list("precip",
        [(p, c) for p, c in colors])


def wind_cmap():
    """Shamol tezligi: och → to'q"""
    colors = [
        (0.0, (0.90, 0.95, 0.90)),    # 0 m/s: och
        (0.3, (0.55, 0.80, 0.60)),    # 3 m/s: yashil
        (0.5, (0.90, 0.80, 0.20)),    # 5 m/s: sariq
        (0.7, (0.90, 0.50, 0.10)),    # 8 m/s: to'q sariq
        (1.0, (0.70, 0.10, 0.10)),    # 12+ m/s: qizil
    ]
    return LinearSegmentedColormap.from_list("wind",
        [(p, c) for p, c in colors])



def interpolate_field(cities_data, field, default=0):
    """Shaharlar orasidagi maydonni IDW interpolatsiya qilish."""
    lats, lons, vals = [], [], []
    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        v = info.get(field, default)
        if v is None:
            v = default
        lat, lon = CITY_COORDS[name]
        lats.append(lat)
        lons.append(lon)
        vals.append(float(v))

    if len(lats) < 3:
        return None, None, None

    lats = np.array(lats)
    lons = np.array(lons)
    vals = np.array(vals)

    grid_lon = np.linspace(56.0, 73.5, 200)
    grid_lat = np.linspace(36.5, 45.8, 120)
    glon, glat = np.meshgrid(grid_lon, grid_lat)

    try:
        grid_v = griddata((lons, lats), vals, (glon, glat), method="cubic")
        mask = np.isnan(grid_v)
        if mask.any():
            nearest = griddata((lons, lats), vals, (glon, glat), method="nearest")
            grid_v[mask] = nearest[mask]
    except Exception:
        grid_v = griddata((lons, lats), vals, (glon, glat), method="nearest")

    return glon, glat, grid_v


def setup_map_axes(ax):
    """Xarita axes uchun umumiy sozlamalar."""
    ax.set_extent(MAP_EXTENT, crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.LAND, facecolor="#fafafa", zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor="#e8f0f8", zorder=0)
    ax.add_feature(cfeature.LAKES, facecolor="#d4e8f5",
                   edgecolor="#7ba7cc", linewidth=0.3, zorder=1)
    ax.add_feature(cfeature.RIVERS, edgecolor="#7ba7cc",
                   linewidth=0.3, zorder=1)
    ax.add_feature(cfeature.BORDERS, linewidth=1.5,
                   edgecolor="#2c3e50", linestyle="-", zorder=5)
    gl = ax.gridlines(draw_labels=False, linewidth=0.2,
                      color="#bbb", alpha=0.4, linestyle=":")



def render_forecast_map(day_data, output_path, dpi=180):
    """3 panelli prognoz xaritasi + jadval."""
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

    proj = ccrs.PlateCarree()
    stroke = [pe.withStroke(linewidth=2.5, foreground="white")]

    # === FIGURE ===
    fig = plt.figure(figsize=(16, 12), facecolor="white")

    # --- HEADER ---
    fig.text(0.50, 0.975,
        "GIDROMETEOROLOGIYA XIZMATI AGENTLIGI",
        fontsize=13, fontweight="bold", color="#0d2137",
        ha="center", va="top")
    fig.text(0.50, 0.955,
        f"Qisqa muddatli ob-havo prognozi  \u2014  {title_label}  \u2014  {date_label}",
        fontsize=9.5, color="#455a64", ha="center", va="top")

    # === 3 XARITA PANELI ===
    # 1) HARORAT
    ax1 = fig.add_axes([0.01, 0.48, 0.32, 0.44], projection=proj)
    setup_map_axes(ax1)
    ax1.set_title("Harorat, \u00b0C", fontsize=10, fontweight="bold",
                  color="#0d2137", pad=4)

    glon, glat, grid_t = interpolate_field(cities_data, "temp_max", 25)
    if grid_t is not None:
        im1 = ax1.pcolormesh(glon, glat, grid_t, cmap=temp_cmap(),
            vmin=-5, vmax=48, alpha=0.7, shading="auto",
            transform=proj, zorder=2)
        cb1 = fig.colorbar(im1, ax=ax1, orientation="horizontal",
            fraction=0.05, pad=0.02, aspect=30)
        cb1.ax.tick_params(labelsize=7)

    # Shahar nomlari
    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        tmax = info.get("temp_max")
        if tmax is None:
            continue
        lat, lon = CITY_COORDS[name]
        tmin = info.get("temp_min")
        t_str = f"{tmin}\u00b0\u2013{tmax}\u00b0" if tmin else f"{tmax}\u00b0"
        ax1.plot(lon, lat, "o", color="white", ms=4, mec="#333",
                 mew=0.8, zorder=20, transform=proj)
        ax1.annotate(t_str, (lon, lat), xytext=(0, -6),
            textcoords="offset points", fontsize=6.5,
            fontweight="bold", color="#1a1a1a", ha="center",
            va="top", zorder=22, path_effects=stroke,
            xycoords=proj._as_mpl_transform(ax1))


    # 2) YOG'INGARCHILIK
    ax2 = fig.add_axes([0.34, 0.48, 0.32, 0.44], projection=proj)
    setup_map_axes(ax2)
    ax2.set_title("Yog\u2018ingarchilik, mm", fontsize=10,
                  fontweight="bold", color="#0d2137", pad=4)

    glon2, glat2, grid_p = interpolate_field(cities_data, "precip", 0)
    if grid_p is not None:
        im2 = ax2.pcolormesh(glon2, glat2, grid_p, cmap=precip_cmap(),
            vmin=0, vmax=20, alpha=0.7, shading="auto",
            transform=proj, zorder=2)
        cb2 = fig.colorbar(im2, ax=ax2, orientation="horizontal",
            fraction=0.05, pad=0.02, aspect=30)
        cb2.ax.tick_params(labelsize=7)

    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        precip = info.get("precip", 0)
        if precip is None:
            precip = 0
        lat, lon = CITY_COORDS[name]
        ax2.plot(lon, lat, "o", color="white", ms=4, mec="#333",
                 mew=0.8, zorder=20, transform=proj)
        if precip > 0:
            ax2.annotate(f"{precip}", (lon, lat), xytext=(0, -6),
                textcoords="offset points", fontsize=6.5,
                fontweight="bold", color="#0d47a1", ha="center",
                va="top", zorder=22, path_effects=stroke,
                xycoords=proj._as_mpl_transform(ax2))

    # 3) SHAMOL
    ax3 = fig.add_axes([0.67, 0.48, 0.32, 0.44], projection=proj)
    setup_map_axes(ax3)
    ax3.set_title("Shamol, m/s", fontsize=10,
                  fontweight="bold", color="#0d2137", pad=4)

    glon3, glat3, grid_w = interpolate_field(cities_data, "wind", 3)
    if grid_w is not None:
        im3 = ax3.pcolormesh(glon3, glat3, grid_w, cmap=wind_cmap(),
            vmin=0, vmax=12, alpha=0.6, shading="auto",
            transform=proj, zorder=2)
        cb3 = fig.colorbar(im3, ax=ax3, orientation="horizontal",
            fraction=0.05, pad=0.02, aspect=30)
        cb3.ax.tick_params(labelsize=7)

    # Shamol strelkalari
    for name, info in cities_data.items():
        if name not in CITY_COORDS or not info:
            continue
        wind = info.get("wind", 0)
        if not wind or wind < 1:
            continue
        lat, lon = CITY_COORDS[name]
        # Strelka uzunligi shamolga proporsional
        dx = min(wind * 0.06, 0.6)
        ax3.annotate("", xy=(lon + dx, lat),
            xytext=(lon, lat),
            arrowprops=dict(arrowstyle="-|>", color="#37474f",
                           lw=1.5, mutation_scale=12),
            transform=proj, zorder=20)
        ax3.annotate(f"{wind}", (lon, lat), xytext=(0, -6),
            textcoords="offset points", fontsize=6,
            fontweight="bold", color="#37474f", ha="center",
            va="top", zorder=22, path_effects=stroke,
            xycoords=proj._as_mpl_transform(ax3))


    # === JADVAL (pastki qism) ===
    tbl_ax = fig.add_axes([0.02, 0.08, 0.96, 0.36])
    tbl_ax.set_xlim(0, 1)
    tbl_ax.set_ylim(0, 1)
    tbl_ax.axis("off")

    # Jadval: 2 ustun (chap va o'ng — 7 ta shahar har birida)
    sorted_cities = sorted(
        [(n, d) for n, d in cities_data.items()
         if d and d.get("temp_max") is not None],
        key=lambda x: x[1]["temp_max"], reverse=True)

    col_offset = [0.0, 0.50]  # 2 ustunli layout
    per_col = 7

    for col_idx in range(2):
        x_off = col_offset[col_idx]
        start = col_idx * per_col
        end = start + per_col
        col_cities = sorted_cities[start:end]

        # Sarlavha
        y = 0.95
        tbl_ax.text(x_off + 0.01, y, "Shahar", fontsize=7.5,
                   fontweight="bold", color="#455a64")
        tbl_ax.text(x_off + 0.18, y, "T, \u00b0C", fontsize=7.5,
                   fontweight="bold", color="#455a64")
        tbl_ax.text(x_off + 0.30, y, "m/s", fontsize=7.5,
                   fontweight="bold", color="#455a64")
        tbl_ax.text(x_off + 0.37, y, "mm", fontsize=7.5,
                   fontweight="bold", color="#455a64")
        tbl_ax.text(x_off + 0.43, y, "Hodisa", fontsize=7.5,
                   fontweight="bold", color="#455a64")
        tbl_ax.axhline(y=y - 0.02, xmin=x_off, xmax=x_off + 0.48,
                      color="#cfd8dc", lw=0.6)

        row_y = y - 0.08
        row_h = 0.12

        for name, info in col_cities:
            tmax = info["temp_max"]
            tmin = info.get("temp_min")
            wind = info.get("wind")
            precip = info.get("precip", 0)
            weather = info.get("weather", "ochiq")
            clr = get_temp_color(tmax)
            w_label = WEATHER_LABELS.get(weather, "")

            # Shahar
            tbl_ax.text(x_off + 0.01, row_y, name, fontsize=8,
                       color="#263238", va="center")
            # Harorat
            t_str = f"{tmin}\u00b0\u2013{tmax}\u00b0" if tmin else f"{tmax}\u00b0"
            tbl_ax.text(x_off + 0.18, row_y, t_str, fontsize=8,
                       color=clr, va="center", fontweight="bold")
            # Shamol
            if wind:
                tbl_ax.text(x_off + 0.30, row_y, str(wind),
                           fontsize=7.5, color="#546e7a", va="center")
            # Yog'in
            if precip and precip > 0:
                tbl_ax.text(x_off + 0.37, row_y, f"{precip}",
                           fontsize=7.5, color="#1565c0", va="center",
                           fontweight="bold")
            # Hodisa
            tbl_ax.text(x_off + 0.43, row_y, w_label, fontsize=7,
                       color="#546e7a", va="center")

            row_y -= row_h

    # === FOOTER ===
    if comment:
        fig.text(0.50, 0.04, comment,
            fontsize=8.5, color="#37474f", ha="center", va="center",
            style="italic", wrap=True)

    fig.text(0.50, 0.008,
        "hydromet.uz   \u2022   t.me/uzhydromet   \u2022   facebook.com/uzhydromet",
        fontsize=7.5, color="#78909c", ha="center", va="bottom")

    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none", pad_inches=0.05)
    plt.close()


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



# === RANG SKALARI ===
def temp_cmap():
    colors = [
        (0.00, (0.10, 0.10, 0.55)),
        (0.15, (0.08, 0.40, 0.75)),
        (0.30, (0.20, 0.70, 0.70)),
        (0.40, (0.20, 0.60, 0.20)),
        (0.50, (0.60, 0.75, 0.10)),
        (0.60, (0.95, 0.85, 0.10)),
        (0.70, (0.95, 0.55, 0.05)),
        (0.80, (0.85, 0.20, 0.05)),
        (0.90, (0.65, 0.05, 0.05)),
        (1.00, (0.45, 0.05, 0.30)),
    ]
    return LinearSegmentedColormap.from_list("temp", [(p, c) for p, c in colors])

def precip_cmap():
    colors = [
        (0.0,  (1.0, 1.0, 1.0)),
        (0.1,  (0.85, 0.95, 0.85)),
        (0.25, (0.55, 0.85, 0.55)),
        (0.45, (0.20, 0.70, 0.30)),
        (0.65, (0.10, 0.50, 0.70)),
        (0.80, (0.05, 0.30, 0.75)),
        (1.0,  (0.10, 0.10, 0.50)),
    ]
    return LinearSegmentedColormap.from_list("precip", [(p, c) for p, c in colors])

def wind_cmap():
    colors = [
        (0.0, (0.90, 0.95, 0.90)),
        (0.3, (0.55, 0.80, 0.60)),
        (0.5, (0.90, 0.80, 0.20)),
        (0.7, (0.90, 0.50, 0.10)),
        (1.0, (0.70, 0.10, 0.10)),
    ]
    return LinearSegmentedColormap.from_list("wind", [(p, c) for p, c in colors])
