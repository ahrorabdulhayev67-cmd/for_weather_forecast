/**
 * Ob-havo prognozi xarita generatori
 * SVG asosida viloyat ranglanishi + ikonkalar + termometr legend
 * PNG sifatida yuklab olish imkoniyati
 */

// ===== HARORAT RANGLARI =====
function tempToColor(temp) {
    // Past harorat (ko'k) -> o'rta (yashil/sariq) -> yuqori (qizil)
    if (temp <= -10) return '#1a237e';
    if (temp <= -5) return '#283593';
    if (temp <= 0) return '#1565c0';
    if (temp <= 5) return '#0288d1';
    if (temp <= 10) return '#00838f';
    if (temp <= 15) return '#00695c';
    if (temp <= 20) return '#2e7d32';
    if (temp <= 25) return '#558b2f';
    if (temp <= 28) return '#9e9d24';
    if (temp <= 31) return '#f9a825';
    if (temp <= 34) return '#ff8f00';
    if (temp <= 37) return '#ef6c00';
    if (temp <= 40) return '#d84315';
    if (temp <= 43) return '#c62828';
    if (temp <= 46) return '#b71c1c';
    return '#880e4f';
}

function tempToGradientColor(temp) {
    // Smooth gradient interpolation
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

// ===== OB-HAVO IKONKALARI (SVG) =====
const WEATHER_ICONS = {
    ochiq: function(x, y, size) {
        // Quyosh
        const r = size * 0.4;
        let svg = `<circle cx="${x}" cy="${y}" r="${r}" fill="#FFD600" stroke="#FF8F00" stroke-width="1.5"/>`;
        // Nurlar
        for (let i = 0; i < 8; i++) {
            const angle = (i * 45) * Math.PI / 180;
            const x1 = x + Math.cos(angle) * (r + 3);
            const y1 = y + Math.sin(angle) * (r + 3);
            const x2 = x + Math.cos(angle) * (r + 7);
            const y2 = y + Math.sin(angle) * (r + 7);
            svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#FF8F00" stroke-width="2" stroke-linecap="round"/>`;
        }
        return svg;
    },
    qisman_bulutli: function(x, y, size) {
        // Quyosh + bulut
        const r = size * 0.3;
        let svg = `<circle cx="${x - 4}" cy="${y - 4}" r="${r}" fill="#FFD600" stroke="#FF8F00" stroke-width="1"/>`;
        // Bulut
        svg += `<ellipse cx="${x + 3}" cy="${y + 2}" rx="${size * 0.45}" ry="${size * 0.28}" fill="white" stroke="#90A4AE" stroke-width="1"/>`;
        svg += `<ellipse cx="${x}" cy="${y + 4}" rx="${size * 0.35}" ry="${size * 0.22}" fill="white" stroke="#90A4AE" stroke-width="0.8"/>`;
        return svg;
    },
    bulutli: function(x, y, size) {
        // Bulut
        let svg = `<ellipse cx="${x}" cy="${y}" rx="${size * 0.5}" ry="${size * 0.3}" fill="#B0BEC5" stroke="#78909C" stroke-width="1.2"/>`;
        svg += `<ellipse cx="${x - 5}" cy="${y + 3}" rx="${size * 0.35}" ry="${size * 0.22}" fill="#CFD8DC" stroke="#90A4AE" stroke-width="0.8"/>`;
        svg += `<ellipse cx="${x + 5}" cy="${y + 2}" rx="${size * 0.3}" ry="${size * 0.2}" fill="#CFD8DC" stroke="#90A4AE" stroke-width="0.8"/>`;
        return svg;
    },
    yomgir: function(x, y, size) {
        // Bulut + tomchilar
        let svg = `<ellipse cx="${x}" cy="${y - 3}" rx="${size * 0.45}" ry="${size * 0.25}" fill="#78909C" stroke="#546E7A" stroke-width="1"/>`;
        // Tomchilar
        for (let i = -1; i <= 1; i++) {
            svg += `<line x1="${x + i * 6}" y1="${y + 5}" x2="${x + i * 6 - 2}" y2="${y + 10}" stroke="#1E88E5" stroke-width="1.5" stroke-linecap="round"/>`;
        }
        return svg;
    },
    jala: function(x, y, size) {
        // Quyosh + bulut + yengil yomg'ir
        const r = size * 0.22;
        let svg = `<circle cx="${x - 5}" cy="${y - 6}" r="${r}" fill="#FFD600" stroke="#FF8F00" stroke-width="0.8"/>`;
        svg += `<ellipse cx="${x + 2}" cy="${y - 2}" rx="${size * 0.4}" ry="${size * 0.22}" fill="#B0BEC5" stroke="#78909C" stroke-width="1"/>`;
        svg += `<line x1="${x - 3}" y1="${y + 5}" x2="${x - 4}" y2="${y + 9}" stroke="#42A5F5" stroke-width="1.2" stroke-linecap="round"/>`;
        svg += `<line x1="${x + 3}" y1="${y + 5}" x2="${x + 2}" y2="${y + 9}" stroke="#42A5F5" stroke-width="1.2" stroke-linecap="round"/>`;
        return svg;
    },
    momaqaldiroq: function(x, y, size) {
        // Bulut + chaqmoq
        let svg = `<ellipse cx="${x}" cy="${y - 4}" rx="${size * 0.5}" ry="${size * 0.28}" fill="#546E7A" stroke="#37474F" stroke-width="1.2"/>`;
        // Chaqmoq
        svg += `<path d="M${x - 1},${y + 2} L${x + 3},${y + 6} L${x},${y + 6} L${x + 2},${y + 12}" fill="none" stroke="#FDD835" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;
        return svg;
    },
    qor: function(x, y, size) {
        // Bulut + qor parchalar
        let svg = `<ellipse cx="${x}" cy="${y - 4}" rx="${size * 0.45}" ry="${size * 0.25}" fill="#90A4AE" stroke="#607D8B" stroke-width="1"/>`;
        // Qor
        for (let i = -1; i <= 1; i++) {
            const cx = x + i * 7;
            const cy = y + 7;
            svg += `<circle cx="${cx}" cy="${cy}" r="2" fill="white" stroke="#90A4AE" stroke-width="0.5"/>`;
        }
        return svg;
    },
    tuman: function(x, y, size) {
        // Horizontal chiziqlar
        let svg = '';
        for (let i = -2; i <= 2; i++) {
            const w = size * (0.6 - Math.abs(i) * 0.08);
            svg += `<line x1="${x - w}" y1="${y + i * 4}" x2="${x + w}" y2="${y + i * 4}" stroke="#B0BEC5" stroke-width="2.5" stroke-linecap="round" opacity="${0.9 - Math.abs(i) * 0.15}"/>`;
        }
        return svg;
    },
    dol: function(x, y, size) {
        // Bulut + do'l parchalari
        let svg = `<ellipse cx="${x}" cy="${y - 4}" rx="${size * 0.45}" ry="${size * 0.25}" fill="#78909C" stroke="#546E7A" stroke-width="1"/>`;
        for (let i = -1; i <= 1; i++) {
            svg += `<circle cx="${x + i * 6}" cy="${y + 7}" r="3" fill="#E3F2FD" stroke="#1565C0" stroke-width="1"/>`;
        }
        return svg;
    },
    chang_boroni: function(x, y, size) {
        // Shamol chiziqlari + chang
        let svg = '';
        for (let i = -1; i <= 1; i++) {
            svg += `<path d="M${x - 10},${y + i * 5} Q${x},${y + i * 5 - 3} ${x + 10},${y + i * 5}" fill="none" stroke="#8D6E63" stroke-width="2" stroke-linecap="round" opacity="0.8"/>`;
        }
        svg += `<circle cx="${x + 5}" cy="${y - 3}" r="1.5" fill="#A1887F"/>`;
        svg += `<circle cx="${x - 3}" cy="${y + 5}" r="1" fill="#BCAAA4"/>`;
        return svg;
    },
    qor_boroni: function(x, y, size) {
        // Shamol + qor
        let svg = '';
        svg += `<path d="M${x - 10},${y - 2} Q${x},${y - 5} ${x + 10},${y - 2}" fill="none" stroke="#607D8B" stroke-width="2" stroke-linecap="round"/>`;
        svg += `<path d="M${x - 8},${y + 3} Q${x + 2},${y} ${x + 10},${y + 3}" fill="none" stroke="#78909C" stroke-width="1.5" stroke-linecap="round"/>`;
        for (let i = 0; i < 4; i++) {
            svg += `<circle cx="${x - 5 + i * 4}" cy="${y + 7 + (i % 2) * 3}" r="1.5" fill="white" stroke="#90A4AE" stroke-width="0.5"/>`;
        }
        return svg;
    }
};

// ===== TERMOMETR LEGEND =====
function renderThermometerLegend(x, y, height) {
    const width = 30;
    const temps = [48, 44, 40, 36, 32, 28, 24, 20, 16, 12, 8, 4, 0, -4, -8];
    const segH = height / temps.length;
    
    let svg = '';
    
    // Sarlavha
    svg += `<text x="${x + width / 2}" y="${y - 12}" text-anchor="middle" font-size="11" font-weight="bold" fill="#1a3a5c">°C</text>`;
    
    // Termometr tanasi
    svg += `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="4" ry="4" fill="none" stroke="#455a64" stroke-width="1.5"/>`;
    
    temps.forEach((temp, i) => {
        const segY = y + i * segH;
        const color = tempToGradientColor(temp);
        svg += `<rect x="${x}" y="${segY}" width="${width}" height="${segH + 0.5}" fill="${color}"/>`;
        // Raqam
        svg += `<text x="${x + width + 6}" y="${segY + segH / 2 + 4}" font-size="9" fill="#37474f">${temp}°</text>`;
    });
    
    // Ramka
    svg += `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="4" ry="4" fill="none" stroke="#455a64" stroke-width="1.5"/>`;
    
    // Termometr boshi (pastda doira)
    svg += `<circle cx="${x + width / 2}" cy="${y + height + 12}" r="10" fill="#c62828" stroke="#455a64" stroke-width="1.5"/>`;
    
    return svg;
}

// ===== ASOSIY XARITA RENDERI =====
function renderWeatherMap(weatherData, dateStr, title) {
    const svgWidth = 1200;
    const svgHeight = 750;
    const mapOffsetX = 0;
    const mapOffsetY = 80;
    const legendX = svgWidth - 85;
    const legendY = 120;
    
    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${svgWidth}" height="${svgHeight}" viewBox="0 0 ${svgWidth} ${svgHeight}">`;
    
    // Background
    svg += `<rect width="${svgWidth}" height="${svgHeight}" fill="#f0f4f8"/>`;
    
    // Header background
    svg += `<rect x="0" y="0" width="${svgWidth}" height="70" fill="#1a3a5c"/>`;
    
    // Logo area
    svg += `<text x="35" y="32" font-size="18" font-weight="bold" fill="white" font-family="Arial, sans-serif">O'ZBEKISTON RESPUBLIKASI</text>`;
    svg += `<text x="35" y="54" font-size="14" fill="rgba(255,255,255,0.85)" font-family="Arial, sans-serif">Gidrometeorologiya xizmati agentligi</text>`;
    
    // Title
    svg += `<text x="${svgWidth / 2}" y="35" text-anchor="middle" font-size="20" font-weight="bold" fill="#FFD600" font-family="Arial, sans-serif">OB-HAVO PROGNOZI</text>`;
    svg += `<text x="${svgWidth / 2}" y="56" text-anchor="middle" font-size="13" fill="rgba(255,255,255,0.9)" font-family="Arial, sans-serif">${dateStr || ''}</text>`;
    
    // hydromet.uz
    svg += `<text x="${svgWidth - 35}" y="42" text-anchor="end" font-size="12" fill="rgba(255,255,255,0.7)" font-family="Arial, sans-serif">hydromet.uz</text>`;
    
    // Map area background
    svg += `<rect x="20" y="80" width="${svgWidth - 130}" height="${svgHeight - 110}" rx="8" fill="#e8f0f8" stroke="#c8d8e8" stroke-width="1"/>`;
    
    // === VILOYATLAR ===
    for (const [regionId, regionData] of Object.entries(REGIONS)) {
        const city = Object.entries(CITIES).find(([_, c]) => c.region === regionId);
        let fillColor = '#e0e0e0'; // default
        
        if (city && weatherData[city[0]]) {
            const temp = weatherData[city[0]].temp_max || weatherData[city[0]].temp_avg || 25;
            fillColor = tempToGradientColor(temp);
        }
        
        const path = polygonToPath(regionData.polygon);
        svg += `<path d="${path}" fill="${fillColor}" fill-opacity="0.75" stroke="#37474f" stroke-width="1.5" stroke-linejoin="round"/>`;
    }
    
    // === SHAHAR BELGILARI + HARORAT + IKONKALAR ===
    for (const [cityName, cityData] of Object.entries(CITIES)) {
        const [cx, cy] = geoToSvg(cityData.lon, cityData.lat);
        const weather = weatherData[cityName];
        
        if (!weather) continue;
        
        // Shahar nuqtasi
        svg += `<circle cx="${cx}" cy="${cy}" r="4" fill="white" stroke="#1a3a5c" stroke-width="2"/>`;
        
        // Ob-havo ikonkasi (yuqorida)
        const weatherType = weather.weather || 'ochiq';
        if (WEATHER_ICONS[weatherType]) {
            svg += WEATHER_ICONS[weatherType](cx, cy - 28, 18);
        }
        
        // Harorat label (pastda)
        const tmin = weather.temp_min;
        const tmax = weather.temp_max;
        const tempStr = (tmin !== undefined && tmin !== null) 
            ? `${tmin}°..${tmax}°` 
            : `${tmax}°`;
        
        // Background for temperature
        const textWidth = tempStr.length * 6.5 + 8;
        svg += `<rect x="${cx - textWidth / 2}" y="${cy + 6}" width="${textWidth}" height="16" rx="3" fill="rgba(255,255,255,0.9)" stroke="rgba(0,0,0,0.1)" stroke-width="0.5"/>`;
        svg += `<text x="${cx}" y="${cy + 18}" text-anchor="middle" font-size="11" font-weight="bold" fill="#1a237e" font-family="Arial, sans-serif">${tempStr}</text>`;
        
        // Shahar nomi
        svg += `<text x="${cx}" y="${cy + 34}" text-anchor="middle" font-size="9.5" fill="#37474f" font-weight="500" font-family="Arial, sans-serif">${cityName}</text>`;
    }
    
    // === TERMOMETR LEGEND ===
    svg += renderThermometerLegend(legendX, legendY, 450);
    
    // === FOOTER ===
    svg += `<rect x="0" y="${svgHeight - 28}" width="${svgWidth}" height="28" fill="#1a3a5c"/>`;
    svg += `<text x="${svgWidth / 2}" y="${svgHeight - 10}" text-anchor="middle" font-size="11" fill="rgba(255,255,255,0.8)" font-family="Arial, sans-serif">hydromet.uz  |  t.me/uzhydromet  |  Gidrometeorologiya xizmati agentligi</text>`;
    
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
        canvas.width = 1200 * 2; // 2x for high quality
        canvas.height = 750 * 2;
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
