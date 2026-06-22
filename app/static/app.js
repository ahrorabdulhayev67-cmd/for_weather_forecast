/**
 * Ob-havo prognozi — Asosiy ilova
 * Meteocons ikonkalar + SVG xarita + yuklab olish
 */

// Shaharlar ro'yxati
const CITY_LIST = [
    "Toshkent", "Samarqand", "Buxoro", "Namangan", "Andijon",
    "Farg'ona", "Qarshi", "Nukus", "Navoiy", "Termiz",
    "Jizzax", "Urganch", "Guliston"
];

// Ob-havo turlari
const WEATHER_OPTIONS = [
    { value: "ochiq", label: "Ochiq (quyoshli)" },
    { value: "qisman_bulutli", label: "Qisman bulutli" },
    { value: "bulutli", label: "Bulutli" },
    { value: "yomgir", label: "Yomg'ir" },
    { value: "jala", label: "Jala (mayda yomg'ir)" },
    { value: "momaqaldiroq", label: "Momaqaldiroq" },
    { value: "qor", label: "Qor" },
    { value: "tuman", label: "Tuman" },
    { value: "dol", label: "Do'l" },
    { value: "chang_boroni", label: "Chang bo'roni" },
    { value: "qor_boroni", label: "Qor bo'roni" }
];

// O'zbek oy nomlari
const MONTHS_UZ = ["yanvar", "fevral", "mart", "aprel", "may", "iyun",
    "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"];
const DAYS_UZ = ["yakshanba", "dushanba", "seshanba", "chorshanba",
    "payshanba", "juma", "shanba"];

// ===== NAMUNA MA'LUMOTLARI =====
const SAMPLE_SUMMER = {
    label: "Yozgi issiq kun",
    data: {
        "Toshkent": { temp_min: 22, temp_max: 38, weather: "ochiq" },
        "Samarqand": { temp_min: 18, temp_max: 35, weather: "qisman_bulutli" },
        "Buxoro": { temp_min: 24, temp_max: 42, weather: "ochiq" },
        "Namangan": { temp_min: 20, temp_max: 36, weather: "qisman_bulutli" },
        "Andijon": { temp_min: 19, temp_max: 34, weather: "yomgir" },
        "Farg'ona": { temp_min: 20, temp_max: 37, weather: "jala" },
        "Qarshi": { temp_min: 23, temp_max: 43, weather: "ochiq" },
        "Nukus": { temp_min: 20, temp_max: 40, weather: "ochiq" },
        "Navoiy": { temp_min: 22, temp_max: 41, weather: "qisman_bulutli" },
        "Termiz": { temp_min: 26, temp_max: 45, weather: "ochiq" },
        "Jizzax": { temp_min: 20, temp_max: 37, weather: "bulutli" },
        "Urganch": { temp_min: 21, temp_max: 39, weather: "ochiq" },
        "Guliston": { temp_min: 21, temp_max: 37, weather: "qisman_bulutli" }
    }
};

const SAMPLE_SPRING = {
    label: "Bahorgi yomg'irli kun",
    data: {
        "Toshkent": { temp_min: 12, temp_max: 22, weather: "yomgir" },
        "Samarqand": { temp_min: 10, temp_max: 20, weather: "yomgir" },
        "Buxoro": { temp_min: 14, temp_max: 25, weather: "qisman_bulutli" },
        "Namangan": { temp_min: 11, temp_max: 21, weather: "momaqaldiroq" },
        "Andijon": { temp_min: 10, temp_max: 19, weather: "yomgir" },
        "Farg'ona": { temp_min: 11, temp_max: 20, weather: "jala" },
        "Qarshi": { temp_min: 13, temp_max: 24, weather: "bulutli" },
        "Nukus": { temp_min: 9, temp_max: 18, weather: "chang_boroni" },
        "Navoiy": { temp_min: 12, temp_max: 23, weather: "bulutli" },
        "Termiz": { temp_min: 16, temp_max: 28, weather: "ochiq" },
        "Jizzax": { temp_min: 11, temp_max: 21, weather: "yomgir" },
        "Urganch": { temp_min: 10, temp_max: 19, weather: "bulutli" },
        "Guliston": { temp_min: 11, temp_max: 20, weather: "jala" }
    }
};

const SAMPLE_WINTER = {
    label: "Qishki sovuq kun",
    data: {
        "Toshkent": { temp_min: -3, temp_max: 5, weather: "qor" },
        "Samarqand": { temp_min: -5, temp_max: 3, weather: "qor" },
        "Buxoro": { temp_min: -2, temp_max: 6, weather: "tuman" },
        "Namangan": { temp_min: -6, temp_max: 2, weather: "qor" },
        "Andijon": { temp_min: -5, temp_max: 3, weather: "qor_boroni" },
        "Farg'ona": { temp_min: -4, temp_max: 4, weather: "qor" },
        "Qarshi": { temp_min: -1, temp_max: 7, weather: "bulutli" },
        "Nukus": { temp_min: -8, temp_max: 0, weather: "qor_boroni" },
        "Navoiy": { temp_min: -3, temp_max: 5, weather: "tuman" },
        "Termiz": { temp_min: 2, temp_max: 12, weather: "bulutli" },
        "Jizzax": { temp_min: -4, temp_max: 4, weather: "qor" },
        "Urganch": { temp_min: -6, temp_max: 1, weather: "qor" },
        "Guliston": { temp_min: -3, temp_max: 5, weather: "tuman" }
    }
};

const SAMPLES = [SAMPLE_SUMMER, SAMPLE_SPRING, SAMPLE_WINTER];
let currentSampleIndex = 0;

let currentSvgContent = '';

// ===== JADVAL YARATISH =====
function buildTable() {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    CITY_LIST.forEach(city => {
        const tr = document.createElement('tr');
        
        // Shahar nomi
        const tdCity = document.createElement('td');
        tdCity.textContent = city;
        tdCity.dataset.city = city;
        tr.appendChild(tdCity);

        // Temp min
        const tdMin = document.createElement('td');
        tdMin.innerHTML = `<input type="number" id="tmin_${city}" min="-30" max="55" step="1" placeholder="min">`;
        tr.appendChild(tdMin);

        // Temp max
        const tdMax = document.createElement('td');
        tdMax.innerHTML = `<input type="number" id="tmax_${city}" min="-30" max="55" step="1" placeholder="max">`;
        tr.appendChild(tdMax);

        // Weather type
        const tdWeather = document.createElement('td');
        let selectHtml = `<select id="weather_${city}">`;
        WEATHER_OPTIONS.forEach(opt => {
            selectHtml += `<option value="${opt.value}">${opt.label}</option>`;
        });
        selectHtml += '</select>';
        tdWeather.innerHTML = selectHtml;
        tr.appendChild(tdWeather);

        tbody.appendChild(tr);
    });
}

// ===== MA'LUMOTLARNI YIGISH =====
function collectData() {
    const data = {};
    CITY_LIST.forEach(city => {
        const tmin = document.getElementById(`tmin_${city}`).value;
        const tmax = document.getElementById(`tmax_${city}`).value;
        const weather = document.getElementById(`weather_${city}`).value;

        if (tmax !== '') {
            data[city] = {
                temp_min: tmin !== '' ? parseInt(tmin) : null,
                temp_max: parseInt(tmax),
                weather: weather
            };
        }
    });
    return data;
}

// ===== NAMUNA YUKLASH =====
function loadSampleData() {
    const sample = SAMPLES[currentSampleIndex];
    
    CITY_LIST.forEach(city => {
        if (sample.data[city]) {
            document.getElementById(`tmin_${city}`).value = sample.data[city].temp_min;
            document.getElementById(`tmax_${city}`).value = sample.data[city].temp_max;
            document.getElementById(`weather_${city}`).value = sample.data[city].weather;
        }
    });
    
    // Update button text to show which sample
    const btn = document.getElementById('btnLoadSample');
    btn.textContent = `Namuna: ${sample.label}`;
    
    // Cycle to next sample
    currentSampleIndex = (currentSampleIndex + 1) % SAMPLES.length;
    
    // Show notification
    showNotification(`"${sample.label}" namunasi yuklandi`);
}

// ===== NOTIFICATION =====
function showNotification(message) {
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.style.cssText = 'position:fixed;top:20px;right:20px;background:#1a3a5c;color:white;padding:12px 20px;border-radius:8px;font-size:13px;z-index:1000;opacity:0;transition:opacity 0.3s;box-shadow:0 4px 12px rgba(0,0,0,0.2)';
        document.body.appendChild(notification);
    }
    notification.textContent = message;
    notification.style.opacity = '1';
    setTimeout(() => { notification.style.opacity = '0'; }, 2500);
}

// ===== SANA FORMATLASH =====
function formatDate(dateStr) {
    if (!dateStr) {
        const now = new Date();
        const day = now.getDate();
        const month = MONTHS_UZ[now.getMonth()];
        const year = now.getFullYear();
        const dayName = DAYS_UZ[now.getDay()];
        return `${day} ${month} ${year} yil, ${dayName}`;
    }
    const d = new Date(dateStr);
    const day = d.getDate();
    const month = MONTHS_UZ[d.getMonth()];
    const year = d.getFullYear();
    const dayName = DAYS_UZ[d.getDay()];
    return `${day} ${month} ${year} yil, ${dayName}`;
}

// ===== XARITA GENERATSIYA =====
async function generateMap() {
    const weatherData = collectData();
    
    if (Object.keys(weatherData).length === 0) {
        showNotification("Iltimos, kamida bitta shahar uchun harorat kiriting!");
        return;
    }

    // Show loading state
    const btn = document.getElementById('btnGenerate');
    btn.textContent = 'Yaratilmoqda...';
    btn.disabled = true;

    const dateInput = document.getElementById('forecastDate').value;

    // Server'ga yuborish — rasm generatsiya
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                days: [{
                    date: dateInput || new Date().toISOString().split('T')[0],
                    day_index: 0,
                    cities: weatherData,
                    comment: ""
                }]
            })
        });
        const result = await response.json();

        if (result.success && result.images && result.images.length > 0) {
            // Server rasm qaytardi — ko'rsatish
            const container = document.getElementById('mapContainer');
            container.innerHTML = '<img src="' + result.images[0] + '" style="width:100%;border-radius:8px;" alt="Prognoz xaritasi">';
            document.getElementById('resultPanel').style.display = 'block';
            document.getElementById('resultPanel').scrollIntoView({ behavior: 'smooth' });
            showNotification("Prognoz rasmi muvaffaqiyatli yaratildi!");
        } else {
            // Fallback: lokal SVG
            await generateMapLocal(weatherData, dateInput);
        }
    } catch (err) {
        // Offline — lokal SVG
        await generateMapLocal(weatherData, dateInput);
    }

    btn.textContent = 'Xaritani yaratish';
    btn.disabled = false;
}

// Lokal SVG fallback
async function generateMapLocal(weatherData, dateInput) {
    if (Object.keys(iconCache).length === 0) {
        await loadIconsAsDataURIs();
    }
    const dateStr = formatDate(dateInput);
    currentSvgContent = renderWeatherMap(weatherData, dateStr, "OB-HAVO PROGNOZI");
    const container = document.getElementById('mapContainer');
    container.innerHTML = currentSvgContent;
    document.getElementById('resultPanel').style.display = 'block';
    document.getElementById('resultPanel').scrollIntoView({ behavior: 'smooth' });
    showNotification("Xarita yaratildi (lokal rejim)");
}

// ===== YUKLAB OLISH =====
function downloadPng() {
    const svgElement = document.querySelector('#mapContainer svg');
    if (!svgElement) {
        showNotification("Avval xaritani yarating!");
        return;
    }

    const dateInput = document.getElementById('forecastDate').value;
    const d = dateInput ? new Date(dateInput) : new Date();
    const filename = `ob-havo-prognozi_${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}.png`;

    downloadMapAsPng(svgElement, filename);
    showNotification("PNG yuklab olinmoqda...");
}

function downloadSvg() {
    if (!currentSvgContent) {
        showNotification("Avval xaritani yarating!");
        return;
    }

    const dateInput = document.getElementById('forecastDate').value;
    const d = dateInput ? new Date(dateInput) : new Date();
    const filename = `ob-havo-prognozi_${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}.svg`;

    downloadMapAsSvg(currentSvgContent, filename);
    showNotification("SVG yuklab olinmoqda...");
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Sana ko'rsatish
    document.getElementById('currentDate').textContent = formatDate();

    // Bugungi sanani default qilish
    const dateInput = document.getElementById('forecastDate');
    const now = new Date();
    dateInput.value = now.toISOString().split('T')[0];

    // Jadvalni yaratish
    buildTable();

    // Event listeners
    document.getElementById('btnGenerate').addEventListener('click', generateMap);
    document.getElementById('btnLoadSample').addEventListener('click', loadSampleData);
    document.getElementById('btnDownloadPng').addEventListener('click', downloadPng);
    document.getElementById('btnDownloadSvg').addEventListener('click', downloadSvg);

    // Matn rejimi
    document.getElementById('btnModeText').addEventListener('click', function() {
        document.getElementById('textModeBlock').style.display = 'block';
        document.querySelector('.table-container').style.display = 'none';
        document.querySelector('.action-bar').style.display = 'none';
        this.classList.add('btn-primary');
        this.classList.remove('btn-outline');
    });
    document.getElementById('btnBackToTable').addEventListener('click', function() {
        document.getElementById('textModeBlock').style.display = 'none';
        document.querySelector('.table-container').style.display = '';
        document.querySelector('.action-bar').style.display = '';
        document.getElementById('btnModeText').classList.remove('btn-primary');
        document.getElementById('btnModeText').classList.add('btn-outline');
    });
    document.getElementById('btnParseText').addEventListener('click', generateFromText);
    
    // Preload icons in background
    loadIconsAsDataURIs();
});

// ===== MATN REJIMI — TG matnidan rasm yaratish =====
function generateFromText() {
    var text = document.getElementById('rawForecastText').value.trim();
    if (!text) {
        alert("Iltimos, O'zgidromet Telegram matnini kiriting!");
        return;
    }

    var dateInput = document.getElementById('forecastDate');
    var dateVal = dateInput ? dateInput.value : '';

    fetch('/api/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({raw_text: text, date: dateVal})
    })
    .then(function(r) { return r.json(); })
    .then(function(result) {
        if (result.success) {
            // Natijani ko'rsatish
            var resultPanel = document.getElementById('resultPanel');
            if (resultPanel) resultPanel.style.display = 'block';
            // Rasmni ko'rsatish
            if (result.images && result.images.length > 0) {
                var imgEl = document.getElementById('resultImage');
                if (imgEl) imgEl.src = result.images[0];
            }
            alert("Prognoz muvaffaqiyatli yaratildi!");
        } else {
            alert("Xatolik: " + (result.error || "Noma'lum"));
        }
    })
    .catch(function(err) {
        alert("Server bilan bog'lanib bo'lmadi: " + err.message);
    });
}
