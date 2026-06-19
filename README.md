# O'zgidromet — Interaktiv Ob-havo Xaritasi (Prototip)

O'zbekiston Gidrometeorologiya xizmati uchun zamonaviy interaktiv ob-havo prognoz tizimi prototipi.

## 📁 Fayllar tuzilmasi

```
uzhydromet-interactive-map/
├── index.html        — Asosiy interaktiv xarita (Leaflet + Open-Meteo)
├── styles.css        — Asosiy sahifa stillari
├── app.js            — JavaScript logikasi
├── heatmap.html      — Harorat/shamol/yog'ingarchilik overlay xaritasi (IDW interpolatsiya)
├── windy-embed.html  — Windy.com embed integratsiya namunasi
└── README.md         — Shu fayl
```

## 🚀 3 ta yondashuv taqqoslashi

### 1️⃣ Asosiy interaktiv xarita (`index.html`)

**Texnologiyalar:** Leaflet.js + Open-Meteo API (bepul, API key shart emas)

**Imkoniyatlar:**
- 18 ta O'zbekiston shahri real-vaqt ob-havo ma'lumotlari bilan
- Harorat / Shamol / Yog'ingarchilik / Namlik qatlamlari
- Shahar markerini bosganda — batafsil ma'lumot + 7 kunlik prognoz
- Responsive dizayn (mobil va desktop)
- O'zbek tilida to'liq lokalizatsiya

**Afzalliklari:** To'liq nazorat, o'z brendingiz, bepul API, kengaytirish oson
**Kamchiliklari:** Ishlab chiqish vaqti ko'proq, server kerak

---

### 2️⃣ Heatmap overlay (`heatmap.html`)

**Texnologiyalar:** Leaflet.js + Canvas IDW interpolatsiya + Open-Meteo

**Imkoniyatlar:**
- Harorat, bulutlilik, yog'ingarchilik, shamol, bosim overlaylari
- IDW (Inverse Distance Weighting) algoritmi bilan silliq gradient
- Real ma'lumotlar asosida rangli xarita
- 5 xil qatlam o'rtasida bir tugma bilan almashtirish

**Afzalliklari:** Professional ko'rinish (Windy ga o'xshash), API key kerak emas
**Kamchiliklari:** Aniqlik stansiyalar soniga bog'liq, hisoblash yuklamasi

---

### 3️⃣ Windy.com embed (`windy-embed.html`)

**Texnologiyalar:** Windy.com iframe embed

**Imkoniyatlar:**
- ECMWF, GFS, ICON prognoz modellari
- Shamol animatsiyasi, bulut harakati
- 10 kunlik prognoz, vaqt o'tkazgichi
- Mobilda mukammal ishlash

**Afzalliklari:** 5 daqiqada tayyor, server kerak emas, yuqori aniqlik
**Kamchiliklari:** Windy brendingi, dizayn nazorati yo'q, bog'liqlik

---

## 📊 Tavsiya (strategiya)

| Maqsad | Tavsiya etiladigan yondashuv |
|--------|------------------------------|
| Tezkor natija (1 hafta) | Windy embed + Telegram Mini App |
| O'rta muddatli (1-2 oy) | Leaflet + Open-Meteo (index.html asosida) |
| Professional tizim (3-6 oy) | Heatmap + o'z backend + O'zgidromet API |

## 🛠️ Ishga tushirish

Brauzarda ochish uchun istalgan `.html` faylni to'g'ridan-to'g'ri oching, yoki:

```bash
# Python orqali lokal server
cd uzhydromet-interactive-map
python3 -m http.server 8080
# Brauzerda: http://localhost:8080
```

## 🌐 Texnologiyalar

- **[Leaflet.js](https://leafletjs.com/)** — ochiq kodli interaktiv xarita kutubxonasi
- **[Open-Meteo](https://open-meteo.com/)** — bepul ob-havo API (API key shart emas)
- **[OpenStreetMap](https://www.openstreetmap.org/)** — bepul xarita tile'lar
- **[Windy.com](https://www.windy.com/)** — professional ob-havo vizualizatsiya

## 📱 Telegram integratsiya strategiyasi

1. **Hozir:** Windy embed sahifasini Telegram Mini App sifatida bog'lash
2. **Keyinroq:** `index.html` ni Telegram Web App sifatida ishlatish
3. **Ideal:** Bot + Mini App + Push notification ogohlantirish tizimi

---

*Prototip — 2026 | Open-Meteo API (bepul, API key shart emas)*
