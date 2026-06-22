/**
 * Ob-havo prognozi xarita generatori v3.0
 * Reference: Pragnoz uchun.txt dizayni asosida
 * - Haqiqiy shapefile chegaralari
 * - Ko'k->yashil->sariq->qizil gradient (2°C oraliq)
 * - Meteocons SVG ikonkalar
 * - Viloyat nomlari + harorat + shamol labellari
 * - Professional O'zgidromet header/footer
 */

// ===== HARORAT RANGLARI (Reference: LinearSegmentedColormap) =====
// Ko'k → moviy → yashil → sariq → to'q sariq → qizil gradient
function tempToGradientColor(temp) {
    const stops = [
        { t: 10, r: 21, g: 101, b: 192 },   // #1565C0 ko'k
        { t: 16, r: 41, g: 182, b: 246 },   // #29B6F6 moviy
        { t: 22, r: 102, g: 187, b: 106 },  // #66BB6A yashil
        { t: 28, r: 255, g: 241, b: 118 },  // #FFF176 sariq
        { t: 34, r: 255, g: 152, b: 0 },    // #FF9800 to'q sariq
        { t: 40, r: 229, g: 57, b: 53 },    // #E53935 qizil
        { t: 46, r: 183, g: 28, b: 28 }     // #B71C1C to'q qizil
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

// ===== OB-HAVO IKONKA MAPPING =====
const WEATHER_ICON_FILES = {
    "ochiq": "sun.svg",
    "qisman_bulutli": "partly-cloudy-day.svg",
    "bulutli": "overcast.svg",
    "yomgir": "rain.svg",
    "jala": "drizzle.svg",
    "momaqaldiroq": "thunderstorms-rain.svg",
    "qor": "snow.svg",
    "tuman": "fog.svg",
    "dol": "hail.svg",
    "chang_boroni": "dust.svg",
    "qor_boroni": "overcast-snow.svg"
};

let iconCache = {};

async function loadIconsAsDataURIs() {
    const promises = Object.entries(WEATHER_ICON_FILES).map(async ([key, filename]) => {
        try {
            const response = await fetch(`/static/icons/${filename}`);
            if (response.ok) {
                const svgText = await response.text();
                const encoded = btoa(unescape(encodeURIComponent(svgText)));
                iconCache[key] = `data:image/svg+xml;base64,${encoded}`;
            }
        } catch (e) {
            console.warn(`Could not load icon: ${filename}`, e);
        }
    });
    await Promise.all(promises);
}

// ===== VILOYAT NOMI SILJITISHLARI (reference koddan) =====
const LABEL_OFFSETS = {
    "Nukus": { dx: 0, dy: -15 },
    "Urganch": { dx: -15, dy: 10 },
    "Buxoro": { dx: 0, dy: -5 },
    "Navoiy": { dx: 0, dy: -10 },
    "Samarqand": { dx: 0, dy: 5 },
    "Jizzax": { dx: 0, dy: -5 },
    "Guliston": { dx: 20, dy: -5 },
    "Toshkent": { dx: -20, dy: -20 },
    "Namangan": { dx: 15, dy: -18 },
    "Andijon": { dx: 25, dy: 0 },
    "Farg'ona": { dx: 25, dy: 10 },
    "Qarshi": { dx: 0, dy: -5 },
    "Termiz": { dx: 0, dy: 5 },
};

// ===== HORIZONTAL COLORBAR =====
function renderColorbar(x, y, width, height) {
    const temps = [10, 14, 18, 22, 26, 30, 34, 38, 42, 46];
    const segW = width / (temps.length - 1);
    let svg = '';

    // Label
    svg += `<text x="${x + width / 2}" y="${y - 8}" text-anchor="middle" font-size="10" font-weight="bold" fill="#0B3D91" font-family="Arial, sans-serif">Harorat, °C</text>`;

    // Color segments
    for (let i = 0; i < temps.length - 1; i++) {
        const color = tempToGradientColor((temps[i] + temps[i + 1]) / 2);
        svg += `<rect x="${x + i * segW}" y="${y}" width="${segW + 0.5}" height="${height}" fill="${color}"/>`;
    }

    // Border
    svg += `<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="none" stroke="#455a64" stroke-width="1"/>`;

    // Tick labels
    for (let i = 0; i < temps.length; i++) {
        const tx = x + i * segW;
        svg += `<line x1="${tx}" y1="${y + height}" x2="${tx}" y2="${y + height + 4}" stroke="#455a64" stroke-width="0.8"/>`;
        svg += `<text x="${tx}" y="${y + height + 14}" text-anchor="middle" font-size="8" fill="#37474f" font-family="Arial, sans-serif">${temps[i]}°</text>`;
    }

    return svg;
}

// ===== ASOSIY XARITA RENDERI =====
function renderWeatherMap(weatherData, dateStr, title) {
    const svgWidth = 1200;
    const svgHeight = 800;
    const iconSize = 30;

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">`;

    // === DEFS ===
    svg += `<defs>`;
    svg += `<linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#0B3D91"/><stop offset="100%" stop-color="#1565C0"/></linearGradient>`;
    svg += `<linearGradient id="mapBg" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#EAF4FF"/><stop offset="100%" stop-color="#D4E8F8"/></linearGradient>`;
    svg += `<filter id="shadow" x="-2%" y="-2%" width="104%" height="104%"><feDropShadow dx="0" dy="1" stdDeviation="2" flood-opacity="0.1"/></filter>`;
    svg += `</defs>`;

    // === BACKGROUND ===
    svg += `<rect width="${svgWidth}" height="${svgHeight}" fill="#EAF4FF"/>`;

    // === MAIN PANEL (reference: rounded box with border) ===
    svg += `<rect x="15" y="15" width="${svgWidth - 30}" height="${svgHeight - 30}" rx="12" fill="#F7FBFF" stroke="#0B4EA2" stroke-width="2.5"/>`;

    // === HEADER ===
    svg += `<rect x="15" y="15" width="${svgWidth - 30}" height="65" rx="12" fill="url(#headerGrad)"/>`;
    svg += `<rect x="15" y="55" width="${svgWidth - 30}" height="25" fill="url(#headerGrad)"/>`;

    // Logo text
    svg += `<text x="40" y="42" font-size="18" font-weight="bold" fill="white" font-family="Arial, sans-serif">O'ZGIDROMET</text>`;
    svg += `<text x="40" y="62" font-size="9" fill="rgba(255,255,255,0.8)" font-family="Arial, sans-serif">O'ZBEKISTON GIDROMETEOROLOGIYA XIZMATI</text>`;

    // Title center
    svg += `<text x="${svgWidth / 2}" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="#FFD600" font-family="Arial, sans-serif">HARORAT XARITASI</text>`;
    svg += `<text x="${svgWidth / 2}" y="62" text-anchor="middle" font-size="11" fill="rgba(255,255,255,0.9)" font-family="Arial, sans-serif">${dateStr || ''}</text>`;

    // Date badge right
    svg += `<text x="${svgWidth - 40}" y="48" text-anchor="end" font-size="10" fill="rgba(255,255,255,0.8)" font-family="Arial, sans-serif">hydromet.uz</text>`;

    // === MAP AREA ===
    svg += `<rect x="30" y="90" width="${svgWidth - 60}" height="${svgHeight - 160}" rx="8" fill="url(#mapBg)"/>`;

    // === VILOYATLAR (haqiqiy shapefile) ===
    for (const [regionId, regionData] of Object.entries(REGIONS)) {
        const city = Object.entries(CITIES).find(([_, c]) => c.region === regionId);
        let fillColor = '#E8F5E9';

        if (city && weatherData[city[0]]) {
            const tempMax = weatherData[city[0]].temp_max;
            const tempMin = weatherData[city[0]].temp_min;
            // Use max temp for coloring (reference uses day temp)
            fillColor = tempToGradientColor(tempMax);
        }

        let pathD = '';
        for (const ring of regionData.rings) {
            pathD += ringToPath(ring) + ' ';
        }
        // Thicker white border first, then colored border (like reference)
        svg += `<path d="${pathD.trim()}" fill="${fillColor}" fill-opacity="0.88" stroke="white" stroke-width="2.5" stroke-linejoin="round"/>`;
        svg += `<path d="${pathD.trim()}" fill="none" stroke="#0B4EA2" stroke-width="0.4" stroke-linejoin="round" stroke-opacity="0.6"/>`;
    }

    // === SHAHAR BELGILARI + HARORAT + IKONKALAR ===
    for (const [cityName, cityData] of Object.entries(CITIES)) {
        let [cx, cy] = geoToSvg(cityData.lon, cityData.lat);
        const weather = weatherData[cityName];
        if (!weather) continue;

        // Apply offset
        const offset = LABEL_OFFSETS[cityName] || { dx: 0, dy: 0 };
        const lx = cx + offset.dx;
        const ly = cy + offset.dy;

        const weatherType = weather.weather || 'ochiq';
        const tmin = weather.temp_min;
        const tmax = weather.temp_max;

        // --- Viloyat nomi (yuqorida, bold, kichik) ---
        const regionName = REGIONS[cityData.region] ? REGIONS[cityData.region].name : cityName;
        const shortName = regionName.length > 14 ? regionName.substring(0, 12) + '.' : regionName;
        svg += `<text x="${lx}" y="${ly - 38}" text-anchor="middle" font-size="8.5" font-weight="bold" fill="#0B3D91" font-family="Arial, sans-serif">${shortName}</text>`;

        // --- Ob-havo ikonkasi ---
        if (iconCache[weatherType]) {
            svg += `<image x="${lx - iconSize / 2}" y="${ly - 34}" width="${iconSize}" height="${iconSize}" href="${iconCache[weatherType]}"/>`;
        }

        // --- Shahar nuqtasi ---
        svg += `<circle cx="${cx}" cy="${cy}" r="3.5" fill="white" stroke="#0B4EA2" stroke-width="1.5"/>`;

        // --- Kunduzi harorat (qizil, bold) ---
        const dayStr = (tmin !== undefined && tmin !== null)
            ? `${tmin}...${tmax}°C`
            : `${tmax}°C`;
        svg += `<text x="${lx}" y="${ly + 12}" text-anchor="middle" font-size="10.5" font-weight="bold" fill="#E53935" font-family="Arial, sans-serif">${dayStr}</text>`;

        // --- Kechasi harorat (ko'k, kichikroq) ---
        if (tmin !== undefined && tmin !== null) {
            svg += `<text x="${lx}" y="${ly + 25}" text-anchor="middle" font-size="8.5" fill="#1565C0" font-family="Arial, sans-serif">kechasi: ${tmin}°C</text>`;
        }
    }

    // === COLORBAR (pastda, horizontal) ===
    svg += renderColorbar(200, svgHeight - 55, 500, 14);

    // === FOOTER ===
    svg += `<text x="${svgWidth / 2}" y="${svgHeight - 22}" text-anchor="middle" font-size="9" fill="#546E7A" font-family="Arial, sans-serif">O'zbekiston Gidrometeorologiya xizmati agentligi  |  hydromet.uz  |  t.me/uzhydromet</text>`;

    svg += '</svg>';
    return svg;
}

// ===== PNG YUKLAB OLISH =====
function downloadMapAsPng(svgElement, filename) {
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    const img = new Image();
    img.onload = function() {
        const canvas = document.createElement('canvas');
        const scale = 2;
        canvas.width = 1200 * scale;
        canvas.height = 800 * scale;
        const ctx = canvas.getContext('2d');
        ctx.scale(scale, scale);
        ctx.drawImage(img, 0, 0);

        canvas.toBlob(function(blob) {
            const link = document.createElement('a');
            link.download = filename || 'ob-havo-prognozi.png';
            link.href = URL.createObjectURL(blob);
            link.click();
            URL.revokeObjectURL(link.href);
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
    link.click();
    URL.revokeObjectURL(link.href);
}
