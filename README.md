# Gidrometeorologiya xizmati — Qisqa muddatli prognoz tizimi

Sinoptik jadvalga raqamlarni kiritadi → tizim professional ob-havo xaritasini avtomatik shakllantiradi.

## Arxitektura

```
Sinoptik (brauzer)
    │
    ▼
┌─────────────────────────────────┐
│  HTML interfeys                 │
│  • 3 kunlik jadval              │
│  • Ob-havo hodisasi tanlash     │
│  • Sinoptik izohi               │
│  └── "Shakllantirish" tugmasi   │
└───────────────┬─────────────────┘
                │ POST /api/generate
                ▼
┌─────────────────────────────────┐
│  Flask server (Python)          │
│  • map_renderer.py              │
│  • Matplotlib + SciPy           │
│  • IDW interpolatsiya           │
│  • Professional dizayn          │
│  └── PNG xarita + TG matn      │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│  Natija                         │
│  • PNG xarita (yuklab olish)    │
│  • Telegram matn (nusxa olish)  │
└─────────────────────────────────┘
```

## Ishga tushirish

```bash
cd app
pip install -r requirements.txt
python server.py
# Brauzerda: http://localhost:5000
```

## Ob-havo hodisalari klassifikatsiyasi

WMO va O'zgidromet amaliyotiga mos terminologiya:

| Kod | Hodisa | Tavsif |
|-----|--------|--------|
| `ochiq` | Havo ochiq | Bulutlilik 0–2 ball |
| `qisman_bulutli` | Qisman bulutli | Bulutlilik 3–7 ball |
| `bulutli` | Bulutli | Bulutlilik 8–10 ball |
| `tuman` | Tuman | Ko'rinish < 1 km |
| `yomgir` | Yomg'ir | Uzluksiz yog'ingarchilik |
| `jala` | Jala | Qisqa muddatli kuchli yog'in |
| `momaqaldiroq` | Momaqaldiroq | Chaqmoq va kuchli yog'in |
| `qor` | Qor | Qattiq yog'ingarchilik |
| `dol` | Do'l | Muz parchalari tushishi |
| `chang_boroni` | Chang bo'roni | Ko'rinish < 1 km, shamol > 15 m/s |
| `qor_boroni` | Qor bo'roni | Kuchli shamol + qor yog'ishi |

## Texnologiyalar

- Python 3.11+ / Flask
- Matplotlib (xarita rendering)
- SciPy (harorat interpolatsiyasi)
- Vanilla JavaScript (frontend)
