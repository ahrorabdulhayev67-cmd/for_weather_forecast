# 🗺️ O'zgidromet — Python Prognoz Xarita Generatori

Sinoptiklar oddiy raqamlarni kiritadi → Professional ob-havo xaritasi PNG sifatida yaratiladi.

## ⚡ Tezkor boshlash

```bash
# 1. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 2. Namuna bilan xarita yaratish
python generate_map.py

# 3. Natija:
#    ✅ forecast_map.png — tayyor xarita!
```

## 📋 Sinoptik uchun foydalanish

### Variant A: CSV fayldan (eng oson!)

`prognoz.csv` faylni Excel yoki oddiy matn muharririda to'ldiring:

```csv
shahar,temp_min,temp_max,wind,precip,weather
Toshkent,22,36,12,0,ochiq
Samarqand,18,33,8,0,az_bulutli
Buxoro,24,40,15,0,ochiq
...
```

Keyin:
```bash
python generate_map.py --csv prognoz.csv
```

### Variant B: JSON fayldan

```bash
python generate_map.py --input sample_input.json
```

### Variant C: 3 kunlik xaritalar (bir yo'la)

```bash
python generate_map.py --3day
# Natija: output/prognoz_kun_1.png, prognoz_kun_2.png, prognoz_kun_3.png
```

## 🎨 Ob-havo turlari (weather ustuni)

| Kod | Tavsif |
|-----|--------|
| `ochiq` | ☀ Ochiq havo |
| `az_bulutli` | 🌤 Az bulutli |
| `bulutli` | ☁ Bulutli |
| `toliq_bulut` | 🌥 To'liq bulutli |
| `tuman` | 🌫 Tuman |
| `yomgir` | 🌧 Yomg'ir |
| `kuchli_yomgir` | ⛈ Kuchli yomg'ir |
| `qor` | ❄ Qor |
| `shamol` | 💨 Kuchli shamol |
| `dol` | 🌨 Do'l |

## 🖼️ Xarita xususiyatlari

- **Professional dizayn** — qorong'u fon, gradient harorat xaritasi
- **Harorat interpolatsiyasi** — shaharlar orasidagi gradient (SciPy IDW)
- **Cartopy** — professional kartografik proyeksiya
- **Ob-havo ikonkalari** — har shahar uchun vizual belgi
- **Izoh** — sinoptik izohi xaritada ko'rinadi
- **Rang skalasi** — professional meteorologik rang palitrasik
- **Yuqori sifat** — 200 DPI (Telegram va sayt uchun ideal)

## 📐 Arxitektura

```
Sinoptik:
  Excel/CSV → raqamlar kiritadi
       ↓
  python generate_map.py --csv prognoz.csv
       ↓
  forecast_map.png (professional xarita)
       ↓
  Telegram kanalga yuborish
```

## 🔄 Avtomatlashtirish (kelajak)

```python
# Cron job (har kuni ertalab 6:00 da)
# crontab -e:
# 0 6 * * * cd /path/to/python_map && python generate_map.py --csv /data/today.csv
```

## 📦 Talablar

- Python 3.9+
- matplotlib >= 3.7
- numpy >= 1.24
- scipy >= 1.10
- cartopy >= 0.21 (optional — bo'lmasa oddiy xarita)
- Pillow >= 9.5
