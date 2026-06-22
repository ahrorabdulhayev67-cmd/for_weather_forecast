"""
O'zgidromet — 2 ta alohida rasm generatori.
FAQAT PIL (Pillow) — matplotlib KERAK EMAS.
GeoJSON koordinatalari -> PIL polygon.

1-RASM: Xarita (to'liq, sifatli)
2-RASM: Jadval (guruhlar + ijtimoiy tarmoqlar)
"""
import json
import urllib.request
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# === CONFIG ===
GEOJSON_URL = "https://raw.githubusercontent.com/akbartus/GeoJSON-Uzbekistan/main/Uzbekistan_regions.json"
CACHE_DIR = Path(__file__).parent / "data"
GEOJSON_CACHE = CACHE_DIR / "uzbekistan_regions.geojson"
LOGO_PATH = Path(__file__).parent / "static" / "uzhydromet-logo.jpg"

MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun",
             "iyul","avgust","sentabr","oktabr","noyabr","dekabr"]
DAYS_UZ = ["dushanba","seshanba","chorshanba","payshanba","juma","shanba","yakshanba"]

REGION_CITY_MAP = {
    "Toshkent":"Toshkent","Tashkent":"Toshkent","Toshkent \u0448.":"Toshkent",
    "Samarqand":"Samarqand","Samarkand":"Samarqand",
    "Buxoro":"Buxoro","Bukhara":"Buxoro",
    "Namangan":"Namangan","Andijon":"Andijon","Andijan":"Andijon",
    "Farg'ona":"Farg'ona","Fergana":"Farg'ona","Fargona":"Farg'ona",
    "Qashqadaryo":"Qarshi","Kashkadarya":"Qarshi",
    "Qoraqalpog'iston Respublikasi":"Nukus","Qoraqalpog'iston":"Nukus","Karakalpakstan":"Nukus",
    "Navoiy":"Navoiy","Navoi":"Navoiy",
    "Surxondaryo":"Termiz","Surxandaryo":"Termiz","Surkhandarya":"Termiz",
    "Jizzax":"Jizzax","Jizzakh":"Jizzax",
    "Xorazm":"Urganch","Khorezm":"Urganch",
    "Sirdaryo":"Guliston","Syrdarya":"Guliston",
}


def temp_to_color(t):
    if t is None: return "#E8EEF4"
    if t >= 42: return "#FFCDD2"
    if t >= 40: return "#FFAB91"
    if t >= 38: return "#FFCC80"
    if t >= 36: return "#FFE082"
    if t >= 34: return "#FFF59D"
    if t >= 32: return "#E6EE9C"
    if t >= 30: return "#C5E1A5"
    if t >= 28: return "#A5D6A7"
    if t >= 25: return "#80CBC4"
    if t >= 20: return "#80DEEA"
    if t >= 15: return "#90CAF9"
    return "#B39DDB"


def get_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def download_geojson():
    """Lokal GeoJSON faylni olish (repoda mavjud)."""
    local_path = Path(__file__).parent / "data" / "uzbekistan_regions.geojson"
    if local_path.exists():
        return local_path
    # Fallback: yuklab olish
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if GEOJSON_CACHE.exists():
        return GEOJSON_CACHE
    try:
        urllib.request.urlretrieve(GEOJSON_URL, str(GEOJSON_CACHE))
        return GEOJSON_CACHE
    except Exception:
        return None


def get_city_for_region(name):
    for key, city in REGION_CITY_MAP.items():
        if key.lower() in name.lower() or name.lower() in key.lower():
            return city
    return None


def geo_to_pixel(lon, lat, bounds, img_w, img_h, padding=20):
    """GeoJSON koordinatani pikselga aylantirish."""
    min_lon, min_lat, max_lon, max_lat = bounds
    x = padding + (lon - min_lon) / (max_lon - min_lon) * (img_w - 2*padding)
    y = padding + (max_lat - lat) / (max_lat - min_lat) * (img_h - 2*padding)
    return (x, y)


# ===========================================================
# 1-RASM: XARITA
# ===========================================================
def render_map_image(day_data, output_path):
    cities_data = day_data.get("cities", {})
    date_str = day_data.get("date", "")
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            dt = datetime.now()
    else:
        dt = datetime.now()
    date_label = f"{dt.day} {MONTHS_UZ[dt.month-1]} {dt.year}, {DAYS_UZ[dt.weekday()]}"

    W, H = 1600, 1200
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # HEADER
    draw.rectangle([(0, 0), (W, 70)], fill="#0B3D8F")
    if LOGO_PATH.exists():
        try:
            logo = Image.open(str(LOGO_PATH)).resize((55, 55))
            img.paste(logo, (10, 8))
        except Exception:
            pass
    draw.text((75, 12), "O'ZGIDROMET", fill="#FFFFFF", font=get_font(20, True))
    draw.text((75, 40), "Gidrometeorologiya xizmati", fill="#B0C4DE", font=get_font(12))
    draw.text((W//2, 15), "HARORAT XARITASI", fill="#FFFFFF", font=get_font(18, True), anchor="mt")
    draw.text((W//2, 45), date_label, fill="#B0C4DE", font=get_font(12), anchor="mt")

    # XARITA CHIZISH
    geojson_path = download_geojson()
    map_top = 80
    map_h = H - 130
    map_w = W - 40

    if geojson_path and geojson_path.exists():
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson = json.load(f)

        # Bounds hisoblash
        all_lons, all_lats = [], []
        for feat in geojson.get("features", []):
            geom = feat["geometry"]
            rings = []
            if geom["type"] == "Polygon":
                rings = geom["coordinates"]
            elif geom["type"] == "MultiPolygon":
                for mp in geom["coordinates"]:
                    rings.extend(mp)
            for ring in rings:
                for lon, lat in ring:
                    all_lons.append(lon)
                    all_lats.append(lat)

        bounds = (min(all_lons), min(all_lats), max(all_lons), max(all_lats))

        def to_px(lon, lat):
            return geo_to_pixel(lon, lat, bounds, map_w, map_h, padding=30)

        # Viloyatlarni chizish
        centroids = {}
        for feat in geojson.get("features", []):
            props = feat.get("properties", {})
            region_name = props.get("name") or props.get("NAME_1") or ""
            geom = feat["geometry"]
            city = get_city_for_region(region_name)
            info = cities_data.get(city, {}) if city else {}
            tmax = info.get("temp_max") if info else None
            fill = temp_to_color(tmax)

            rings = []
            if geom["type"] == "Polygon":
                rings = geom["coordinates"]
            elif geom["type"] == "MultiPolygon":
                for mp in geom["coordinates"]:
                    rings.extend(mp)

            largest_ring = max(rings, key=len) if rings else None

            for ring in rings:
                pixels = [(20 + to_px(lon, lat)[0], map_top + to_px(lon, lat)[1]) for lon, lat in ring]
                if len(pixels) >= 3:
                    draw.polygon(pixels, fill=fill, outline="#2C3E50")

            if city and largest_ring:
                cx = sum(p[0] for p in largest_ring) / len(largest_ring)
                cy = sum(p[1] for p in largest_ring) / len(largest_ring)
                px, py = to_px(cx, cy)
                centroids[city] = (20 + px, map_top + py)

        # Viloyat nomlari + harorat
        font_name = get_font(13, True)
        font_temp = get_font(15, True)
        for city, (px, py) in centroids.items():
            info = cities_data.get(city, {})
            tmax = info.get("temp_max") if info else None

            # Oq fon doira
            draw.ellipse([(px-28, py-20), (px+28, py+20)], fill="#FFFFFFCC", outline=None)

            # Nom
            draw.text((px, py-8), city[:5], fill="#1A2332", font=get_font(10, True), anchor="mm")

            # Harorat
            if tmax is not None:
                draw.text((px, py+8), f"{tmax}\u00b0", fill="#C62828", font=font_temp, anchor="mm")

    # FOOTER (colorbar placeholder)
    draw.rectangle([(0, H-50), (W, H)], fill="#F5F7FA")
    draw.text((W//2, H-30), "Harorat skalasi: 15\u00b0...42\u00b0C+", fill="#546E7A", font=get_font(11), anchor="mm")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    return output_path


# ===========================================================
# 2-RASM: JADVAL
# ===========================================================
def render_table_image(day_data, output_path):
    cities_data = day_data.get("cities", {})
    comment = day_data.get("comment", "")
    date_str = day_data.get("date", "")
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            dt = datetime.now()
    else:
        dt = datetime.now()
    date_label = f"{dt.day} {MONTHS_UZ[dt.month-1]} {dt.year}, {DAYS_UZ[dt.weekday()]}"

    W, H = 1200, 1000
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    # HEADER
    draw.rectangle([(0, 0), (W, 70)], fill="#0B3D8F")
    if LOGO_PATH.exists():
        try:
            logo = Image.open(str(LOGO_PATH)).resize((55, 55))
            img.paste(logo, (10, 8))
        except Exception:
            pass
    draw.text((75, 12), "O'ZGIDROMET", fill="#FFFFFF", font=get_font(18, True))
    draw.text((75, 40), "Gidrometeorologiya xizmati", fill="#B0C4DE", font=get_font(11))
    draw.text((W//2, 15), "VILOYATLAR BO'YICHA PROGNOZ", fill="#FFFFFF", font=get_font(16, True), anchor="mt")
    draw.text((W//2, 45), date_label, fill="#B0C4DE", font=get_font(11), anchor="mt")

    # JADVAL
    GROUPS = [
        {"name": "Toshkent shahri", "cities": ["Toshkent"]},
        {"name": "Qoraqalpog'iston R., Xorazm", "cities": ["Nukus", "Urganch"]},
        {"name": "Buxoro viloyati", "cities": ["Buxoro"]},
        {"name": "Navoiy viloyati", "cities": ["Navoiy"]},
        {"name": "Toshkent, Samarqand, Jizzax, Sirdaryo", "cities": ["Toshkent", "Samarqand", "Jizzax", "Guliston"]},
        {"name": "Qashqadaryo, Surxondaryo", "cities": ["Qarshi", "Termiz"]},
        {"name": "Andijon, Namangan, Farg'ona", "cities": ["Andijon", "Namangan", "Farg'ona"]},
        {"name": "Tog' oldi va tog'li hududlar", "cities": ["Toshkent", "Namangan"]},
    ]

    # Sarlavha
    y = 90
    cols = [30, 550, 750, 950]
    draw.text((cols[0], y), "HUDUD", fill="#0B3D8F", font=get_font(14, True))
    draw.text((cols[1], y), "KECHASI", fill="#1565C0", font=get_font(14, True))
    draw.text((cols[2], y), "KUNDUZI", fill="#C62828", font=get_font(14, True))
    draw.text((cols[3], y), "SHAMOL", fill="#37474F", font=get_font(14, True))
    y += 30
    draw.line([(20, y), (W-20, y)], fill="#B0BEC5", width=2)
    y += 15

    row_h = 75
    for i, group in enumerate(GROUPS):
        gy = y + i * row_h

        # Zebra
        if i % 2 == 0:
            draw.rectangle([(20, gy-5), (W-20, gy+row_h-10)], fill="#F5F9FC")

        # Ma'lumot
        tmins, tmaxs, winds = [], [], []
        for city in group["cities"]:
            info = cities_data.get(city, {})
            if not info: continue
            if info.get("temp_min") is not None: tmins.append(info["temp_min"])
            if info.get("temp_max") is not None: tmaxs.append(info["temp_max"])
            if info.get("wind") is not None: winds.append(info["wind"])

        night = f"{min(tmins)}-{max(tmins)}\u00b0" if tmins else "\u2014"
        day_t = f"{min(tmaxs)}-{max(tmaxs)}\u00b0" if tmaxs else "\u2014"
        wind = f"{min(winds)}-{max(winds)} m/s" if winds else "\u2014"

        draw.text((cols[0], gy+10), group["name"], fill="#1A2332", font=get_font(13, True))
        draw.text((cols[1], gy+8), night, fill="#1565C0", font=get_font(16, True))
        draw.text((cols[2], gy+5), day_t, fill="#C62828", font=get_font(18, True))
        draw.text((cols[3], gy+10), wind, fill="#37474F", font=get_font(13))

    # DIQQAT
    warn_y = y + len(GROUPS) * row_h + 10
    if comment:
        draw.rounded_rectangle([(20, warn_y), (W-20, warn_y+50)], radius=8, fill="#FFF3E0", outline="#FF6F00")
        draw.text((35, warn_y+12), f"\u26a0 {comment}", fill="#E65100", font=get_font(13, True))
        warn_y += 60

    # FOOTER — ijtimoiy tarmoqlar (haqiqiy logolar bilan)
    footer_y = max(warn_y + 20, H - 160)
    draw.rectangle([(0, footer_y), (W, H)], fill="#F0F4F8")
    draw.line([(0, footer_y), (W, footer_y)], fill="#CFD8DC", width=1)

    draw.text((W//2, footer_y+15), f"\u00a9 {dt.year} O'zbekiston Respublikasi Gidrometeorologiya xizmati agentligi",
              fill="#263238", font=get_font(12, True), anchor="mt")

    # Ijtimoiy tarmoq logolari
    SOCIAL_DIR = Path(__file__).parent / "static" / "social"
    socials = [
        ("web.png", "uzgidromet.uz"),
        ("telegram.png", "t.me/uzgidromet"),
        ("instagram.jpg", "instagram.com/uzgidromet.uz"),
        ("facebook.png", "facebook.com/uzgidromet.uz"),
        ("youtube.png", "youtube.com/@uzgidromet_"),
    ]

    ly = footer_y + 45
    x_pos = 40
    icon_size = 28
    for icon_file, link_text in socials:
        icon_path = SOCIAL_DIR / icon_file
        if icon_path.exists():
            try:
                icon_img = Image.open(str(icon_path)).convert("RGBA")
                icon_img = icon_img.resize((icon_size, icon_size), Image.LANCZOS)
                # PNG transparency uchun
                img.paste(icon_img, (x_pos, ly), icon_img if icon_img.mode == "RGBA" else None)
            except Exception:
                pass
        draw.text((x_pos + icon_size + 6, ly + 5), link_text, fill="#37474F", font=get_font(11))
        x_pos += 230

    img.save(output_path, "PNG")
    return output_path


# ===========================================================
# ASOSIY (server.py uchun)
# ===========================================================
def render_forecast_card(day_data, output_path, dpi=150):
    """2 ta rasm: xarita + jadval."""
    base = Path(output_path)
    stem = base.stem
    parent = base.parent
    parent.mkdir(parents=True, exist_ok=True)

    map_path = str(parent / f"{stem}_map.png")
    render_map_image(day_data, map_path)

    tbl_path = str(parent / f"{stem}_table.png")
    render_table_image(day_data, tbl_path)

    # Asosiy fayl = xarita
    render_map_image(day_data, output_path)
    return output_path
