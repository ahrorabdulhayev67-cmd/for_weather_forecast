"""
O'zgidromet — Professional ob-havo prognoz kartochka generatori.
PIL (Pillow) asosida.

Layout:
+--------------------------------------------------+
|  HEADER: Logo + "QISQA MUDDATLI OB-HAVO PROGNOZI"|
+--------------------------------------------------+
|  CHAP: O'zbekiston   |  O'NG: 14 viloyat         |
|  xaritasi (SVG->PNG) |  kartochkalari (4x4 grid) |
|  viloyatlar rangli    |  kunduz/tun/shamol        |
+--------------------------------------------------+
|  DIQQAT XABARI (qizil fonda)                     |
+--------------------------------------------------+
|  FOOTER: sana + @uzgidromet + ob-havo belgilari   |
+--------------------------------------------------+
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime
import os

# === KONFIGURATSIYA ===
WIDTH = 1200
HEIGHT = 900
BG_COLOR = "#FFFFFF"
HEADER_COLOR = "#0B3D8F"
ACCENT_RED = "#C62828"
ACCENT_BLUE = "#1565C0"
TEXT_DARK = "#1A2332"
TEXT_GRAY = "#6B7C8E"
CARD_BG = "#F4F6F9"
ALERT_BG = "#FCEBEB"
ALERT_TEXT = "#791F1F"

MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun",
             "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_UZ = ["dushanba","seshanba","chorshanba","payshanba","juma","shanba","yakshanba"]

WEATHER_SYMBOLS = {
    "ochiq": "\u2600",
    "qisman_bulutli": "\u26c5",
    "bulutli": "\u2601",
    "tuman": "\u2601",
    "yomgir": "\u2602",
    "jala": "\u2602",
    "momaqaldiroq": "\u26a1",
    "qor": "\u2744",
    "dol": "\u2744",
    "chang_boroni": "\u2248",
    "qor_boroni": "\u2744",
}

# Viloyatlar ro'yxati (14 ta)
CITIES_ORDER = [
    "Toshkent", "Samarqand", "Buxoro", "Namangan",
    "Andijon", "Farg'ona", "Qarshi", "Nukus",
    "Navoiy", "Termiz", "Jizzax", "Urganch",
    "Guliston", "Shahrisabz"
]

FONT_DIR = Path(__file__).parent / "fonts"


def get_font(size, bold=False):
    """Shrift olish — mavjud bo'lsa Inter, aks holda default."""
    if bold:
        paths = [
            FONT_DIR / "Inter-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
        ]
    else:
        paths = [
            FONT_DIR / "Inter-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
        ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def get_temp_color(t):
    """Haroratga qarab rang."""
    if t >= 40: return "#B71C1C"
    if t >= 37: return "#D32F2F"
    if t >= 34: return "#E65100"
    if t >= 30: return "#EF6C00"
    if t >= 25: return "#F9A825"
    if t >= 20: return "#558B2F"
    if t >= 10: return "#1565C0"
    return "#0D47A1"


def get_temp_color_map(t):
    """Xarita viloyatlari uchun rang (referensdagidek)."""
    if t >= 40: return "#F7C1C1"
    if t >= 37: return "#EF9F27"
    if t >= 34: return "#EF9F27"
    if t >= 30: return "#FAC775"
    if t >= 25: return "#FAC775"
    if t >= 18: return "#85B7EB"
    return "#85B7EB"


def render_forecast_card(day_data, output_path, dpi=150):
    """
    Bitta kunlik prognoz kartochkasini rasm sifatida generatsiya qiladi.

    day_data = {
        "date": "2026-06-17",
        "cities": {
            "Toshkent": {"temp_min": 22, "temp_max": 35, "weather": "ochiq", "wind": 5},
            ...
        },
        "comment": "Tog' hududlarida sel xavfi"
    }
    """
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Shriftlar
    font_header = get_font(22, bold=True)
    font_sub = get_font(12)
    font_city = get_font(13, bold=True)
    font_temp_big = get_font(20, bold=True)
    font_temp_sm = get_font(14)
    font_wind = get_font(11)
    font_alert = get_font(13, bold=True)
    font_alert_body = get_font(11)
    font_footer = get_font(10)
    font_legend = get_font(10)

    # === HEADER ===
    draw.rectangle([(0, 0), (WIDTH, 60)], fill=HEADER_COLOR)
    draw.text((20, 12), "QISQA MUDDATLI OB-HAVO PROGNOZI", fill="#FFFFFF", font=font_header)

    # Sana
    date_str = day_data.get("date", "")
    if date_str:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        date_label = f"{dt.day} {MONTHS_UZ[dt.month-1]} {dt.year}, {DAYS_UZ[dt.weekday()]}"
    else:
        dt = datetime.now()
        date_label = f"{dt.day} {MONTHS_UZ[dt.month-1]} {dt.year}, {DAYS_UZ[dt.weekday()]}"
    draw.text((20, 40), date_label, fill="#CCDDFF", font=font_sub)

    # Logo o'ng tomonda
    draw.text((WIDTH - 200, 15), "O'ZGIDROMET", fill="#FFFFFF", font=get_font(16, bold=True))
    draw.text((WIDTH - 200, 38), "hydromet.uz", fill="#AAC4E8", font=font_sub)

    # === AJRATUVCHI CHIZIQ ===
    y_start = 65

    # === CHAP PANEL: O'ZBEKISTON XARITASI (viloyat poligonlari) ===
    map_x, map_y = 15, y_start + 10
    map_w, map_h = 440, 520

    # Xarita fon
    draw.rectangle([(map_x, map_y), (map_x + map_w, map_y + map_h)], fill="#DBEEFF", outline="#90CAF9", width=1)

    # SVG koordinatalarini pikselga aylantirish
    # SVG viewBox: 55, 37, 22, 12 -> map_x..map_x+map_w, map_y..map_y+map_h
    def svg_to_px(sx, sy):
        px = map_x + (sx - 55) / 22.0 * map_w
        py = map_y + (sy - 37) / 12.0 * map_h
        return (px, py)

    # Viloyat poligonlari (SVG path dan)
    REGIONS = {
        "Nukus": {
            "path": [(55.5,37.5),(63,37.5),(64,38.5),(64.5,40),(63.5,41.5),(61,42.5),(58,43),(55.5,42)],
            "color": "#85B7EB", "label_pos": (58.5, 40.2)
        },
        "Urganch": {
            "path": [(58,43),(61,42.5),(61.5,44),(60,44.5),(58.5,44)],
            "color": "#85B7EB", "label_pos": (59.2, 43.5)
        },
        "Buxoro": {
            "path": [(61,42.5),(63.5,41.5),(65,43),(65.5,45.5),(63,46),(61.5,45),(61.5,44)],
            "color": "#FAC775", "label_pos": (62.5, 44)
        },
        "Navoiy": {
            "path": [(63.5,41.5),(64.5,40),(66,40),(67,41),(67,42.5),(65,43)],
            "color": "#FAC775", "label_pos": (65, 41.5)
        },
        "Samarqand": {
            "path": [(67,41),(68,40),(69,40.5),(69,42),(68,42.5),(67,42.5)],
            "color": "#EF9F27", "label_pos": (67.8, 41.5)
        },
        "Jizzax": {
            "path": [(68,40),(69.5,39.5),(70,40.5),(69,42),(69,40.5)],
            "color": "#EF9F27", "label_pos": (69, 40.3)
        },
        "Qarshi": {
            "path": [(67,42.5),(68,42.5),(69,42),(69.5,44),(68.5,46),(66.5,46),(65.5,45.5),(65,43)],
            "color": "#FAC775", "label_pos": (67, 44.2)
        },
        "Termiz": {
            "path": [(68.5,46),(69.5,44),(71,44.5),(71,47),(69.5,47.5)],
            "color": "#F7C1C1", "label_pos": (69.5, 45.8)
        },
        "Toshkent": {
            "path": [(69.5,39.5),(71,39),(72,39.5),(71.5,40.5),(70,40.5)],
            "color": "#EF9F27", "label_pos": (70.5, 39.8)
        },
        "Guliston": {
            "path": [(71.5,40.5),(72,39.5),(73,40),(72.5,41.5),(71,41)],
            "color": "#EF9F27", "label_pos": (72, 40.5)
        },
        "Namangan": {
            "path": [(71,39),(72.5,38.5),(74,39),(73.5,40),(73,40),(72,39.5)],
            "color": "#EF9F27", "label_pos": (72.5, 39.2)
        },
        "Andijon": {
            "path": [(73.5,40),(74,39),(75.5,39.5),(76,40.5),(74.5,40.5)],
            "color": "#EF9F27", "label_pos": (74.5, 39.9)
        },
        "Farg'ona": {
            "path": [(72.5,41.5),(73,40),(74.5,40.5),(76,40.5),(76,42),(74,42.5),(72.5,42)],
            "color": "#EF9F27", "label_pos": (74, 41.3)
        },
    }

    cities_data = day_data.get("cities", {})

    # Viloyatlarni chizish
    for city_name, region in REGIONS.items():
        # Haroratga qarab rang
        info = cities_data.get(city_name, {})
        tmax = info.get("temp_max")
        if tmax is not None:
            fill_color = get_temp_color_map(tmax)
        else:
            fill_color = region["color"]

        # Poligon koordinatalari
        polygon = [svg_to_px(x, y) for x, y in region["path"]]
        draw.polygon(polygon, fill=fill_color, outline="#FFFFFF")

    # Viloyat nomlari va harorat
    for city_name, region in REGIONS.items():
        info = cities_data.get(city_name, {})
        tmax = info.get("temp_max")
        lx, ly = svg_to_px(*region["label_pos"])

        # Shahar nomi
        short = city_name[:6] if len(city_name) > 6 else city_name
        bbox = draw.textbbox((0, 0), short, font=font_legend)
        nw = bbox[2] - bbox[0]
        draw.text((lx - nw//2, ly - 5), short, fill="#1a1a1a", font=font_legend)

        # Harorat (agar mavjud)
        if tmax is not None:
            t_str = f"{tmax}\u00b0"
            bbox2 = draw.textbbox((0, 0), t_str, font=font_city)
            tw = bbox2[2] - bbox2[0]
            draw.text((lx - tw//2, ly + 7), t_str, fill="#FFFFFF", font=font_city)

    # Xarita sarlavhasi
    draw.text((map_x + 10, map_y + 5), "O\u2018ZBEKISTON", fill=HEADER_COLOR, font=get_font(11, bold=True))

    # === O'NG PANEL: 14 VILOYAT KARTOCHKALARI ===
    panel_x = map_x + map_w + 20
    panel_y = y_start + 10
    card_w = 165
    card_h = 115
    gap = 8
    cols = 4

    for idx, city_name in enumerate(CITIES_ORDER):
        if idx >= 14:
            break
        row = idx // cols
        col = idx % cols

        cx = panel_x + col * (card_w + gap)
        cy = panel_y + row * (card_h + gap)

        info = cities_data.get(city_name, {})
        tmax = info.get("temp_max")
        tmin = info.get("temp_min")
        wind = info.get("wind")
        weather = info.get("weather", "ochiq")

        # Kartochka fon
        draw.rounded_rectangle([(cx, cy), (cx + card_w, cy + card_h)],
                               radius=8, fill=CARD_BG, outline="#E0E5EC", width=1)

        # Shahar nomi
        draw.text((cx + 8, cy + 6), city_name, fill=TEXT_DARK, font=font_city)

        # Ob-havo belgisi
        w_symbol = WEATHER_SYMBOLS.get(weather, "\u2600")
        draw.text((cx + card_w - 25, cy + 6), w_symbol, fill=TEXT_GRAY, font=font_city)

        # Kunduz harorat (katta, qizil)
        if tmax is not None:
            draw.text((cx + 8, cy + 30), f"+{tmax}\u00b0", fill=ACCENT_RED, font=font_temp_big)
        else:
            draw.text((cx + 8, cy + 30), "\u2014", fill=TEXT_GRAY, font=font_temp_big)

        # Tun harorat (kichik, ko'k)
        if tmin is not None:
            draw.text((cx + 75, cy + 35), f"+{tmin}\u00b0", fill=ACCENT_BLUE, font=font_temp_sm)

        # Shamol
        if wind:
            draw.text((cx + 8, cy + 65), f"\u2192 {wind} m/s", fill=TEXT_GRAY, font=font_wind)

        # Ob-havo nomi
        weather_names = {
            "ochiq":"ochiq","qisman_bulutli":"qis.bulutli","bulutli":"bulutli",
            "yomgir":"yomg'ir","momaqaldiroq":"momaqald.","qor":"qor",
            "tuman":"tuman","jala":"jala","dol":"do'l",
            "chang_boroni":"chang","qor_boroni":"qor bo'r."
        }
        w_name = weather_names.get(weather, "")
        draw.text((cx + 8, cy + 82), w_name, fill=TEXT_GRAY, font=font_legend)

    # === DIQQAT XABARI ===
    alert_y = panel_y + 4 * (card_h + gap) + 10
    comment = day_data.get("comment", "")

    if comment:
        # Qizil fon
        draw.rounded_rectangle([(15, alert_y), (WIDTH - 15, alert_y + 50)],
                               radius=8, fill=ALERT_BG, outline="#F09595", width=1)
        draw.text((25, alert_y + 8), "\u26a0 DIQQAT!", fill=ALERT_TEXT, font=font_alert)
        draw.text((25, alert_y + 28), comment, fill=ALERT_TEXT, font=font_alert_body)
        footer_y = alert_y + 60
    else:
        footer_y = alert_y + 5

    # === FOOTER ===
    # Ob-havo belgilari izohi
    legend_items = [
        ("\u2600", "Quyoshli"), ("\u26c5", "Qis.bulutli"),
        ("\u2601", "Bulutli"), ("\u2602", "Yomg'ir"),
        ("\u26a1", "Momaqaldiroq"), ("\u2744", "Qor"),
    ]
    lx = 20
    for symbol, label in legend_items:
        draw.text((lx, footer_y + 5), f"{symbol} {label}", fill=TEXT_GRAY, font=font_legend)
        lx += 120

    # Chiziq
    draw.line([(15, footer_y + 25), (WIDTH - 15, footer_y + 25)], fill="#E0E5EC", width=1)

    # Sana va kanal
    draw.text((20, footer_y + 30), f"\u00a9 {dt.year} Gidrometeorologiya xizmati agentligi",
              fill=TEXT_GRAY, font=font_footer)
    draw.text((WIDTH - 180, footer_y + 30), "@uzgidromet  |  hydromet.uz",
              fill=TEXT_GRAY, font=font_footer)

    # Saqlash
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG", dpi=(dpi, dpi))
    return output_path
