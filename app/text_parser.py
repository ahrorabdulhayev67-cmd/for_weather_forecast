"""
O'zgidromet Telegram prognoz matni parser.

Kirish: O'zgidromet rasmiy TG kanali formati
Chiqish: strukturalangan dict (guruhlar bo'yicha)

Namuna kirish:
  🔷TOSHKENT SHAHRI: Havo o'zgaruvchan... Shamol sharqdan 3-8 m/s...
  Harorat kechasi 23-25°, kunduzi 36-38° bo'ladi.

Namuna chiqish:
  {
    "date": "23-iyun",
    "groups": [
      {"name": "Toshkent shahri", "night": "23-25", "day": "36-38",
       "wind": "3-8", "weather": "ochiq", "description": "..."},
      ...
    ],
    "warning": "sel-suv toshqin..."
  }
"""
import re


def parse_forecast_text(text):
    """
    O'zgidromet Telegram prognoz matnini parse qiladi.

    Returns:
        dict: {date, groups: [...], warning, cities: {...}}
    """
    result = {
        "date": "",
        "groups": [],
        "warning": "",
        "cities": {},  # server.py uchun — individual shahar ma'lumotlari
    }

    # Sanani topish
    date_match = re.search(r'(\d{1,2})-?(IYUN|IYUL|YANVAR|FEVRAL|MART|APREL|MAY|AVGUST|SENTABR|OKTABR|NOYABR|DEKABR)\w*\s+OB-HAVO', text, re.IGNORECASE)
    if date_match:
        result["date"] = date_match.group(0).replace("OB-HAVO", "").strip()

    # Matnni bloklarga ajratish (🔷 yoki diam belgisi bilan)
    blocks = re.split(r'[🔷\u25c7]\s*', text)
    blocks = [b.strip() for b in blocks if b.strip()]

    for block in blocks:
        # MUHIM HODISALAR
        if "MUHIM HODISALAR" in block.upper() or "MUHIM OGOHLANTIRISH" in block.upper():
            result["warning"] = block.split(":", 1)[-1].strip() if ":" in block else block
            continue

        # Sana blokini o'tkazib yuborish
        if "OB-HAVO PROGNOZI" in block.upper() and "HARORAT" not in block.upper():
            # Sana qatorini saqlash
            result["date"] = block.strip()
            continue

        # Viloyat bloki
        group = parse_region_block(block)
        if group:
            result["groups"].append(group)

    # cities dict ni to'ldirish (server uchun)
    result["cities"] = groups_to_cities(result["groups"])

    return result


def parse_region_block(block):
    """Bitta viloyat/guruh blokini parse qiladi."""
    # Nom: birinchi jumladan oldin (': ' gacha yoki birinchi qator)
    name_match = re.match(r'^([^:]+):', block)
    if not name_match:
        return None

    name = name_match.group(1).strip()
    body = block[name_match.end():].strip()

    # "RESPUBLIKANING TOG' OLDI..." maxsus holat
    if "TOG'" in name.upper() and "HUDUD" in name.upper():
        name = "Tog' oldi va tog'li hududlar"

    # Nomni tozalash
    name = clean_region_name(name)

    group = {
        "name": name,
        "night": "",
        "day": "",
        "wind": "",
        "wind_max": "",
        "weather": "ochiq",
        "description": body,
    }

    # Harorat: "kechasi 23-25°, kunduzi 36-38°"
    night_match = re.search(r'kechasi\s+(\d+)[-\u2013\u2014](\d+)\s*°', body, re.IGNORECASE)
    if night_match:
        group["night"] = f"{night_match.group(1)}-{night_match.group(2)}"

    day_match = re.search(r'kunduzi\s+(\d+)[-\u2013\u2014](\d+)\s*°', body, re.IGNORECASE)
    if day_match:
        group["day"] = f"{day_match.group(1)}-{day_match.group(2)}"

    # Shamol: "7-12 m/s"
    wind_match = re.search(r'(\d+)[-\u2013](\d+)\s*m/s', body)
    if wind_match:
        group["wind"] = f"{wind_match.group(1)}-{wind_match.group(2)}"

    # Shamol kuchayishi: "15-20 m/s gacha kuchayishi"
    wind_max_match = re.search(r'(\d+)[-\u2013](\d+)\s*m/s\s*gacha\s*kuchay', body)
    if wind_max_match:
        group["wind_max"] = f"{wind_max_match.group(1)}-{wind_max_match.group(2)}"

    # Ob-havo holati aniqlash
    group["weather"] = detect_weather(body)

    return group


def clean_region_name(name):
    """Viloyat nomini tozalash."""
    name = name.strip()
    # Katta harflarni normal qilish
    if name.isupper():
        # "TOSHKENT SHAHRI" -> "Toshkent shahri"
        words = name.split()
        name = " ".join(w.capitalize() if w not in ("VA", "R.", "R", "VILOYATI", "VILOYATLARI")
                        else w.lower() for w in words)
        name = name.replace(" viloyati", "").replace(" viloyatlari", "")
    # "Respublikaning tog' oldi..." tozalash
    name = re.sub(r'^Respublikaning\s+', '', name, flags=re.IGNORECASE)
    return name.strip()


def detect_weather(text):
    """Matn asosida ob-havo holatini aniqlash."""
    text_lower = text.lower()
    if "momaqaldiroq" in text_lower:
        return "momaqaldiroq"
    if "yomg'ir" in text_lower or "yog'ingarchilik" in text_lower.replace("kutilmaydi", ""):
        if "kutilmaydi" in text_lower and "yomg'ir" not in text_lower:
            pass
        elif "qisqa muddatli yomg'ir" in text_lower:
            return "jala"
    if "chang-to'zon" in text_lower or "chang" in text_lower:
        return "chang_boroni"
    if "bulutli" in text_lower and "biroz" not in text_lower:
        return "bulutli"
    if "biroz bulutli" in text_lower or "o'zgaruvchan" in text_lower:
        return "qisman_bulutli"
    return "ochiq"


def groups_to_cities(groups):
    """
    Guruhlarni individual shahar dict'ga aylantirish.
    server.py /api/generate uchun kerak.
    """
    # Guruh -> shaharlar mapping
    GROUP_CITIES_MAP = {
        "Toshkent shahri": ["Toshkent"],
        "Qoraqalpog'iston": ["Nukus", "Urganch"],
        "Xorazm": ["Urganch"],
        "Buxoro": ["Buxoro"],
        "Navoiy": ["Navoiy"],
        "Samarqand": ["Samarqand"],
        "Jizzax": ["Jizzax"],
        "Sirdaryo": ["Guliston"],
        "Qashqadaryo": ["Qarshi"],
        "Surxondaryo": ["Termiz"],
        "Andijon": ["Andijon"],
        "Namangan": ["Namangan"],
        "Farg'ona": ["Farg'ona"],
    }

    cities = {}
    for group in groups:
        name = group["name"]
        # Harorat parse
        night_nums = re.findall(r'\d+', group.get("night", ""))
        day_nums = re.findall(r'\d+', group.get("day", ""))
        wind_nums = re.findall(r'\d+', group.get("wind", ""))

        temp_min = int(night_nums[0]) if night_nums else None
        temp_max = int(day_nums[-1]) if day_nums else None
        wind_val = int(wind_nums[-1]) if wind_nums else None

        city_info = {
            "temp_min": temp_min,
            "temp_max": temp_max,
            "wind": wind_val,
            "weather": group.get("weather", "ochiq"),
            "precip": 0,
        }

        # Guruh nomidagi har bir viloyatni topish
        matched = False
        for key, city_list in GROUP_CITIES_MAP.items():
            if key.lower() in name.lower():
                for city in city_list:
                    cities[city] = dict(city_info)
                matched = True

        if not matched and "tog'" not in name.lower():
            # Birinchi so'zni shahar sifatida ishlatish
            first_word = name.split(",")[0].split()[0]
            cities[first_word] = dict(city_info)

    return cities
