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
    draw.text((20, 40), date_label, fill="rgba(255,255,255,0.8)", font=font_sub)

    # Logo o'ng tomonda
    draw.text((WIDTH - 200, 15), "O'ZGIDROMET", fill="#FFFFFF", font=get_font(16, bold=True))
    draw.text((WIDTH - 200, 38), "hydromet.uz", fill="rgba(255,255,255,0.7)", font=font_sub)

    # === AJRATUVCHI CHIZIQ ===
    y_start = 65

    # === CHAP PANEL: XARITA (placeholder — rangli to'rtburchaklar) ===
    map_x, map_y = 15, y_start + 10
    map_w, map_h = 440, 520

    # Xarita fon
    draw.rectangle([(map_x, map_y), (map_x + map_w, map_y + map_h)], fill="#E3F2FD", outline="#90CAF9", width=1)

    # Oddiy viloyat ko'rsatkich (placeholder dots)
    cities_data = day_data.get("cities", {})
    CITY_POS_MAP = {
        "Toshkent": (330, 80), "Namangan": (380, 60), "Andijon": (400, 95),
        "Farg'ona": (385, 120), "Samarqand": (280, 145), "Jizzax": (310, 105),
        "Buxoro": (180, 200), "Navoiy": (220, 130), "Qarshi": (270, 230),
        "Termiz": (320, 310), "Nukus": (100, 130), "Urganch": (110, 190),
        "Guliston": (345, 115), "Shahrisabz": (285, 200),
    }

    for city_name, pos in CITY_POS_MAP.items():
        info = cities_data.get(city_name, {})
        cx = map_x + pos[0]
        cy = map_y + pos[1]

        # Doira
        tmax = info.get("temp_max")
        if tmax is not None:
            clr = get_temp_color(tmax)
            draw.ellipse([(cx-12, cy-12), (cx+12, cy+12)], fill=clr, outline="#FFFFFF", width=2)
            # Harorat raqami
            t_text = str(tmax)
            bbox = draw.textbbox((0, 0), t_text, font=font_temp_sm)
            tw = bbox[2] - bbox[0]
            draw.text((cx - tw//2, cy - 7), t_text, fill="#FFFFFF", font=font_temp_sm)
        else:
            draw.ellipse([(cx-8, cy-8), (cx+8, cy+8)], fill="#B0BEC5", outline="#FFFFFF", width=1)

        # Shahar nomi (pastda)
        short_name = city_name[:5] if len(city_name) > 5 else city_name
        bbox = draw.textbbox((0, 0), short_name, font=font_legend)
        nw = bbox[2] - bbox[0]
        draw.text((cx - nw//2, cy + 14), short_name, fill=TEXT_DARK, font=font_legend)

    # Xarita sarlavhasi
    draw.text((map_x + 10, map_y + 5), "O'ZBEKISTON", fill=HEADER_COLOR, font=get_font(11, bold=True))

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
