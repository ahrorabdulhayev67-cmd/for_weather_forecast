#!/usr/bin/env python3
"""
O'ZGIDROMET — Professional Ob-havo Prognoz Xaritasi Generatori
================================================================
Sinoptik raqamlarni kiritadi → Chiroyli PNG xarita hosil bo'ladi.

Ishlatish:
    python generate_map.py                   # Namuna ma'lumotlar bilan
    python generate_map.py --input data.json # JSON fayldan
    python generate_map.py --csv data.csv    # CSV fayldan

Talablar:
    pip install matplotlib numpy scipy cartopy Pillow
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Server uchun (GUI kerak emas)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import griddata

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    HAS_CARTOPY = True
except ImportError:
    HAS_CARTOPY = False
    print("⚠️  Cartopy topilmadi. Oddiy matplotlib xarita ishlatiladi.")
    print("   O'rnatish: pip install cartopy")


# ============================================================
# O'ZBEKISTON SHAHARLARI
# ============================================================
CITIES = {
    "Toshkent":     {"lat": 41.30, "lon": 69.24, "capital": True},
    "Samarqand":    {"lat": 39.65, "lon": 66.96, "capital": False},
    "Buxoro":       {"lat": 39.77, "lon": 64.43, "capital": False},
    "Namangan":     {"lat": 41.00, "lon": 71.67, "capital": False},
    "Andijon":      {"lat": 40.78, "lon": 72.34, "capital": False},
    "Farg'ona":     {"lat": 40.38, "lon": 71.79, "capital": False},
    "Qarshi":       {"lat": 38.86, "lon": 65.80, "capital": False},
    "Nukus":        {"lat": 42.46, "lon": 59.60, "capital": False},
    "Navoiy":       {"lat": 40.10, "lon": 65.38, "capital": False},
    "Termiz":       {"lat": 37.22, "lon": 67.28, "capital": False},
    "Jizzax":       {"lat": 40.12, "lon": 67.84, "capital": False},
    "Urganch":      {"lat": 41.55, "lon": 60.63, "capital": False},
    "Guliston":     {"lat": 40.49, "lon": 68.78, "capital": False},
    "Shahrisabz":   {"lat": 39.06, "lon": 66.83, "capital": False},
}

# O'zbekiston chegarasi koordinatalari (soddalashtirilgan)
UZB_BORDER = np.array([
    [56.0, 41.3], [57.0, 41.5], [58.0, 42.5], [58.5, 42.6],
    [59.0, 42.0], [59.5, 41.8], [60.0, 42.0], [60.5, 41.7],
    [61.0, 41.5], [61.5, 41.9], [62.0, 41.5], [63.0, 41.2],
    [64.0, 41.0], [65.0, 40.1], [66.0, 39.6], [66.5, 39.4],
    [67.0, 37.3], [67.5, 37.2], [68.0, 37.9], [68.5, 38.2],
    [69.0, 37.1], [70.0, 37.3], [70.5, 38.4], [71.0, 39.5],
    [71.5, 39.9], [72.0, 40.5], [72.5, 40.8], [73.1, 40.4],
    [72.0, 41.0], [71.5, 41.5], [71.0, 41.0], [70.5, 41.5],
    [70.0, 41.8], [69.5, 41.0], [69.0, 41.2], [68.5, 40.9],
    [68.0, 41.0], [67.0, 41.2], [66.0, 41.7], [65.0, 42.0],
    [64.0, 43.5], [62.0, 44.0], [60.0, 44.5], [58.5, 45.5],
    [56.0, 45.0], [56.0, 41.3]
])



# ============================================================
# NAMUNA MA'LUMOTLAR (sinoptik kiritishi kerak bo'lgan formatda)
# ============================================================
SAMPLE_FORECAST = {
    "date": "2026-06-18",
    "day_label": "Bugun",
    "comment": "Respublikada havo ochiq va issiq. Janubiy hududlarda harorat 40°C dan oshadi. Suv ko'proq ichish tavsiya etiladi.",
    "cities": {
        "Toshkent":   {"temp_min": 22, "temp_max": 36, "wind": 12, "precip": 0, "weather": "ochiq"},
        "Samarqand":  {"temp_min": 18, "temp_max": 33, "wind": 8,  "precip": 0, "weather": "az_bulutli"},
        "Buxoro":     {"temp_min": 24, "temp_max": 40, "wind": 15, "precip": 0, "weather": "ochiq"},
        "Namangan":   {"temp_min": 20, "temp_max": 35, "wind": 10, "precip": 0, "weather": "az_bulutli"},
        "Andijon":    {"temp_min": 21, "temp_max": 34, "wind": 8,  "precip": 2, "weather": "yomgir"},
        "Farg'ona":   {"temp_min": 22, "temp_max": 38, "wind": 6,  "precip": 0, "weather": "ochiq"},
        "Qarshi":     {"temp_min": 23, "temp_max": 41, "wind": 12, "precip": 0, "weather": "ochiq"},
        "Nukus":      {"temp_min": 20, "temp_max": 38, "wind": 18, "precip": 0, "weather": "az_bulutli"},
        "Navoiy":     {"temp_min": 21, "temp_max": 39, "wind": 14, "precip": 0, "weather": "ochiq"},
        "Termiz":     {"temp_min": 26, "temp_max": 44, "wind": 10, "precip": 0, "weather": "ochiq"},
        "Jizzax":     {"temp_min": 20, "temp_max": 36, "wind": 11, "precip": 0, "weather": "bulutli"},
        "Urganch":    {"temp_min": 21, "temp_max": 37, "wind": 16, "precip": 0, "weather": "az_bulutli"},
        "Guliston":   {"temp_min": 21, "temp_max": 35, "wind": 9,  "precip": 0, "weather": "az_bulutli"},
        "Shahrisabz": {"temp_min": 19, "temp_max": 34, "wind": 7,  "precip": 0, "weather": "bulutli"},
    }
}

# Ob-havo turlari → ikonkalar (Unicode)
WEATHER_ICONS = {
    "ochiq":        "☀",
    "az_bulutli":   "🌤",
    "bulutli":      "☁",
    "toliq_bulut":  "🌥",
    "tuman":        "🌫",
    "yomgir":       "🌧",
    "kuchli_yomgir":"⛈",
    "qor":          "❄",
    "shamol":       "💨",
    "dol":          "🌨",
}


# ============================================================
# HARORAT RANG SKALASI (professional meteorologik)
# ============================================================
def create_temp_colormap():
    """Professional ob-havo xarita uchun rang skalasi"""
    colors = [
        (0.0,  '#1a237e'),   # -10°C va past — to'q ko'k
        (0.1,  '#1565c0'),   # -5°C
        (0.2,  '#42a5f5'),   # 0°C — och ko'k
        (0.3,  '#4dd0e1'),   # 10°C — ko'k-yashil
        (0.4,  '#66bb6a'),   # 15°C — yashil
        (0.5,  '#aed581'),   # 20°C — och yashil
        (0.6,  '#ffee58'),   # 25°C — sariq
        (0.7,  '#ffa726'),   # 30°C — to'q sariq
        (0.8,  '#f44336'),   # 35°C — qizil
        (0.9,  '#c62828'),   # 40°C — to'q qizil
        (1.0,  '#6a1b9a'),   # 45°C+ — binafsha
    ]
    positions = [c[0] for c in colors]
    hex_colors = [c[1] for c in colors]
    
    # HEX dan RGB ga
    rgb_colors = []
    for h in hex_colors:
        r = int(h[1:3], 16) / 255
        g = int(h[3:5], 16) / 255
        b = int(h[5:7], 16) / 255
        rgb_colors.append((r, g, b))
    
    cmap = LinearSegmentedColormap.from_list('uzb_temp', list(zip(positions, rgb_colors)))
    return cmap



# ============================================================
# ASOSIY XARITA GENERATSIYA FUNKSIYASI
# ============================================================
def generate_forecast_map(forecast_data=None, output_path="forecast_map.png", dpi=200):
    """
    Professional ob-havo prognoz xaritasini yaratadi.
    
    Args:
        forecast_data: Prognoz ma'lumotlari (dict). None bo'lsa namuna ishlatiladi.
        output_path: Chiqish fayl nomi
        dpi: Rasm sifati (72=tezkor, 150=oddiy, 200=yuqori, 300=bosma)
    """
    if forecast_data is None:
        forecast_data = SAMPLE_FORECAST
    
    # ========== HARORAT INTERPOLATSIYASI ==========
    lats = []
    lons = []
    temps = []
    
    for city_name, data in forecast_data["cities"].items():
        if city_name in CITIES:
            city = CITIES[city_name]
            lats.append(city["lat"])
            lons.append(city["lon"])
            temps.append(data["temp_max"])
    
    lats = np.array(lats)
    lons = np.array(lons)
    temps = np.array(temps)
    
    # Grid yaratish (interpolatsiya uchun)
    grid_lon = np.linspace(55.5, 73.5, 300)
    grid_lat = np.linspace(36.5, 46.0, 200)
    grid_lon_2d, grid_lat_2d = np.meshgrid(grid_lon, grid_lat)
    
    # IDW interpolatsiya (scipy)
    points = np.column_stack([lons, lats])
    grid_temp = griddata(points, temps, (grid_lon_2d, grid_lat_2d), method='cubic')
    
    # NaN joylarni nearest bilan to'ldirish
    mask = np.isnan(grid_temp)
    if mask.any():
        grid_temp_nearest = griddata(points, temps, (grid_lon_2d, grid_lat_2d), method='nearest')
        grid_temp[mask] = grid_temp_nearest[mask]
    
    # ========== XARITA YARATISH ==========
    fig = plt.figure(figsize=(16, 11), facecolor='#0a1628')
    
    if HAS_CARTOPY:
        ax = fig.add_axes([0.05, 0.08, 0.85, 0.82], projection=ccrs.PlateCarree())
        ax.set_extent([55.5, 73.5, 36.5, 46.0], crs=ccrs.PlateCarree())
        
        # Cartopy xususiyatlari
        ax.add_feature(cfeature.LAND, facecolor='#1a2744', zorder=0)
        ax.add_feature(cfeature.OCEAN, facecolor='#0a1628', zorder=0)
        ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='#4a6fa5', zorder=3)
        ax.add_feature(cfeature.LAKES, facecolor='#1a3a5c', edgecolor='#4a6fa5', linewidth=0.3, zorder=2)
        ax.add_feature(cfeature.RIVERS, edgecolor='#2a5a8c', linewidth=0.3, zorder=2)
        
        transform = ccrs.PlateCarree()
    else:
        ax = fig.add_axes([0.05, 0.08, 0.85, 0.82])
        ax.set_xlim(55.5, 73.5)
        ax.set_ylim(36.5, 46.0)
        ax.set_facecolor('#1a2744')
        ax.set_aspect('equal')
        transform = None
    
    # ========== HARORAT GRADIENT (heatmap) ==========
    temp_cmap = create_temp_colormap()
    temp_min_val = -10
    temp_max_val = 50
    
    if HAS_CARTOPY:
        im = ax.pcolormesh(grid_lon_2d, grid_lat_2d, grid_temp,
                          cmap=temp_cmap, vmin=temp_min_val, vmax=temp_max_val,
                          alpha=0.65, transform=transform, zorder=1, shading='auto')
    else:
        im = ax.pcolormesh(grid_lon_2d, grid_lat_2d, grid_temp,
                          cmap=temp_cmap, vmin=temp_min_val, vmax=temp_max_val,
                          alpha=0.65, zorder=1, shading='auto')
    
    # ========== O'ZBEKISTON CHEGARASI ==========
    border_lons = UZB_BORDER[:, 0]
    border_lats = UZB_BORDER[:, 1]
    
    if HAS_CARTOPY:
        ax.plot(border_lons, border_lats, color='#ffffff', linewidth=2.0,
                transform=transform, zorder=5, alpha=0.8)
    else:
        ax.plot(border_lons, border_lats, color='#ffffff', linewidth=2.0,
                zorder=5, alpha=0.8)
    
    # ========== SHAHAR MARKERLARI VA HARORAT ==========
    text_effects = [
        pe.withStroke(linewidth=3, foreground='#0a1628'),
    ]
    
    for city_name, data in forecast_data["cities"].items():
        if city_name not in CITIES:
            continue
        
        city = CITIES[city_name]
        lat, lon = city["lat"], city["lon"]
        temp_max = data["temp_max"]
        temp_min = data["temp_min"]
        weather = data.get("weather", "ochiq")
        wind = data.get("wind", 0)
        
        # Ob-havo ikonkasi
        icon = WEATHER_ICONS.get(weather, "☀")
        
        # Rang tanlash (haroratga qarab)
        if temp_max >= 40:
            temp_color = '#ff1744'
        elif temp_max >= 35:
            temp_color = '#ff6d00'
        elif temp_max >= 30:
            temp_color = '#ffab00'
        elif temp_max >= 20:
            temp_color = '#76ff03'
        elif temp_max >= 10:
            temp_color = '#00e5ff'
        else:
            temp_color = '#448aff'
        
        # Marker
        marker_size = 10 if city.get("capital") else 7
        plot_kwargs = {"transform": transform} if HAS_CARTOPY else {}
        
        ax.plot(lon, lat, 'o', color=temp_color, markersize=marker_size,
                markeredgecolor='white', markeredgewidth=1.5, zorder=10, **plot_kwargs)
        
        # Harorat matni
        temp_text = f"{temp_max}°"
        ax.annotate(temp_text, (lon, lat),
                   xytext=(8, -4), textcoords='offset points',
                   fontsize=14, fontweight='bold', color=temp_color,
                   path_effects=text_effects, zorder=11,
                   **({'xycoords': transform._as_mpl_transform(ax)} if HAS_CARTOPY else {}))
        
        # Shahar nomi
        name_offset = (8, 8) if not city.get("capital") else (10, 10)
        fontsize = 11 if city.get("capital") else 9
        ax.annotate(f"{icon} {city_name}", (lon, lat),
                   xytext=name_offset, textcoords='offset points',
                   fontsize=fontsize, color='white', fontweight='bold' if city.get("capital") else 'normal',
                   path_effects=text_effects, zorder=11,
                   **({'xycoords': transform._as_mpl_transform(ax)} if HAS_CARTOPY else {}))
    
    # ========== SARLAVHA ==========
    date_str = forecast_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    day_label = forecast_data.get("day_label", "Bugun")
    
    title = f"O'ZGIDROMET — OB-HAVO PROGNOZI"
    subtitle = f"📅 {day_label} | {date_str} | Maksimal harorat (°C)"
    
    fig.text(0.5, 0.96, title, fontsize=22, fontweight='bold', color='white',
            ha='center', va='top',
            path_effects=[pe.withStroke(linewidth=2, foreground='#0a1628')])
    fig.text(0.5, 0.925, subtitle, fontsize=13, color='#b0bec5',
            ha='center', va='top')
    
    # ========== IZOH (pastda) ==========
    comment = forecast_data.get("comment", "")
    if comment:
        fig.text(0.5, 0.03, f"📋 {comment}", fontsize=11, color='#e0e0e0',
                ha='center', va='bottom', wrap=True,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a2744',
                         edgecolor='#4a6fa5', alpha=0.9))
    
    # ========== COLORBAR (rang skalasi) ==========
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.6])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label('Harorat (°C)', color='white', fontsize=11)
    cbar.ax.tick_params(colors='white', labelsize=9)
    cbar.ax.yaxis.label.set_color('white')
    
    # ========== LEGEND ==========
    legend_items = [
        mpatches.Patch(facecolor='#ff1744', label='40°C +  (juda issiq)'),
        mpatches.Patch(facecolor='#ff6d00', label='35-40°C (issiq)'),
        mpatches.Patch(facecolor='#ffab00', label='30-35°C (iliq)'),
        mpatches.Patch(facecolor='#76ff03', label='20-30°C (qulay)'),
        mpatches.Patch(facecolor='#00e5ff', label='10-20°C (salqin)'),
        mpatches.Patch(facecolor='#448aff', label='10°C dan past'),
    ]
    
    legend = ax.legend(handles=legend_items, loc='lower left', fontsize=8,
                      facecolor='#1a2744', edgecolor='#4a6fa5', labelcolor='white',
                      title='Harorat shkala', title_fontsize=9)
    legend.get_title().set_color('white')
    
    # ========== WATERMARK ==========
    fig.text(0.98, 0.01, "© O'zgidromet | Avtomatik generatsiya",
            fontsize=8, color='#4a6fa5', ha='right', va='bottom')
    
    # ========== SAQLASH ==========
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    
    print(f"✅ Xarita yaratildi: {output_path}")
    print(f"   Hajmi: {os.path.getsize(output_path) / 1024:.0f} KB")
    print(f"   Sifat: {dpi} DPI")
    return output_path



# ============================================================
# 3 KUNLIK XARITA YARATISH
# ============================================================
def generate_3day_maps(forecast_3day=None, output_dir="output"):
    """3 kun uchun alohida xaritalar yaratadi"""
    Path(output_dir).mkdir(exist_ok=True)
    
    if forecast_3day is None:
        forecast_3day = SAMPLE_3DAY
    
    output_files = []
    for i, day_data in enumerate(forecast_3day):
        filename = f"{output_dir}/prognoz_kun_{i+1}.png"
        generate_forecast_map(day_data, output_path=filename)
        output_files.append(filename)
    
    print(f"\n🎉 Barcha xaritalar tayyor! ({len(output_files)} ta)")
    for f in output_files:
        print(f"   📄 {f}")
    
    return output_files


# 3 kunlik namuna
SAMPLE_3DAY = [
    {
        "date": "2026-06-18",
        "day_label": "Bugun (18-iyun, Chorshanba)",
        "comment": "Havo ochiq va issiq. Termiz, Qarshi, Buxoro — 40°C+. Suv ichish tavsiya etiladi.",
        "cities": {
            "Toshkent": {"temp_min": 22, "temp_max": 36, "wind": 12, "precip": 0, "weather": "ochiq"},
            "Samarqand": {"temp_min": 18, "temp_max": 33, "wind": 8, "precip": 0, "weather": "az_bulutli"},
            "Buxoro": {"temp_min": 24, "temp_max": 40, "wind": 15, "precip": 0, "weather": "ochiq"},
            "Namangan": {"temp_min": 20, "temp_max": 35, "wind": 10, "precip": 0, "weather": "az_bulutli"},
            "Andijon": {"temp_min": 21, "temp_max": 34, "wind": 8, "precip": 0, "weather": "az_bulutli"},
            "Farg'ona": {"temp_min": 22, "temp_max": 38, "wind": 6, "precip": 0, "weather": "ochiq"},
            "Qarshi": {"temp_min": 23, "temp_max": 41, "wind": 12, "precip": 0, "weather": "ochiq"},
            "Nukus": {"temp_min": 20, "temp_max": 38, "wind": 18, "precip": 0, "weather": "az_bulutli"},
            "Navoiy": {"temp_min": 21, "temp_max": 39, "wind": 14, "precip": 0, "weather": "ochiq"},
            "Termiz": {"temp_min": 26, "temp_max": 44, "wind": 10, "precip": 0, "weather": "ochiq"},
            "Jizzax": {"temp_min": 20, "temp_max": 36, "wind": 11, "precip": 0, "weather": "bulutli"},
            "Urganch": {"temp_min": 21, "temp_max": 37, "wind": 16, "precip": 0, "weather": "az_bulutli"},
            "Guliston": {"temp_min": 21, "temp_max": 35, "wind": 9, "precip": 0, "weather": "az_bulutli"},
            "Shahrisabz": {"temp_min": 19, "temp_max": 34, "wind": 7, "precip": 0, "weather": "bulutli"},
        }
    },
    {
        "date": "2026-06-19",
        "day_label": "Ertaga (19-iyun, Payshanba)",
        "comment": "Shimoliy-sharqda momaqaldiroqli yomg'ir. Xorazmda kuchli shamol (20+ km/s). Ehtiyot bo'ling!",
        "cities": {
            "Toshkent": {"temp_min": 21, "temp_max": 34, "wind": 15, "precip": 3, "weather": "yomgir"},
            "Samarqand": {"temp_min": 17, "temp_max": 31, "wind": 12, "precip": 5, "weather": "yomgir"},
            "Buxoro": {"temp_min": 23, "temp_max": 38, "wind": 18, "precip": 0, "weather": "bulutli"},
            "Namangan": {"temp_min": 19, "temp_max": 33, "wind": 14, "precip": 8, "weather": "kuchli_yomgir"},
            "Andijon": {"temp_min": 20, "temp_max": 32, "wind": 12, "precip": 10, "weather": "kuchli_yomgir"},
            "Farg'ona": {"temp_min": 21, "temp_max": 35, "wind": 10, "precip": 5, "weather": "yomgir"},
            "Qarshi": {"temp_min": 22, "temp_max": 39, "wind": 14, "precip": 0, "weather": "az_bulutli"},
            "Nukus": {"temp_min": 19, "temp_max": 36, "wind": 22, "precip": 0, "weather": "shamol"},
            "Navoiy": {"temp_min": 20, "temp_max": 37, "wind": 16, "precip": 0, "weather": "bulutli"},
            "Termiz": {"temp_min": 25, "temp_max": 42, "wind": 12, "precip": 0, "weather": "ochiq"},
            "Jizzax": {"temp_min": 19, "temp_max": 34, "wind": 13, "precip": 2, "weather": "yomgir"},
            "Urganch": {"temp_min": 20, "temp_max": 35, "wind": 20, "precip": 0, "weather": "shamol"},
            "Guliston": {"temp_min": 20, "temp_max": 33, "wind": 11, "precip": 1, "weather": "yomgir"},
            "Shahrisabz": {"temp_min": 18, "temp_max": 32, "wind": 9, "precip": 4, "weather": "yomgir"},
        }
    },
    {
        "date": "2026-06-20",
        "day_label": "Indinga (20-iyun, Juma)",
        "comment": "Havo barqarorlashadi. Az bulutli, yog'ingarchilik kutilmaydi. Harorat bir oz pasayadi.",
        "cities": {
            "Toshkent": {"temp_min": 20, "temp_max": 32, "wind": 10, "precip": 0, "weather": "az_bulutli"},
            "Samarqand": {"temp_min": 16, "temp_max": 30, "wind": 8, "precip": 0, "weather": "az_bulutli"},
            "Buxoro": {"temp_min": 22, "temp_max": 37, "wind": 12, "precip": 0, "weather": "az_bulutli"},
            "Namangan": {"temp_min": 18, "temp_max": 31, "wind": 8, "precip": 0, "weather": "bulutli"},
            "Andijon": {"temp_min": 19, "temp_max": 30, "wind": 6, "precip": 0, "weather": "bulutli"},
            "Farg'ona": {"temp_min": 20, "temp_max": 33, "wind": 7, "precip": 0, "weather": "az_bulutli"},
            "Qarshi": {"temp_min": 21, "temp_max": 38, "wind": 10, "precip": 0, "weather": "ochiq"},
            "Nukus": {"temp_min": 18, "temp_max": 35, "wind": 14, "precip": 0, "weather": "az_bulutli"},
            "Navoiy": {"temp_min": 19, "temp_max": 36, "wind": 11, "precip": 0, "weather": "az_bulutli"},
            "Termiz": {"temp_min": 24, "temp_max": 41, "wind": 8, "precip": 0, "weather": "ochiq"},
            "Jizzax": {"temp_min": 18, "temp_max": 33, "wind": 9, "precip": 0, "weather": "az_bulutli"},
            "Urganch": {"temp_min": 19, "temp_max": 34, "wind": 12, "precip": 0, "weather": "bulutli"},
            "Guliston": {"temp_min": 19, "temp_max": 32, "wind": 8, "precip": 0, "weather": "az_bulutli"},
            "Shahrisabz": {"temp_min": 17, "temp_max": 31, "wind": 7, "precip": 0, "weather": "az_bulutli"},
        }
    }
]



# ============================================================
# JSON/CSV FAYLDAN O'QISH
# ============================================================
def load_from_json(filepath):
    """JSON fayldan prognoz ma'lumotlarini o'qish"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_from_csv(filepath):
    """
    CSV fayldan o'qish. Format:
    shahar,temp_min,temp_max,wind,precip,weather
    Toshkent,22,36,12,0,ochiq
    Samarqand,18,33,8,0,az_bulutli
    ...
    """
    import csv
    cities_data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cities_data[row['shahar']] = {
                "temp_min": int(row['temp_min']),
                "temp_max": int(row['temp_max']),
                "wind": int(row.get('wind', 0)),
                "precip": float(row.get('precip', 0)),
                "weather": row.get('weather', 'ochiq'),
            }
    return {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "day_label": "Bugun",
        "comment": "",
        "cities": cities_data
    }


# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("🌦️  O'ZGIDROMET — Prognoz Xarita Generatori")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--input" and len(sys.argv) > 2:
            data = load_from_json(sys.argv[2])
            generate_forecast_map(data)
        elif sys.argv[1] == "--csv" and len(sys.argv) > 2:
            data = load_from_csv(sys.argv[2])
            generate_forecast_map(data)
        elif sys.argv[1] == "--3day":
            generate_3day_maps()
        elif sys.argv[1] == "--help":
            print(__doc__)
        else:
            print(f"Noma'lum argument: {sys.argv[1]}")
            print("Yordam: python generate_map.py --help")
    else:
        # Namuna bilan bitta xarita
        print("\n📌 Namuna ma'lumotlar bilan xarita yaratilmoqda...")
        print("   (O'z ma'lumotlaringiz bilan: python generate_map.py --input data.json)\n")
        generate_forecast_map()
        
        print("\n" + "=" * 60)
        print("💡 3 kunlik xaritalar uchun: python generate_map.py --3day")
        print("=" * 60)
