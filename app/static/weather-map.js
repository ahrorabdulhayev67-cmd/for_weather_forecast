/**
 * Ob-havo prognozi — v5.0 (Ikki panelli: xarita + kartochkalar)
 * CHAP: O'zbekiston xaritasi (shapefile, ranglar, ikonalar)
 * O'NG: 14 viloyat kartochkasi (4x4 grid)
 */

// ===== HARORAT → RANG =====
function tempToColor(temp) {
    const stops = [
        { t: 10, r: 21, g: 101, b: 192 },
        { t: 16, r: 41, g: 182, b: 246 },
        { t: 22, r: 102, g: 187, b: 106 },
        { t: 28, r: 255, g: 241, b: 118 },
        { t: 34, r: 255, g: 152, b: 0 },
        { t: 40, r: 229, g: 57, b: 53 },
        { t: 46, r: 183, g: 28, b: 28 }
    ];
    if (temp <= stops[0].t) return `rgb(${stops[0].r},${stops[0].g},${stops[0].b})`;
    if (temp >= stops[stops.length - 1].t) {
        const s = stops[stops.length - 1];
        return `rgb(${s.r},${s.g},${s.b})`;
    }
    for (let i = 0; i < stops.length - 1; i++) {
        if (temp >= stops[i].t && temp <= stops[i + 1].t) {
            const ratio = (temp - stops[i].t) / (stops[i + 1].t - stops[i].t);
            const r = Math.round(stops[i].r + (stops[i + 1].r - stops[i].r) * ratio);
            const g = Math.round(stops[i].g + (stops[i + 1].g - stops[i].g) * ratio);
            const b = Math.round(stops[i].b + (stops[i + 1].b - stops[i].b) * ratio);
            return `rgb(${r},${g},${b})`;
        }
    }
    return '#66BB6A';
}

// ===== IKONKA =====
const WEATHER_ICON_FILES = {
    "ochiq": "sun.svg", "qisman_bulutli": "partly-cloudy-day.svg",
    "bulutli": "overcast.svg", "yomgir": "rain.svg",
    "jala": "drizzle.svg", "momaqaldiroq": "thunderstorms-rain.svg",
    "qor": "snow.svg", "tuman": "fog.svg", "dol": "hail.svg",
    "chang_boroni": "dust.svg", "qor_boroni": "overcast-snow.svg"
};
const WEATHER_LABELS_UZ = {
    "ochiq": "Quyoshli", "qisman_bulutli": "Qisman bulutli",
    "bulutli": "Bulutli", "yomgir": "Yomg'ir", "jala": "Jala",
    "momaqaldiroq": "Momaqaldiroq", "qor": "Qor", "tuman": "Tuman",
    "dol": "Do'l", "chang_boroni": "Chang", "qor_boroni": "Qor bo'roni"
};
let iconCache = {};

async function loadIconsAsDataURIs() {
    const promises = Object.entries(WEATHER_ICON_FILES).map(async ([key, filename]) => {
        try {
            const resp = await fetch(`/static/icons/${filename}`);
            if (resp.ok) {
                const svgText = await resp.text();
                iconCache[key] = `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svgText)))}`;
            }
        } catch (e) { /* skip */ }
    });
    await Promise.all(promises);
}

// ===== XARITA LABELLARI (faqat katta viloyatlar uchun) =====
// Farg'ona vodiysi labellar O'NG PANELda ko'rsatiladi, xaritada emas
const MAP_LABELS = {
    "Nukus": { dx: 0, dy: -8, show: true },
    "Urganch": { dx: 0, dy: 5, show: true },
    "Buxoro": { dx: 0, dy: 0, show: true },
    "Navoiy": { dx: 0, dy: -5, show: true },
    "Samarqand": { dx: 0, dy: 5, show: true },
    "Jizzax": { dx: 0, dy: -8, show: true },
    "Guliston": { dx: 15, dy: 0, show: true },
    "Toshkent": { dx: -10, dy: -12, show: true },
    "Qarshi": { dx: 0, dy: 0, show: true },
    "Termiz": { dx: 0, dy: 5, show: true },
    // Farg'ona vodiysi — faqat nuqta, label yo'q (o'ng panelda)
    "Namangan": { dx: 0, dy: -6, show: false },
    "Andijon": { dx: 0, dy: 0, show: false },
    "Farg'ona": { dx: 0, dy: 0, show: false },
};

// ===== COLORBAR =====
function renderColorbar(x, y, width, height) {
    const temps = [10, 14, 18, 22, 26, 30, 34, 38, 42, 46];
    const segW = width / (temps.length - 1);
    let s = '';
    s += `<rect x="${x - 5}" y="${y - 22}" width="${width + 10}" height="${height + 38}" rx="5" fill="rgba(255,255,255,0.92)" stroke="#B0C4DE" stroke-width="0.8"/>`;
    s += `<text x="${x + width / 2}" y="${y - 6}" text-anchor="middle" font-size="9" font-weight="bold" fill="#0B3D91" font-family="Arial,sans-serif">Kunduzgi harorat, °C</text>`;
    for (let i = 0; i < temps.length - 1; i++) {
        s += `<rect x="${x + i * segW}" y="${y}" width="${segW + 0.5}" height="${height}" fill="${tempToColor((temps[i] + temps[i + 1]) / 2)}"/>`;
    }
    s += `<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="none" stroke="#333" stroke-width="0.8"/>`;
    for (let i = 0; i < temps.length; i++) {
        const tx = x + i * segW;
        s += `<text x="${tx}" y="${y + height + 11}" text-anchor="middle" font-size="7.5" fill="#333" font-family="Arial,sans-serif">${temps[i]}°</text>`;
    }
    return s;
}

// ===== O'NG PANEL: VILOYAT KARTOCHKALARI =====
function renderRightPanel(x0, y0, panelW, panelH, weatherData, dateStr) {
    let s = '';
    // Panel background
    s += `<rect x="${x0}" y="${y0}" width="${panelW}" height="${panelH}" rx="10" fill="#F7FBFF" stroke="#0B4EA2" stroke-width="1.5"/>`;

    // Panel header
    s += `<rect x="${x0}" y="${y0}" width="${panelW}" height="50" rx="10" fill="#1a3a6b"/>`;
    s += `<rect x="${x0}" y="${y0 + 35}" width="${panelW}" height="15" fill="#1a3a6b"/>`;
    s += `<text x="${x0 + panelW / 2}" y="${y0 + 25}" text-anchor="middle" font-size="14" font-weight="bold" fill="white" font-family="Arial,sans-serif">VILOYATLAR BO'YICHA PROGNOZ</text>`;
    s += `<text x="${x0 + panelW / 2}" y="${y0 + 43}" text-anchor="middle" font-size="9" fill="rgba(255,255,255,0.7)" font-family="Arial,sans-serif">Ertangi kun uchun / ${dateStr}</text>`;

    // Grid: 3 columns x 5 rows (or 4x4 with last row 2)
    const cols = 3;
    const padX = 8, padY = 8;
    const cardW = (panelW - padX * (cols + 1)) / cols;
    const cardH = 115;
    const startY = y0 + 58;

    const cityOrder = [
        "Toshkent", "Samarqand", "Buxoro",
        "Namangan", "Andijon", "Farg'ona",
        "Qarshi", "Nukus", "Navoiy",
        "Termiz", "Jizzax", "Urganch",
        "Guliston"
    ];

    // Viloyat qisqa nomlari
    const SHORT_NAMES = {
        "Toshkent": "TOSHKENT", "Samarqand": "SAMARQAND", "Buxoro": "BUXORO",
        "Namangan": "NAMANGAN", "Andijon": "ANDIJON", "Farg'ona": "FARG'ONA",
        "Qarshi": "QARSHI", "Nukus": "NUKUS", "Navoiy": "NAVOIY",
        "Termiz": "TERMIZ", "Jizzax": "JIZZAX", "Urganch": "URGANCH",
        "Guliston": "GULISTON"
    };

    const BADGES = {
        "Toshkent": "TV", "Samarqand": "SM", "Buxoro": "BX",
        "Namangan": "NM", "Andijon": "AN", "Farg'ona": "FR",
        "Qarshi": "QR", "Nukus": "NK", "Navoiy": "NV",
        "Termiz": "TZ", "Jizzax": "JZ", "Urganch": "XR",
        "Guliston": "SD"
    };

    cityOrder.forEach((city, idx) => {
        const col = idx % cols;
        const row = Math.floor(idx / cols);
        const cx = x0 + padX + col * (cardW + padX);
        const cy = startY + row * (cardH + padY);

        const w = weatherData[city];
        if (!w) return;

        const weatherType = w.weather || 'ochiq';

        // Card background
        s += `<rect x="${cx}" y="${cy}" width="${cardW}" height="${cardH}" rx="6" fill="white" stroke="#e0e0e0" stroke-width="1"/>`;

        // Header: name + badge
        s += `<text x="${cx + 8}" y="${cy + 16}" font-size="10" font-weight="bold" fill="#1a3a6b" font-family="Arial,sans-serif">${SHORT_NAMES[city] || city.toUpperCase()}</text>`;

        // Badge
        const badge = BADGES[city] || "??";
        s += `<circle cx="${cx + cardW - 16}" cy="${cy + 14}" r="10" fill="#FF9800" opacity="0.85"/>`;
        s += `<text x="${cx + cardW - 16}" y="${cy + 18}" text-anchor="middle" font-size="7.5" font-weight="bold" fill="white" font-family="Arial,sans-serif">${badge}</text>`;

        // Weather icon (36x36)
        const iconX = cx + cardW / 2 - 18;
        const iconY = cy + 24;
        if (iconCache[weatherType]) {
            s += `<image x="${iconX}" y="${iconY}" width="36" height="36" href="${iconCache[weatherType]}"/>`;
        }

        // Day temp (red, bold)
        s += `<text x="${cx + 8}" y="${cy + 78}" font-size="14" font-weight="bold" fill="#C62828" font-family="Arial,sans-serif">${w.temp_min}...${w.temp_max}°C</text>`;

        // Night temp (blue)
        if (w.temp_min != null) {
            s += `<text x="${cx + 8}" y="${cy + 94}" font-size="10" fill="#0D47A1" font-family="Arial,sans-serif">kechasi: ${w.temp_min}°C</text>`;
        }

        // Weather label
        const wLabel = WEATHER_LABELS_UZ[weatherType] || '';
        s += `<text x="${cx + 8}" y="${cy + 108}" font-size="8.5" fill="#546E7A" font-family="Arial,sans-serif">${wLabel}</text>`;
    });

    return s;
}

// ===== ASOSIY RENDER =====
function renderWeatherMap(weatherData, dateStr, title) {
    const W = 1400, H = 750;
    const mapW = 760, panelW = W - mapW - 30;

    // Set viewport for map (left side)
    setMapViewport(30, 85, mapW - 60, H - 170);

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`;

    // Defs
    svg += `<defs><linearGradient id="hG" x1="0%" y1="0%" x2="100%"><stop offset="0%" stop-color="#0B3D91"/><stop offset="100%" stop-color="#1565C0"/></linearGradient></defs>`;

    // Background
    svg += `<rect width="${W}" height="${H}" fill="#EAF4FF"/>`;

    // === HEADER (70px) ===
    svg += `<rect x="0" y="0" width="${W}" height="70" fill="url(#hG)"/>`;

    // Logo (uzhydromet-logo.jpg embedded as image)
    svg += `<image x="12" y="8" width="54" height="54" href="/static/uzhydromet-logo.jpg" preserveAspectRatio="xMidYMid meet"/>`;

    // Header text
    svg += `<text x="75" y="30" font-size="15" font-weight="bold" fill="white" font-family="Arial,sans-serif">O'ZGIDROMET</text>`;
    svg += `<text x="75" y="50" font-size="8.5" fill="rgba(255,255,255,0.8)" font-family="Arial,sans-serif">O'zbekiston Gidrometeorologiya xizmati agentligi</text>`;

    // Center title
    svg += `<text x="${W / 2}" y="30" text-anchor="middle" font-size="20" font-weight="bold" fill="#FFD600" font-family="Arial,sans-serif">OB-HAVO PROGNOZI</text>`;
    svg += `<text x="${W / 2}" y="50" text-anchor="middle" font-size="11" fill="rgba(255,255,255,0.9)" font-family="Arial,sans-serif">${dateStr}</text>`;

    svg += `<text x="${W - 20}" y="40" text-anchor="end" font-size="9.5" fill="rgba(255,255,255,0.7)" font-family="Arial,sans-serif">hydromet.uz</text>`;

    // === LEFT: MAP PANEL ===
    svg += `<rect x="8" y="76" width="${mapW}" height="${H - 84}" rx="10" fill="#F0F7FF" stroke="#0B4EA2" stroke-width="1.5"/>`;

    // Viloyatlar
    for (const [regionId, regionData] of Object.entries(REGIONS)) {
        const city = Object.entries(CITIES).find(([_, c]) => c.region === regionId);
        let fillColor = '#E8F5E9';

        if (city && weatherData[city[0]]) {
            // FIX: temp_max for coloring (matches colorbar which shows daytime temp)
            fillColor = tempToColor(weatherData[city[0]].temp_max);
        }

        let pathD = '';
        for (const ring of regionData.rings) {
            pathD += ringToPath(ring) + ' ';
        }
        svg += `<path d="${pathD.trim()}" fill="${fillColor}" fill-opacity="0.85" stroke="white" stroke-width="2.5" stroke-linejoin="round"/>`;
        svg += `<path d="${pathD.trim()}" fill="none" stroke="#0B4EA2" stroke-width="0.4" stroke-linejoin="round" opacity="0.5"/>`;
    }

    // City markers + labels (only big regions shown on map)
    for (const [cityName, cityData] of Object.entries(CITIES)) {
        const [cx, cy] = geoToSvg(cityData.lon, cityData.lat);
        const w = weatherData[cityName];
        if (!w) continue;

        const labelCfg = MAP_LABELS[cityName] || { dx: 0, dy: 0, show: true };
        const weatherType = w.weather || 'ochiq';

        // City dot
        svg += `<circle cx="${cx}" cy="${cy}" r="3" fill="white" stroke="#0B4EA2" stroke-width="1.5"/>`;

        // Icon (uniform 26px)
        if (iconCache[weatherType]) {
            svg += `<image x="${cx - 13}" y="${cy - 35}" width="26" height="26" href="${iconCache[weatherType]}"/>`;
        }

        if (labelCfg.show) {
            const lx = cx + (labelCfg.dx || 0);
            const ly = cy + (labelCfg.dy || 0);

            // City name (KO'K, bold)
            svg += `<text x="${lx}" y="${ly + 14}" text-anchor="middle" font-size="8" font-weight="bold" fill="#0B3D91" font-family="Arial,sans-serif" stroke="white" stroke-width="2" paint-order="stroke">${cityName}</text>`;

            // Temp (below name, compact)
            const tempStr = `${w.temp_min}...${w.temp_max}°`;
            svg += `<text x="${lx}" y="${ly + 25}" text-anchor="middle" font-size="8" font-weight="bold" fill="#C62828" font-family="Arial,sans-serif" stroke="white" stroke-width="2" paint-order="stroke">${tempStr}</text>`;
        } else {
            // Farg'ona vodiysi: faqat kichik nom
            svg += `<text x="${cx}" y="${cy + 12}" text-anchor="middle" font-size="6.5" fill="#0B3D91" font-family="Arial,sans-serif" stroke="white" stroke-width="1.5" paint-order="stroke">${cityName}</text>`;
        }
    }

    // Colorbar (pastda, xarita ichida)
    svg += renderColorbar(120, H - 50, 400, 12);

    // === RIGHT: VILOYAT KARTOCHKALARI ===
    svg += renderRightPanel(mapW + 18, 76, panelW - 6, H - 84, weatherData, dateStr);

    // === FOOTER ===
    svg += `<text x="${W / 2}" y="${H - 5}" text-anchor="middle" font-size="8" fill="#78909C" font-family="Arial,sans-serif">O'zbekiston Gidrometeorologiya xizmati agentligi • hydromet.uz • t.me/uzhydromet</text>`;

    svg += '</svg>';
    return svg;
}

// ===== YUKLAB OLISH =====
function downloadMapAsPng(svgElement, filename) {
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);
    const img = new Image();
    img.onload = function() {
        const canvas = document.createElement('canvas');
        canvas.width = 1400 * 2; canvas.height = 750 * 2;
        const ctx = canvas.getContext('2d');
        ctx.scale(2, 2); ctx.drawImage(img, 0, 0);
        canvas.toBlob(function(blob) {
            const link = document.createElement('a');
            link.download = filename || 'ob-havo-prognozi.png';
            link.href = URL.createObjectURL(blob);
            link.click(); URL.revokeObjectURL(link.href);
        }, 'image/png');
        URL.revokeObjectURL(url);
    };
    img.src = url;
}

function downloadMapAsSvg(svgContent, filename) {
    const blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' });
    const link = document.createElement('a');
    link.download = filename || 'ob-havo-prognozi.svg';
    link.href = URL.createObjectURL(blob);
    link.click(); URL.revokeObjectURL(link.href);
}
