/**
 * Ob-havo prognozi xarita generatori v4.0
 * Barcha kamchiliklar tuzatildi:
 * 1) Ranglar: O'RTACHA harorat (min+max)/2 asosida
 * 2) Labellar: katta offsetlar, ustma-ust tushmasligi uchun
 * 3) Kontrast: oq fon + oq stroke barcha matnlar uchun
 * 4) Colorbar: katta, yuqorida, o'qiladigan
 * 5) Header: logo joy + professional dizayn
 */

// ===== HARORAT RANGLARI =====
function tempToGradientColor(temp) {
    const stops = [
        { t: 10, r: 21, g: 101, b: 192 },   // #1565C0
        { t: 16, r: 41, g: 182, b: 246 },   // #29B6F6
        { t: 22, r: 102, g: 187, b: 106 },  // #66BB6A
        { t: 28, r: 255, g: 241, b: 118 },  // #FFF176
        { t: 34, r: 255, g: 152, b: 0 },    // #FF9800
        { t: 40, r: 229, g: 57, b: 53 },    // #E53935
        { t: 46, r: 183, g: 28, b: 28 }     // #B71C1C
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

// ===== IKONKA MAPPING =====
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
        } catch (e) { /* skip */ }
    });
    await Promise.all(promises);
}

// ===== LABEL OFFSETLAR (katta, ustma-ust tushmasligi uchun) =====
const LABEL_OFFSETS = {
    "Nukus":      { dx: 0, dy: -20 },
    "Urganch":    { dx: -30, dy: 20 },
    "Buxoro":     { dx: -15, dy: 15 },
    "Navoiy":     { dx: 0, dy: -15 },
    "Samarqand":  { dx: -10, dy: 20 },
    "Jizzax":     { dx: 15, dy: -30 },
    "Guliston":   { dx: 50, dy: -15 },
    "Toshkent":   { dx: -55, dy: -35 },
    "Namangan":   { dx: 30, dy: -35 },
    "Andijon":    { dx: 55, dy: -10 },
    "Farg'ona":   { dx: 55, dy: 25 },
    "Qarshi":     { dx: 0, dy: 15 },
    "Termiz":     { dx: 0, dy: 15 },
};

// ===== COLORBAR =====
function renderColorbar(x, y, width, height) {
    const temps = [10, 14, 18, 22, 26, 30, 34, 38, 42, 46];
    const segW = width / (temps.length - 1);
    let svg = '';

    // Background panel
    svg += `<rect x="${x - 10}" y="${y - 28}" width="${width + 20}" height="${height + 50}" rx="6" fill="rgba(255,255,255,0.9)" stroke="#B0C4DE" stroke-width="1"/>`;

    // Title
    svg += `<text x="${x + width / 2}" y="${y - 10}" text-anchor="middle" font-size="11" font-weight="bold" fill="#0B3D91" font-family="Arial, sans-serif">Kunduzgi harorat, °C</text>`;

    // Color segments
    for (let i = 0; i < temps.length - 1; i++) {
        const color = tempToGradientColor((temps[i] + temps[i + 1]) / 2);
        svg += `<rect x="${x + i * segW}" y="${y}" width="${segW + 0.5}" height="${height}" fill="${color}"/>`;
    }

    // Border
    svg += `<rect x="${x}" y="${y}" width="${width}" height="${height}" fill="none" stroke="#455a64" stroke-width="1.2"/>`;

    // Tick marks and labels
    for (let i = 0; i < temps.length; i++) {
        const tx = x + i * segW;
        svg += `<line x1="${tx}" y1="${y + height}" x2="${tx}" y2="${y + height + 5}" stroke="#333" stroke-width="1"/>`;
        svg += `<text x="${tx}" y="${y + height + 16}" text-anchor="middle" font-size="9.5" font-weight="500" fill="#1a2332" font-family="Arial, sans-serif">${temps[i]}°</text>`;
    }

    return svg;
}

// ===== LABEL BILAN OQ FON (kontrast uchun) =====
function labelWithBg(x, y, text, fontSize, color, bold, anchor) {
    const weight = bold ? 'bold' : 'normal';
    const approxWidth = text.length * fontSize * 0.55 + 8;
    const h = fontSize + 4;
    let lx = x;
    if (anchor === 'middle') lx = x - approxWidth / 2;
    else if (anchor === 'end') lx = x - approxWidth;

    let svg = '';
    // Oq fon (rounded)
    svg += `<rect x="${lx}" y="${y - h + 2}" width="${approxWidth}" height="${h}" rx="3" fill="rgba(255,255,255,0.88)" stroke="rgba(0,0,0,0.06)" stroke-width="0.5"/>`;
    // Matn (oq stroke bilan ham)
    svg += `<text x="${x}" y="${y}" text-anchor="${anchor}" font-size="${fontSize}" font-weight="${weight}" fill="${color}" font-family="Arial, sans-serif" stroke="white" stroke-width="2.5" stroke-linejoin="round" paint-order="stroke">${text}</text>`;
    return svg;
}

// ===== ASOSIY RENDER =====
function renderWeatherMap(weatherData, dateStr, title) {
    const svgWidth = 1200;
    const svgHeight = 850;
    const iconSize = 28;

    let svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">`;

    // === DEFS ===
    svg += `<defs>`;
    svg += `<linearGradient id="hdrG" x1="0%" y1="0%" x2="100%"><stop offset="0%" stop-color="#0B3D91"/><stop offset="100%" stop-color="#1565C0"/></linearGradient>`;
    svg += `<linearGradient id="mapBg" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#EEF6FF"/><stop offset="100%" stop-color="#DCE8F4"/></linearGradient>`;
    svg += `</defs>`;

    // === BACKGROUND ===
    svg += `<rect width="${svgWidth}" height="${svgHeight}" fill="#EAF4FF"/>`;

    // === MAIN PANEL ===
    svg += `<rect x="12" y="12" width="${svgWidth - 24}" height="${svgHeight - 24}" rx="14" fill="#F7FBFF" stroke="#0B4EA2" stroke-width="2.5"/>`;

    // === HEADER (75px) ===
    svg += `<rect x="12" y="12" width="${svgWidth - 24}" height="75" rx="14" fill="url(#hdrG)"/>`;
    svg += `<rect x="12" y="62" width="${svgWidth - 24}" height="25" fill="url(#hdrG)"/>`;

    // Logo circle placeholder
    svg += `<circle cx="55" cy="50" r="22" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/>`;
    svg += `<text x="55" y="45" text-anchor="middle" font-size="7" fill="rgba(255,255,255,0.9)" font-family="Arial, sans-serif">O'Z</text>`;
    svg += `<text x="55" y="56" text-anchor="middle" font-size="6" fill="rgba(255,255,255,0.7)" font-family="Arial, sans-serif">GIDRO</text>`;

    // Title text
    svg += `<text x="90" y="43" font-size="16" font-weight="bold" fill="white" font-family="Arial, sans-serif">O'ZGIDROMET</text>`;
    svg += `<text x="90" y="62" font-size="8.5" fill="rgba(255,255,255,0.8)" font-family="Arial, sans-serif">O'zbekiston Gidrometeorologiya xizmati agentligi</text>`;

    // Center title
    svg += `<text x="${svgWidth / 2}" y="43" text-anchor="middle" font-size="22" font-weight="bold" fill="#FFD600" font-family="Arial, sans-serif">OB-HAVO PROGNOZI</text>`;
    svg += `<text x="${svgWidth / 2}" y="64" text-anchor="middle" font-size="12" fill="rgba(255,255,255,0.9)" font-family="Arial, sans-serif">${dateStr || ''}</text>`;

    // Right badge
    svg += `<text x="${svgWidth - 40}" y="50" text-anchor="end" font-size="10" fill="rgba(255,255,255,0.75)" font-family="Arial, sans-serif">hydromet.uz</text>`;

    // === MAP AREA ===
    const mapTop = 95;
    const mapBottom = svgHeight - 105;
    svg += `<rect x="25" y="${mapTop}" width="${svgWidth - 50}" height="${mapBottom - mapTop}" rx="8" fill="url(#mapBg)"/>`;

    // === VILOYATLAR ===
    for (const [regionId, regionData] of Object.entries(REGIONS)) {
        const city = Object.entries(CITIES).find(([_, c]) => c.region === regionId);
        let fillColor = '#E8F5E9';

        if (city && weatherData[city[0]]) {
            const d = weatherData[city[0]];
            // FIX #1: O'RTACHA harorat (min+max)/2 asosida ranglash
            const avgTemp = (d.temp_min != null && d.temp_max != null)
                ? (d.temp_min + d.temp_max) / 2
                : (d.temp_max || 25);
            fillColor = tempToGradientColor(avgTemp);
        }

        let pathD = '';
        for (const ring of regionData.rings) {
            pathD += ringToPath(ring) + ' ';
        }
        // Oq chegara (qalin) + ingichka ko'k outline
        svg += `<path d="${pathD.trim()}" fill="${fillColor}" fill-opacity="0.85" stroke="white" stroke-width="2.8" stroke-linejoin="round"/>`;
        svg += `<path d="${pathD.trim()}" fill="none" stroke="#0B4EA2" stroke-width="0.5" stroke-linejoin="round" stroke-opacity="0.5"/>`;
    }

    // === SHAHAR LABELLARI ===
    for (const [cityName, cityData] of Object.entries(CITIES)) {
        let [cx, cy] = geoToSvg(cityData.lon, cityData.lat);
        const weather = weatherData[cityName];
        if (!weather) continue;

        const offset = LABEL_OFFSETS[cityName] || { dx: 0, dy: 0 };
        const lx = cx + offset.dx;
        const ly = cy + offset.dy;

        const weatherType = weather.weather || 'ochiq';
        const tmin = weather.temp_min;
        const tmax = weather.temp_max;

        // Connection line (shahar nuqtasidan labelgacha)
        if (offset.dx !== 0 || offset.dy !== 0) {
            svg += `<line x1="${cx}" y1="${cy}" x2="${lx}" y2="${ly - 20}" stroke="#0B4EA2" stroke-width="0.7" stroke-opacity="0.4" stroke-dasharray="2,2"/>`;
        }

        // Shahar nuqtasi
        svg += `<circle cx="${cx}" cy="${cy}" r="3.5" fill="white" stroke="#0B4EA2" stroke-width="1.8"/>`;

        // FIX #3: OQ FON bilan label guruhi
        // Viloyat nomi
        const regionName = REGIONS[cityData.region] ? REGIONS[cityData.region].name : cityName;
        let shortName = regionName;
        if (shortName.length > 16) shortName = shortName.substring(0, 14) + '.';
        svg += labelWithBg(lx, ly - 32, shortName, 8.5, '#0B3D91', true, 'middle');

        // Ob-havo ikonkasi
        if (iconCache[weatherType]) {
            svg += `<image x="${lx - iconSize / 2}" y="${ly - 28}" width="${iconSize}" height="${iconSize}" href="${iconCache[weatherType]}"/>`;
        }

        // Kunduzi harorat (QIZIL, oq fon bilan)
        const dayStr = (tmin != null) ? `${tmin}...${tmax}°` : `${tmax}°`;
        svg += labelWithBg(lx, ly + 12, dayStr, 11, '#C62828', true, 'middle');

        // Kechasi (KO'K, oq fon bilan)
        if (tmin != null) {
            svg += labelWithBg(lx, ly + 27, `kechasi ${tmin}°`, 8.5, '#0D47A1', false, 'middle');
        }
    }

    // === COLORBAR (katta, yuqoriga ko'tarilgan) ===
    svg += renderColorbar(250, svgHeight - 90, 500, 16);

    // === FOOTER ===
    svg += `<text x="${svgWidth / 2}" y="${svgHeight - 22}" text-anchor="middle" font-size="9.5" fill="#546E7A" font-family="Arial, sans-serif">O'zbekiston Gidrometeorologiya xizmati agentligi  •  hydromet.uz  •  t.me/uzhydromet</text>`;

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
        canvas.width = 1200 * 2;
        canvas.height = 850 * 2;
        const ctx = canvas.getContext('2d');
        ctx.scale(2, 2);
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
