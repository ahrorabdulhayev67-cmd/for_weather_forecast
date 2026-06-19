// ============================================
// O'ZGIDROMET PROGNOZ XARITA GENERATORI
// Sinoptiklar uchun oddiy interfeys
// ============================================

// O'zbekiston viloyat markazlari
const CITIES = [
    { id: "toshkent", name: "Toshkent", lat: 41.2995, lon: 69.2401 },
    { id: "samarqand", name: "Samarqand", lat: 39.6542, lon: 66.9597 },
    { id: "buxoro", name: "Buxoro", lat: 39.7745, lon: 64.4286 },
    { id: "namangan", name: "Namangan", lat: 41.0011, lon: 71.6722 },
    { id: "andijon", name: "Andijon", lat: 40.7821, lon: 72.3442 },
    { id: "fargona", name: "Farg'ona", lat: 40.3834, lon: 71.7870 },
    { id: "qarshi", name: "Qarshi", lat: 38.8606, lon: 65.7983 },
    { id: "nukus", name: "Nukus", lat: 42.4628, lon: 59.6003 },
    { id: "navoiy", name: "Navoiy", lat: 40.1033, lon: 65.3792 },
    { id: "termiz", name: "Termiz", lat: 37.2241, lon: 67.2783 },
    { id: "jizzax", name: "Jizzax", lat: 40.1158, lon: 67.8422 },
    { id: "urganch", name: "Urganch", lat: 41.5531, lon: 60.6318 },
    { id: "guliston", name: "Guliston", lat: 40.4897, lon: 68.7842 },
    { id: "karshi", name: "Shahrisabz", lat: 39.0581, lon: 66.8344 }
];

// Ob-havo turlari (sinoptik tanlaydi)
const WEATHER_TYPES = [
    { code: 0, icon: "☀️", label: "Ochiq" },
    { code: 1, icon: "🌤️", label: "Az bulutli" },
    { code: 2, icon: "⛅", label: "Bulutli" },
    { code: 3, icon: "☁️", label: "To'liq bulutli" },
    { code: 10, icon: "🌫️", label: "Tuman" },
    { code: 51, icon: "🌦️", label: "Yengil yomg'ir" },
    { code: 61, icon: "🌧️", label: "Yomg'ir" },
    { code: 65, icon: "🌧️", label: "Kuchli yomg'ir" },
    { code: 80, icon: "⛈️", label: "Momaqaldiroq" },
    { code: 71, icon: "❄️", label: "Qor" },
    { code: 96, icon: "🌨️", label: "Do'l" },
    { code: 99, icon: "💨", label: "Kuchli shamol" }
];

// Hafta kunlari
const DAYS_UZ = ["Yakshanba", "Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"];
const MONTHS_UZ = ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];


// ============================================
// MA'LUMOTLAR SAQLASH (3 kun x shaharlar)
// ============================================

// 3 kunlik prognoz ma'lumotlar bazasi
let forecastData = {
    days: [
        { date: null, comment: "", cities: {} },
        { date: null, comment: "", cities: {} },
        { date: null, comment: "", cities: {} }
    ]
};

let currentDay = 0; // Hozirgi tab (0, 1, 2)
let map = null;
let markers = [];

// ============================================
// JADVAL YARATISH (INPUT INTERFEYS)
// ============================================

function initDates() {
    const today = new Date();
    for (let i = 0; i < 3; i++) {
        const d = new Date(today);
        d.setDate(d.getDate() + i);
        forecastData.days[i].date = d;
    }
    updateDateDisplay();
    updateDayTabs();
}

function updateDateDisplay() {
    const today = new Date();
    document.getElementById('currentDate').textContent = 
        `${DAYS_UZ[today.getDay()]}, ${today.getDate()} ${MONTHS_UZ[today.getMonth()]} ${today.getFullYear()}`;
}

function updateDayTabs() {
    document.querySelectorAll('.day-tab').forEach((tab, idx) => {
        const d = forecastData.days[idx].date;
        const labels = ["Bugun", "Ertaga", "Indinga"];
        tab.textContent = `📅 ${labels[idx]} (${d.getDate()}.${String(d.getMonth()+1).padStart(2,'0')})`;
    });
}

function buildTable() {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    CITIES.forEach(city => {
        const row = document.createElement('tr');
        const data = forecastData.days[currentDay].cities[city.id] || {};
        
        // Ob-havo turini tanlash uchun select
        let weatherOptions = WEATHER_TYPES.map(w => 
            `<option value="${w.code}" ${data.weather === w.code ? 'selected' : ''}>${w.icon} ${w.label}</option>`
        ).join('');

        row.innerHTML = `
            <td>${city.name}</td>
            <td><input type="number" data-city="${city.id}" data-field="tempMin" 
                value="${data.tempMin ?? ''}" min="-30" max="55" step="1" placeholder="—"></td>
            <td><input type="number" data-city="${city.id}" data-field="tempMax" 
                value="${data.tempMax ?? ''}" min="-30" max="55" step="1" placeholder="—"></td>
            <td><input type="number" data-city="${city.id}" data-field="wind" 
                value="${data.wind ?? ''}" min="0" max="100" step="1" placeholder="—"></td>
            <td><input type="number" data-city="${city.id}" data-field="precip" 
                value="${data.precip ?? ''}" min="0" max="200" step="0.1" placeholder="—"></td>
            <td><select data-city="${city.id}" data-field="weather">${weatherOptions}</select></td>
        `;
        tbody.appendChild(row);
    });

    // Input o'zgarishlarini kuzatish
    tbody.querySelectorAll('input, select').forEach(el => {
        el.addEventListener('change', handleInputChange);
        el.addEventListener('input', handleInputChange);
    });

    // Izoh matnini yuklash
    document.getElementById('dayComment').value = forecastData.days[currentDay].comment || '';
}

function handleInputChange(e) {
    const cityId = e.target.dataset.city;
    const field = e.target.dataset.field;
    let value;

    if (e.target.type === 'number') {
        value = e.target.value === '' ? null : parseFloat(e.target.value);
    } else {
        value = parseInt(e.target.value);
    }

    if (!forecastData.days[currentDay].cities[cityId]) {
        forecastData.days[currentDay].cities[cityId] = {};
    }
    forecastData.days[currentDay].cities[cityId][field] = value;
}


// ============================================
// DAY TAB VA COMMENT BOSHQARUVI
// ============================================

function switchDay(dayIndex) {
    // Hozirgi kunni saqlash
    forecastData.days[currentDay].comment = document.getElementById('dayComment').value;
    
    // Yangi kunga o'tish
    currentDay = dayIndex;
    
    // Tablarni yangilash
    document.querySelectorAll('.day-tab').forEach((tab, idx) => {
        tab.classList.toggle('active', idx === dayIndex);
    });
    
    // Jadvalni qayta qurish
    buildTable();
}

// ============================================
// NAMUNA MA'LUMOTLAR (test uchun)
// ============================================

function loadSampleData() {
    const sampleWeather = [
        // Bugun
        {
            toshkent: { tempMin: 22, tempMax: 36, wind: 12, precip: 0, weather: 0 },
            samarqand: { tempMin: 18, tempMax: 33, wind: 8, precip: 0, weather: 1 },
            buxoro: { tempMin: 24, tempMax: 40, wind: 15, precip: 0, weather: 0 },
            namangan: { tempMin: 20, tempMax: 35, wind: 10, precip: 0, weather: 1 },
            andijon: { tempMin: 21, tempMax: 34, wind: 8, precip: 2, weather: 51 },
            fargona: { tempMin: 22, tempMax: 38, wind: 6, precip: 0, weather: 0 },
            qarshi: { tempMin: 23, tempMax: 41, wind: 12, precip: 0, weather: 0 },
            nukus: { tempMin: 20, tempMax: 38, wind: 18, precip: 0, weather: 1 },
            navoiy: { tempMin: 21, tempMax: 39, wind: 14, precip: 0, weather: 0 },
            termiz: { tempMin: 26, tempMax: 44, wind: 10, precip: 0, weather: 0 },
            jizzax: { tempMin: 20, tempMax: 36, wind: 11, precip: 0, weather: 2 },
            urganch: { tempMin: 21, tempMax: 37, wind: 16, precip: 0, weather: 1 },
            guliston: { tempMin: 21, tempMax: 35, wind: 9, precip: 0, weather: 1 },
            karshi: { tempMin: 19, tempMax: 34, wind: 7, precip: 0, weather: 2 }
        },
        // Ertaga
        {
            toshkent: { tempMin: 21, tempMax: 34, wind: 15, precip: 3, weather: 51 },
            samarqand: { tempMin: 17, tempMax: 31, wind: 12, precip: 5, weather: 61 },
            buxoro: { tempMin: 23, tempMax: 38, wind: 18, precip: 0, weather: 2 },
            namangan: { tempMin: 19, tempMax: 33, wind: 14, precip: 8, weather: 80 },
            andijon: { tempMin: 20, tempMax: 32, wind: 12, precip: 10, weather: 80 },
            fargona: { tempMin: 21, tempMax: 35, wind: 10, precip: 5, weather: 61 },
            qarshi: { tempMin: 22, tempMax: 39, wind: 14, precip: 0, weather: 1 },
            nukus: { tempMin: 19, tempMax: 36, wind: 22, precip: 0, weather: 99 },
            navoiy: { tempMin: 20, tempMax: 37, wind: 16, precip: 0, weather: 2 },
            termiz: { tempMin: 25, tempMax: 42, wind: 12, precip: 0, weather: 0 },
            jizzax: { tempMin: 19, tempMax: 34, wind: 13, precip: 2, weather: 51 },
            urganch: { tempMin: 20, tempMax: 35, wind: 20, precip: 0, weather: 99 },
            guliston: { tempMin: 20, tempMax: 33, wind: 11, precip: 1, weather: 51 },
            karshi: { tempMin: 18, tempMax: 32, wind: 9, precip: 4, weather: 61 }
        },
        // Indinga
        {
            toshkent: { tempMin: 20, tempMax: 32, wind: 10, precip: 0, weather: 2 },
            samarqand: { tempMin: 16, tempMax: 30, wind: 8, precip: 0, weather: 1 },
            buxoro: { tempMin: 22, tempMax: 37, wind: 12, precip: 0, weather: 1 },
            namangan: { tempMin: 18, tempMax: 31, wind: 8, precip: 0, weather: 2 },
            andijon: { tempMin: 19, tempMax: 30, wind: 6, precip: 0, weather: 2 },
            fargona: { tempMin: 20, tempMax: 33, wind: 7, precip: 0, weather: 1 },
            qarshi: { tempMin: 21, tempMax: 38, wind: 10, precip: 0, weather: 0 },
            nukus: { tempMin: 18, tempMax: 35, wind: 14, precip: 0, weather: 1 },
            navoiy: { tempMin: 19, tempMax: 36, wind: 11, precip: 0, weather: 1 },
            termiz: { tempMin: 24, tempMax: 41, wind: 8, precip: 0, weather: 0 },
            jizzax: { tempMin: 18, tempMax: 33, wind: 9, precip: 0, weather: 1 },
            urganch: { tempMin: 19, tempMax: 34, wind: 12, precip: 0, weather: 2 },
            guliston: { tempMin: 19, tempMax: 32, wind: 8, precip: 0, weather: 1 },
            karshi: { tempMin: 17, tempMax: 31, wind: 7, precip: 0, weather: 1 }
        }
    ];

    const comments = [
        "Respublikada havo ochiq va issiq. Buxoro, Qarshi, Termiz hududlarida harorat 40°C dan oshadi. Suv ko'proq ichish tavsiya etiladi.",
        "Shimoliy-sharqiy hududlarda momaqaldiroqli yomg'ir kutilmoqda. Xorazm va Qoraqalpog'istonda kuchli shamol (20-22 km/s). Ehtiyot bo'ling!",
        "Havo barqaror, oz bulutli. Harorat bir oz pasayadi. Yog'ingarchilik kutilmaydi."
    ];

    for (let i = 0; i < 3; i++) {
        forecastData.days[i].cities = sampleWeather[i];
        forecastData.days[i].comment = comments[i];
    }

    buildTable();
    alert("✅ Namuna ma'lumotlar yuklandi! Endi 'Xarita yaratish' ni bosing.");
}


// ============================================
// XARITA GENERATSIYASI (ASOSIY FUNKSIONAL)
// ============================================

function getWeatherInfo(code) {
    return WEATHER_TYPES.find(w => w.code === code) || { code: 0, icon: "❓", label: "Noma'lum" };
}

function getTempColor(temp) {
    if (temp === null || temp === undefined) return "#a0aec0";
    if (temp <= 0) return "#1565c0";
    if (temp <= 10) return "#42a5f5";
    if (temp <= 20) return "#66bb6a";
    if (temp <= 30) return "#ff9800";
    if (temp <= 35) return "#f44336";
    if (temp <= 40) return "#c62828";
    return "#6a1b9a"; // 40+ juda issiq
}

function generateMap() {
    // Hozirgi kunning izohini saqlash
    forecastData.days[currentDay].comment = document.getElementById('dayComment').value;

    // Validatsiya — kamida bitta shahar uchun ma'lumot bormi?
    let hasData = false;
    for (let i = 0; i < 3; i++) {
        const cities = forecastData.days[i].cities;
        for (const cityId in cities) {
            const c = cities[cityId];
            if (c.tempMax !== null && c.tempMax !== undefined) {
                hasData = true;
                break;
            }
        }
        if (hasData) break;
    }

    if (!hasData) {
        alert("⚠️ Kamida bitta shahar uchun harorat kiritilishi kerak!\n\nYoki 'Namuna yuklash' tugmasini bosing.");
        return;
    }

    // Input panelni yashirish, xaritani ko'rsatish
    document.getElementById('inputPanel').style.display = 'none';
    document.getElementById('mapPanel').style.display = 'block';

    // Xaritani yaratish (agar birinchi marta bo'lsa)
    if (!map) {
        map = L.map('map', {
            center: [41.0, 65.5],
            zoom: 6,
            minZoom: 5,
            maxZoom: 10,
            zoomControl: true
        });

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap | O\'zgidromet prognozi'
        }).addTo(map);
    }

    // Markerlarni yangilash
    renderMapForDay(0);
    
    // Map day buttonsni yangilash
    document.querySelectorAll('.map-day-btn').forEach((btn, idx) => {
        btn.classList.toggle('active', idx === 0);
        const d = forecastData.days[idx].date;
        const labels = ["Bugun", "Ertaga", "Indinga"];
        btn.textContent = `${labels[idx]} (${d.getDate()}.${String(d.getMonth()+1).padStart(2,'0')})`;
    });
}

function renderMapForDay(dayIndex) {
    // Eski markerlarni o'chirish
    markers.forEach(m => m.remove());
    markers = [];

    const dayData = forecastData.days[dayIndex];
    const cities = dayData.cities;

    CITIES.forEach(city => {
        const data = cities[city.id];
        if (!data || (data.tempMax === null && data.tempMin === null)) return;

        const tempMax = data.tempMax;
        const tempMin = data.tempMin;
        const wind = data.wind;
        const precip = data.precip;
        const weatherInfo = getWeatherInfo(data.weather);
        const color = getTempColor(tempMax);

        // Marker yaratish
        const icon = L.divIcon({
            className: 'city-marker',
            html: `<div class="marker-label" style="border-color:${color}">
                       <span class="m-icon">${weatherInfo.icon}</span>
                       <span class="m-temp" style="color:${color}">${tempMax !== null ? tempMax + '°' : '—'}</span>
                   </div>`,
            iconSize: [75, 30],
            iconAnchor: [37, 15]
        });

        const marker = L.marker([city.lat, city.lon], { icon: icon }).addTo(map);

        // Popup (bosganida batafsil info)
        const popupContent = `
            <div class="marker-popup">
                <div class="popup-city">${weatherInfo.icon} ${city.name}</div>
                <div class="popup-row"><span>🌡️ Harorat:</span> <b>${tempMin ?? '—'}° / ${tempMax ?? '—'}°C</b></div>
                <div class="popup-row"><span>💨 Shamol:</span> <b>${wind ?? '—'} km/s</b></div>
                <div class="popup-row"><span>🌧️ Yog'ingarchilik:</span> <b>${precip ?? 0} mm</b></div>
                <div class="popup-row"><span>☁️ Ob-havo:</span> <b>${weatherInfo.label}</b></div>
            </div>
        `;
        marker.bindPopup(popupContent, { maxWidth: 220 });

        // Tooltip (hover)
        marker.bindTooltip(`<b>${city.name}</b>: ${tempMin ?? ''}°/${tempMax ?? ''}° ${weatherInfo.icon}`, {
            direction: 'top', offset: [0, -12]
        });

        markers.push(marker);
    });

    // Izoh (comment) ko'rsatish
    const commentEl = document.getElementById('mapComment');
    if (dayData.comment && dayData.comment.trim()) {
        const d = dayData.date;
        const dayLabel = ["Bugun", "Ertaga", "Indinga"][dayIndex];
        commentEl.innerHTML = `<strong>📋 ${dayLabel} (${d.getDate()} ${MONTHS_UZ[d.getMonth()]}):</strong> ${dayData.comment}`;
        commentEl.classList.add('visible');
    } else {
        commentEl.classList.remove('visible');
    }

    // Active button yangilash
    document.querySelectorAll('.map-day-btn').forEach((btn, idx) => {
        btn.classList.toggle('active', idx === dayIndex);
    });
}


// ============================================
// TELEGRAM FORMAT GENERATORI
// ============================================

function generateTelegramMessage() {
    let msg = '';

    for (let i = 0; i < 3; i++) {
        const day = forecastData.days[i];
        const d = day.date;
        const dayLabel = ["📅 BUGUN", "📅 ERTAGA", "📅 INDINGA"][i];
        const dateStr = `${d.getDate()} ${MONTHS_UZ[d.getMonth()]} (${DAYS_UZ[d.getDay()]})`;

        msg += `${dayLabel} — ${dateStr}\n`;
        msg += `━━━━━━━━━━━━━━━━━━━━\n`;

        // Shaharlar
        let hasCityData = false;
        CITIES.forEach(city => {
            const data = day.cities[city.id];
            if (!data || data.tempMax === null) return;
            hasCityData = true;

            const weatherInfo = getWeatherInfo(data.weather);
            const precipStr = data.precip > 0 ? ` 💧${data.precip}mm` : '';
            const windStr = data.wind ? ` 💨${data.wind}km/s` : '';

            msg += `${weatherInfo.icon} ${city.name}: ${data.tempMin ?? ''}°/${data.tempMax}°C${windStr}${precipStr}\n`;
        });

        if (!hasCityData) {
            msg += `   Ma'lumot kiritilmagan\n`;
        }

        // Izoh
        if (day.comment && day.comment.trim()) {
            msg += `\n📝 ${day.comment}\n`;
        }

        msg += `\n`;
    }

    msg += `━━━━━━━━━━━━━━━━━━━━\n`;
    msg += `📡 Manba: O'zgidromet\n`;
    msg += `🕐 Yangilangan: ${new Date().toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' })}`;

    return msg;
}

function showTelegramPreview() {
    const preview = document.getElementById('telegramPreview');
    const msgEl = document.getElementById('tgMessage');
    
    const msg = generateTelegramMessage();
    msgEl.textContent = msg;
    preview.style.display = 'block';
}

function copyTelegramMessage() {
    const msg = generateTelegramMessage();
    navigator.clipboard.writeText(msg).then(() => {
        const btn = document.getElementById('btnCopyTg');
        btn.textContent = '✅ Nusxa olindi!';
        setTimeout(() => { btn.textContent = '📋 Nusxa olish'; }, 2000);
    }).catch(() => {
        // Fallback
        const ta = document.createElement('textarea');
        ta.value = generateTelegramMessage();
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        alert('✅ Nusxa olindi!');
    });
}

// ============================================
// EKSPORT (RASM SIFATIDA)
// ============================================

function exportAsImage() {
    // leaflet-image kutubxonasi yo'q, shuning uchun oddiy screenshot tavsiya
    alert(
        "📸 Rasm sifatida saqlash:\n\n" +
        "1. Klaviaturada Ctrl+Shift+S (yoki Cmd+Shift+4 Mac'da)\n" +
        "2. Xarita sohasini tanlang\n" +
        "3. Rasm saqlanadi\n\n" +
        "Yoki brauzerda: O'ng tugma → 'Screenshot qilish'\n\n" +
        "💡 Kelajakda avtomatik PNG eksport qo'shiladi."
    );
}


// ============================================
// EVENT LISTENERS VA INIT
// ============================================

function goBackToInput() {
    document.getElementById('inputPanel').style.display = 'block';
    document.getElementById('mapPanel').style.display = 'none';
    document.getElementById('telegramPreview').style.display = 'none';
}

function clearAllData() {
    if (!confirm("⚠️ Barcha kiritilgan ma'lumotlar o'chiriladi. Davom etasizmi?")) return;
    
    forecastData.days.forEach(day => {
        day.cities = {};
        day.comment = '';
    });
    buildTable();
}

// DOM yuklanganda
document.addEventListener('DOMContentLoaded', function() {
    // Sanalarni o'rnatish
    initDates();
    
    // Jadvalni qurish
    buildTable();

    // Day tabs
    document.querySelectorAll('.day-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            switchDay(parseInt(this.dataset.day));
        });
    });

    // Izohni saqlash
    document.getElementById('dayComment').addEventListener('input', function() {
        forecastData.days[currentDay].comment = this.value;
    });

    // Tugmalar
    document.getElementById('btnGenerate').addEventListener('click', generateMap);
    document.getElementById('btnLoadSample').addEventListener('click', loadSampleData);
    document.getElementById('btnClearAll').addEventListener('click', clearAllData);
    document.getElementById('btnBackToInput').addEventListener('click', goBackToInput);
    document.getElementById('btnExportImage').addEventListener('click', exportAsImage);
    document.getElementById('btnTelegram').addEventListener('click', showTelegramPreview);
    document.getElementById('btnCopyTg').addEventListener('click', copyTelegramMessage);

    // Map day navigation
    document.querySelectorAll('.map-day-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            renderMapForDay(parseInt(this.dataset.day));
        });
    });
});
