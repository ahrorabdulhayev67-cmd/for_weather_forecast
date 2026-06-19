// O'zbekiston shaharlari koordinatalari
const CITIES = [
    { name: "Toshkent", lat: 41.2995, lon: 69.2401, region: "Toshkent shahri" },
    { name: "Samarqand", lat: 39.6542, lon: 66.9597, region: "Samarqand viloyati" },
    { name: "Buxoro", lat: 39.7745, lon: 64.4286, region: "Buxoro viloyati" },
    { name: "Namangan", lat: 41.0011, lon: 71.6722, region: "Namangan viloyati" },
    { name: "Andijon", lat: 40.7821, lon: 72.3442, region: "Andijon viloyati" },
    { name: "Farg'ona", lat: 40.3834, lon: 71.7870, region: "Farg'ona viloyati" },
    { name: "Qarshi", lat: 38.8606, lon: 65.7983, region: "Qashqadaryo viloyati" },
    { name: "Nukus", lat: 42.4628, lon: 59.6003, region: "Qoraqalpog'iston" },
    { name: "Navoiy", lat: 40.1033, lon: 65.3792, region: "Navoiy viloyati" },
    { name: "Termiz", lat: 37.2241, lon: 67.2783, region: "Surxondaryo viloyati" },
    { name: "Jizzax", lat: 40.1158, lon: 67.8422, region: "Jizzax viloyati" },
    { name: "Urganch", lat: 41.5531, lon: 60.6318, region: "Xorazm viloyati" },
    { name: "Guliston", lat: 40.4897, lon: 68.7842, region: "Sirdaryo viloyati" },
    { name: "Xiva", lat: 41.3775, lon: 60.3619, region: "Xorazm viloyati" },
    { name: "Shahrisabz", lat: 39.0581, lon: 66.8344, region: "Qashqadaryo viloyati" },
    { name: "Chirchiq", lat: 41.4689, lon: 69.5822, region: "Toshkent viloyati" },
    { name: "Olmaliq", lat: 40.8453, lon: 69.5986, region: "Toshkent viloyati" },
    { name: "Zarafshon", lat: 41.5744, lon: 64.1853, region: "Navoiy viloyati" }
];


// Ob-havo kodlari uchun ikonkalar
const WEATHER_CODES = {
    0: { icon: "☀️", desc: "Ochiq havo" },
    1: { icon: "🌤️", desc: "Asosan ochiq" },
    2: { icon: "⛅", desc: "Qisman bulutli" },
    3: { icon: "☁️", desc: "Bulutli" },
    45: { icon: "🌫️", desc: "Tuman" },
    48: { icon: "🌫️", desc: "Qirov tumani" },
    51: { icon: "🌦️", desc: "Yengil yomg'ir" },
    53: { icon: "🌦️", desc: "O'rtacha yomg'ir" },
    55: { icon: "🌧️", desc: "Kuchli yomg'ir" },
    56: { icon: "🌧️", desc: "Muzlagan yomg'ir" },
    57: { icon: "🌧️", desc: "Kuchli muzlagan yomg'ir" },
    61: { icon: "🌧️", desc: "Yengil yog'ish" },
    63: { icon: "🌧️", desc: "O'rtacha yog'ish" },
    65: { icon: "🌧️", desc: "Kuchli yog'ish" },
    66: { icon: "🌨️", desc: "Muzlagan yog'ish" },
    67: { icon: "🌨️", desc: "Kuchli muzlagan yog'ish" },
    71: { icon: "❄️", desc: "Yengil qor" },
    73: { icon: "❄️", desc: "O'rtacha qor" },
    75: { icon: "❄️", desc: "Kuchli qor" },
    77: { icon: "❄️", desc: "Qor donachalari" },
    80: { icon: "🌦️", desc: "Yengil jala" },
    81: { icon: "🌧️", desc: "O'rtacha jala" },
    82: { icon: "🌧️", desc: "Kuchli jala" },
    85: { icon: "🌨️", desc: "Yengil qor jalasi" },
    86: { icon: "🌨️", desc: "Kuchli qor jalasi" },
    95: { icon: "⛈️", desc: "Momaqaldiroq" },
    96: { icon: "⛈️", desc: "Do'l bilan momaqaldiroq" },
    99: { icon: "⛈️", desc: "Kuchli do'l" }
};

// Hafta kunlari
const DAYS_UZ = ["Yak", "Dush", "Sesh", "Chor", "Pay", "Jum", "Shah"];


// Harorat rangini olish
function getTempColor(temp) {
    if (temp <= -10) return "#1a237e";
    if (temp <= 0) return "#1565c0";
    if (temp <= 10) return "#42a5f5";
    if (temp <= 20) return "#66bb6a";
    if (temp <= 30) return "#ffa726";
    if (temp <= 35) return "#ef5350";
    if (temp <= 40) return "#c62828";
    return "#4a148c";
}

// Shamol yo'nalishini olish
function getWindDirection(degrees) {
    const dirs = ["Shim", "Shim-Sharq", "Sharq", "Jan-Sharq", "Jan", "Jan-G'arb", "G'arb", "Shim-G'arb"];
    const index = Math.round(degrees / 45) % 8;
    return dirs[index];
}

// Xaritani yaratish
let map, markers = [], weatherData = {};

function initMap() {
    map = L.map('map', {
        center: [41.3, 64.5],
        zoom: 6,
        minZoom: 5,
        maxZoom: 12
    });

    // Asosiy tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // O'zbekiston chegarasini chizish (taxminiy)
    const uzbekistanBounds = [
        [37.2, 56.0], [37.2, 73.1], [45.6, 73.1], [45.6, 56.0]
    ];
    
    // Legend qo'shish
    addLegend();
    
    // Ma'lumotlarni yuklash
    loadAllWeatherData();
}


// Open-Meteo API dan ma'lumot olish
async function fetchWeatherForCity(city) {
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${city.lat}&longitude=${city.lon}` +
        `&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,apparent_temperature` +
        `&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max` +
        `&timezone=Asia/Tashkent&forecast_days=7`;
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`${city.name} uchun xatolik:`, error);
        return null;
    }
}

// Barcha shaharlar uchun ma'lumot yuklash
async function loadAllWeatherData() {
    const mapEl = document.getElementById('map');
    
    // Loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-overlay';
    loadingDiv.innerHTML = '⏳ Ma\'lumotlar yuklanmoqda...';
    loadingDiv.id = 'loading';
    mapEl.parentElement.style.position = 'relative';
    mapEl.parentElement.appendChild(loadingDiv);

    // Parallel fetch (har 3 tadan)
    const batchSize = 3;
    for (let i = 0; i < CITIES.length; i += batchSize) {
        const batch = CITIES.slice(i, i + batchSize);
        const results = await Promise.all(batch.map(city => fetchWeatherForCity(city)));
        
        results.forEach((data, idx) => {
            const city = batch[idx];
            if (data) {
                weatherData[city.name] = data;
                addCityMarker(city, data);
            }
        });
        
        // Rate limiting uchun kichik pauza
        if (i + batchSize < CITIES.length) {
            await new Promise(r => setTimeout(r, 200));
        }
    }

    // Loading o'chirish
    const loading = document.getElementById('loading');
    if (loading) loading.remove();
}


// Shahar markeri qo'shish
function addCityMarker(city, data) {
    const temp = Math.round(data.current.temperature_2m);
    const code = data.current.weather_code;
    const weatherInfo = WEATHER_CODES[code] || { icon: "🌡️", desc: "Noma'lum" };
    const color = getTempColor(temp);

    const icon = L.divIcon({
        className: 'weather-marker',
        html: `<div class="marker-content" style="border-color: ${color}">
                   <span class="marker-icon">${weatherInfo.icon}</span>
                   <span class="marker-temp" style="color: ${color}">${temp}°</span>
               </div>`,
        iconSize: [80, 32],
        iconAnchor: [40, 16]
    });

    const marker = L.marker([city.lat, city.lon], { icon: icon })
        .addTo(map)
        .on('click', () => showCityDetail(city, data));
    
    // Tooltip
    marker.bindTooltip(`<b>${city.name}</b><br>${weatherInfo.desc}, ${temp}°C`, {
        direction: 'top',
        offset: [0, -16]
    });

    markers.push(marker);
}

// Shahar tafsilotlarini ko'rsatish
function showCityDetail(city, data) {
    const current = data.current;
    const temp = Math.round(current.temperature_2m);
    const feelsLike = Math.round(current.apparent_temperature);
    const humidity = current.relative_humidity_2m;
    const windSpeed = Math.round(current.wind_speed_10m);
    const windDir = getWindDirection(current.wind_direction_10m);
    const code = current.weather_code;
    const weatherInfo = WEATHER_CODES[code] || { icon: "🌡️", desc: "Noma'lum" };

    const detailEl = document.getElementById('cityDetail');
    detailEl.innerHTML = `
        <div class="city-name">${city.name}</div>
        <div style="font-size:12px; color:#718096; margin-bottom:8px;">${city.region}</div>
        <div class="weather-main">
            <span class="weather-icon">${weatherInfo.icon}</span>
            <span class="temp-big">${temp}°</span>
        </div>
        <div style="margin-bottom:12px; color:#4a5568;">${weatherInfo.desc}</div>
        <div class="weather-grid">
            <div class="grid-item">
                <div class="label">His qilish</div>
                <div class="value">${feelsLike}°C</div>
            </div>
            <div class="grid-item">
                <div class="label">Namlik</div>
                <div class="value">${humidity}%</div>
            </div>
            <div class="grid-item">
                <div class="label">Shamol</div>
                <div class="value">${windSpeed} km/s</div>
            </div>
            <div class="grid-item">
                <div class="label">Yo'nalish</div>
                <div class="value">${windDir}</div>
            </div>
        </div>
    `;


    // 7 kunlik prognoz
    showWeeklyForecast(data);
}

// Haftalik prognozni ko'rsatish
function showWeeklyForecast(data) {
    const daily = data.daily;
    const forecastEl = document.getElementById('weeklyForecast');
    
    let html = '';
    for (let i = 0; i < daily.time.length; i++) {
        const date = new Date(daily.time[i]);
        const dayName = DAYS_UZ[date.getDay()];
        const dayNum = date.getDate();
        const code = daily.weather_code[i];
        const weatherInfo = WEATHER_CODES[code] || { icon: "🌡️", desc: "Noma'lum" };
        const maxTemp = Math.round(daily.temperature_2m_max[i]);
        const minTemp = Math.round(daily.temperature_2m_min[i]);
        const precip = daily.precipitation_sum[i];

        html += `
            <div class="day-row">
                <span class="day-name">${dayName} ${dayNum}</span>
                <span class="day-icon" title="${weatherInfo.desc}">${weatherInfo.icon}</span>
                <span class="day-temps">
                    <span class="temp-high">↑${maxTemp}°</span>
                    <span class="temp-low">↓${minTemp}°</span>
                </span>
                ${precip > 0 ? `<span style="color:#3182ce; font-size:11px;">💧${precip}mm</span>` : '<span style="width:45px"></span>'}
            </div>
        `;
    }
    
    forecastEl.innerHTML = html;
}

// Legend qo'shish
function addLegend() {
    const legend = L.control({ position: 'bottomleft' });
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'legend');
        div.innerHTML = `
            <h4>🌡️ Harorat shkala</h4>
            <div class="legend-item"><span class="legend-color" style="background:#1565c0"></span> 0°C dan past</div>
            <div class="legend-item"><span class="legend-color" style="background:#42a5f5"></span> 0° — 10°C</div>
            <div class="legend-item"><span class="legend-color" style="background:#66bb6a"></span> 10° — 20°C</div>
            <div class="legend-item"><span class="legend-color" style="background:#ffa726"></span> 20° — 30°C</div>
            <div class="legend-item"><span class="legend-color" style="background:#ef5350"></span> 30° — 35°C</div>
            <div class="legend-item"><span class="legend-color" style="background:#c62828"></span> 35°C dan yuqori</div>
        `;
        return div;
    };
    legend.addTo(map);
}


// Layer tanlash
document.getElementById('layerSelect').addEventListener('change', function() {
    const layer = this.value;
    updateMarkerDisplay(layer);
});

// Marker ko'rinishini yangilash
function updateMarkerDisplay(layer) {
    markers.forEach(marker => marker.remove());
    markers = [];

    CITIES.forEach(city => {
        const data = weatherData[city.name];
        if (!data) return;

        let displayValue, displayIcon, color;
        const current = data.current;

        switch(layer) {
            case 'temperature':
                displayValue = `${Math.round(current.temperature_2m)}°`;
                displayIcon = WEATHER_CODES[current.weather_code]?.icon || "🌡️";
                color = getTempColor(current.temperature_2m);
                break;
            case 'wind':
                displayValue = `${Math.round(current.wind_speed_10m)} km/s`;
                displayIcon = "💨";
                color = current.wind_speed_10m > 30 ? "#c62828" : 
                        current.wind_speed_10m > 15 ? "#ffa726" : "#42a5f5";
                break;
            case 'precipitation':
                const precip = data.daily.precipitation_sum[0] || 0;
                displayValue = `${precip} mm`;
                displayIcon = precip > 0 ? "🌧️" : "☀️";
                color = precip > 10 ? "#1565c0" : precip > 0 ? "#42a5f5" : "#66bb6a";
                break;
            case 'humidity':
                displayValue = `${current.relative_humidity_2m}%`;
                displayIcon = "💧";
                color = current.relative_humidity_2m > 70 ? "#1565c0" : 
                        current.relative_humidity_2m > 40 ? "#42a5f5" : "#ffa726";
                break;
        }

        const icon = L.divIcon({
            className: 'weather-marker',
            html: `<div class="marker-content" style="border-color: ${color}">
                       <span class="marker-icon">${displayIcon}</span>
                       <span class="marker-temp" style="color: ${color}">${displayValue}</span>
                   </div>`,
            iconSize: [90, 32],
            iconAnchor: [45, 16]
        });

        const marker = L.marker([city.lat, city.lon], { icon: icon })
            .addTo(map)
            .on('click', () => showCityDetail(city, data));
        
        markers.push(marker);
    });
}

// Yangilash tugmasi
document.getElementById('refreshBtn').addEventListener('click', function() {
    markers.forEach(marker => marker.remove());
    markers = [];
    weatherData = {};
    loadAllWeatherData();
});

// Ilovani ishga tushurish
document.addEventListener('DOMContentLoaded', initMap);
