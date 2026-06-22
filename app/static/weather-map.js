/**
 * Ob-havo prognozi xarita generatori
 * SVG asosida viloyat ranglanishi + Meteocons ikonkalar + termometr legend
 * PNG sifatida yuklab olish imkoniyati
 */

// ===== HARORAT RANGLARI =====
function tempToGradientColor(temp) {
    const stops = [
        { t: -10, r: 26, g: 35, b: 126 },
        { t: 0, r: 21, g: 101, b: 192 },
        { t: 10, r: 0, g: 131, b: 143 },
        { t: 18, r: 46, g: 125, b: 50 },
        { t: 25, r: 85, g: 139, b: 47 },
        { t: 30, r: 249, g: 168, b: 37 },
        { t: 35, r: 239, g: 108, b: 0 },
        { t: 40, r: 198, g: 40, b: 40 },
        { t: 48, r: 136, g: 14, b: 79 }
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
    return '#558b2f';
}

// ===== OB-HAVO IKONKA MAPPING =====
// Maps weather type to SVG icon file name
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

// SVG icon content cache (loaded inline for PNG export compatibility)
let iconCache = {};

// Load all icons as inline SVG data URIs for embedding
async function loadIconsAsDataURIs() {
    const promises = Object.entries(WEATHER_ICON_FILES).map(async ([key, filename]) => {
        try {
            const response = await fetch(`/static/icons/${filename}`);
            if (response.ok) {
                const svgText = await response.text();
                // Convert to data URI for use in <image> tags
                const encoded = btoa(unescape(encodeURIComponent(svgText)));
                iconCache[key] = `data:image/svg+xml;base64,${encoded}`;
            }
        } catch (e) {
            console.warn(`Could not load icon: ${filename}`, e);
        }
    });
    await Promise.all(promises);
    console.log(`Loaded ${Object.keys(iconCache).length} weather icons`);
}

// ===== TERMOMETR LEGEND =====
function renderThermometerLegend(x, y, height) {
    const width = 28;
    const temps = [48, 44, 40, 36, 32, 28, 24, 20, 16, 12, 8, 4, 0, -4, -8];
    const segH = height / temps.length;
    
    let svg = '';
    
    // Background panel
    svg += `<rect x="${x - 8}" y="${y - 30}" width="${width + 50}" height="${height + 55}" rx="6" fill="rgba(255,255,255,0.85)" stroke="#c8d8e8" stroke-width="1"/>`;
    
    // Title
    svg += `<text x="${x + width / 2 + 12}" y="${y - 12}" text-anchor="middle" font-size="11" font-weight="bold" fill="#1a3a5c" font-family="Arial, sans-serif">°C</text>`;
    
    // Gradient segments
    temps.forEach((temp, i) => {
        const segY = y + i * segH;
        const color = tempToGradientColor(temp);
        svg += `<rect x="${x}" y="${segY}" width="${width}" height="${segH + 0.5}" fill="${color}"/>`;
        // Temperature label
        svg += `<text x="${x + width + 5}" y="${segY + segH / 2 + 4}" font-size="9" fill="#37474f" font-family="Arial, sans-serif">${temp}°</text>`;
    });
    
    // Border around color bar
    svg += `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="3" ry="3" fill="none" stroke="#455a64" stroke-width="1.5"/>`;
    
    // Thermometer bulb at bottom
    svg += `<circle cx="${x + width / 2}" cy="${y + height + 10}" r="8" fill="#c62828" stroke="#455a64" stroke-width="1.5"/>`;
    svg += `<rect x="${x + width / 2 - 3}" y="${y + height - 2}" width="6" height="12" fill="#c62828"/>`;
    
    return svg;
}

// ===== ASOSIY XARITA RENDERI =====
function renderWeatherMap(weatherData, dateStr, title) {
    const svgWidth = 1200;
    const svgHeight = 750;
    const legendX = svgWidth - 90;
    const legendY = 130;
    const iconSize = 32;
    
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">`;
    
    // Background
    svg += `<rect width="${svgWidth}" height="${svgHeight}" fill="#f0f4f8"/>`;
    
    // Header background with gradient
    svg += `<defs><linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#0d2137"/><stop offset="100%" style="stop-color:#1a3a5c"/></linearGradient></defs>`;
    svg += `<rect x="0" y="0" width="${svgWidth}" height="72" fill="url(#headerGrad)"/>`;
    
    // Logo area
    svg += `<text x="35" y="30" font-size="16" font-weight="bold" fill="white" font-family="Arial, sans-serif">O'ZBEKISTON RESPUBLIKASI</text>`;
    svg += `<text x="35" y="52" font-size="12" fill="rgba(255,255,255,0.85)" font-family="Arial, sans-serif">Gidrometeorologiya xizmati agentligi</text>`;
    
    // Center title
    svg += `<text x="${svgWidth / 2}" y="30" text-anchor="middle" font-size="20" font-weight="bold" fill="#FFD600" font-family="Arial, sans-serif">OB-HAVO PROGNOZI</text>`;
    svg += `<text x="${svgWidth / 2}" y="52" text-anchor="middle" font-size="13" fill="rgba(255,255,255,0.9)" font-family="Arial, sans-serif">${dateStr || ''}</text>`;
    
    // Right side
    svg += `<text x="${svgWidth - 35}" y="42" text-anchor="end" font-size="11" fill="rgba(255,255,255,0.7)" font-family="Arial, sans-serif">hydromet.uz</text>`;
    
    // Map area background
    svg += `<rect x="20" y="82" width="${svgWidth - 135}" height="${svgHeight - 118}" rx="8" fill="#e8f4f8" stroke="#b8d4e8" stroke-width="1"/>`;
    
    // === VILOYATLAR ===
    for (const [regionId, regionData] of Object.entries(REGIONS)) {
        const city = Object.entries(CITIES).find(([_, c]) => c.region === regionId);
        let fillColor = '#dce8d4';
        
        if (city && weatherData[city[0]]) {
            const tempMax = weatherData[city[0]].temp_max;
            const tempMin = weatherData[city[0]].temp_min;
            const avgTemp = tempMin != null ? (tempMin + tempMax) / 2 : tempMax;
            fillColor = tempToGradientColor(avgTemp);
        }
        
        const path = polygonToPath(regionData.polygon);
        svg += `<path d="${path}" fill="${fillColor}" fill-opacity="0.7" stroke="#37474f" stroke-width="1.8" stroke-linejoin="round"/>`;
    }
    
    // === SHAHAR BELGILARI + HARORAT + IKONKALAR ===
    for (const [cityName, cityData] of Object.entries(CITIES)) {
        const [cx, cy] = geoToSvg(cityData.lon, cityData.lat);
        const weather = weatherData[cityName];
        
        if (!weather) continue;
        
        const weatherType = weather.weather || 'ochiq';
        
        // Ob-havo ikonkasi (embedded SVG image)
        if (iconCache[weatherType]) {
            svg += `<image x="${cx - iconSize / 2}" y="${cy - iconSize - 12}" width="${iconSize}" height="${iconSize}" href="${iconCache[weatherType]}"/>`;
        }
        
        // Shahar nuqtasi
        svg += `<circle cx="${cx}" cy="${cy}" r="4" fill="white" stroke="#1a3a5c" stroke-width="2"/>`;
        
        // Harorat label
        const tmin = weather.temp_min;
        const tmax = weather.temp_max;
        const tempStr = (tmin !== undefined && tmin !== null) 
            ? `${tmin}°..${tmax}°` 
            : `${tmax}°`;
        
        // Background for temperature
        const textWidth = tempStr.length * 7 + 10;
        svg += `<rect x="${cx - textWidth / 2}" y="${cy + 6}" width="${textWidth}" height="17" rx="8" fill="rgba(255,255,255,0.92)" stroke="rgba(0,0,0,0.15)" stroke-width="0.7"/>`;
        svg += `<text x="${cx}" y="${cy + 19}" text-anchor="middle" font-size="11" font-weight="bold" fill="#1a237e" font-family="Arial, sans-serif">${tempStr}</text>`;
        
        // Shahar nomi
        svg += `<text x="${cx}" y="${cy + 35}" text-anchor="middle" font-size="9.5" fill="#263238" font-weight="600" font-family="Arial, sans-serif">${cityName}</text>`;
    }
    
    // === TERMOMETR LEGEND ===
    svg += renderThermometerLegend(legendX, legendY, 440);
    
    // === FOOTER ===
    svg += `<rect x="0" y="${svgHeight - 30}" width="${svgWidth}" height="30" fill="url(#headerGrad)"/>`;
    svg += `<text x="${svgWidth / 2}" y="${svgHeight - 11}" text-anchor="middle" font-size="11" fill="rgba(255,255,255,0.85)" font-family="Arial, sans-serif">hydromet.uz  |  t.me/uzhydromet  |  O'zbekiston Gidrometeorologiya xizmati agentligi</text>`;
    
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
        const scale = 2; // 2x for high quality
        canvas.width = 1200 * scale;
        canvas.height = 750 * scale;
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
