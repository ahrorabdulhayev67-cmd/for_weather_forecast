/**
 * Ob-havo prognozi — Asosiy ilova
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
    { value: "jala", label: "Jala" },
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

// Namuna ma'lumotlari (yozgi prognoz)
const SAMPLE_DATA = {
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
};

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
    CITY_LIST.forEach(city => {
        if (SAMPLE_DATA[city]) {
            document.getElementById(`tmin_${city}`).value = SAMPLE_DATA[city].temp_min;
            document.getElementById(`tmax_${city}`).value = SAMPLE_DATA[city].temp_max;
            document.getElementById(`weather_${city}`).value = SAMPLE_DATA[city].weather;
        }
    });
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
function generateMap() {
    const weatherData = collectData();
    
    if (Object.keys(weatherData).length === 0) {
        alert("Iltimos, kamida bitta shahar uchun harorat kiriting!");
        return;
    }

    const dateInput = document.getElementById('forecastDate').value;
    const dateStr = formatDate(dateInput);

    // SVG yaratish
    currentSvgContent = renderWeatherMap(weatherData, dateStr, "OB-HAVO PROGNOZI");

    // Ekranga chiqarish
    const container = document.getElementById('mapContainer');
    container.innerHTML = currentSvgContent;

    // Result panelni ko'rsatish
    document.getElementById('resultPanel').style.display = 'block';

    // Scroll to result
    document.getElementById('resultPanel').scrollIntoView({ behavior: 'smooth' });
}

// ===== YUKLAB OLISH =====
function downloadPng() {
    const svgElement = document.querySelector('#mapContainer svg');
    if (!svgElement) return;

    const dateInput = document.getElementById('forecastDate').value;
    const d = dateInput ? new Date(dateInput) : new Date();
    const filename = `ob-havo-prognozi_${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}.png`;

    downloadMapAsPng(svgElement, filename);
}

function downloadSvg() {
    if (!currentSvgContent) return;

    const dateInput = document.getElementById('forecastDate').value;
    const d = dateInput ? new Date(dateInput) : new Date();
    const filename = `ob-havo-prognozi_${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}.svg`;

    downloadMapAsSvg(currentSvgContent, filename);
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', function() {
    // Sana ko'rsatish
    const now = new Date();
    document.getElementById('currentDate').textContent = formatDate();

    // Bugungi sanani default qilish
    const dateInput = document.getElementById('forecastDate');
    dateInput.value = now.toISOString().split('T')[0];

    // Jadvalni yaratish
    buildTable();

    // Event listeners
    document.getElementById('btnGenerate').addEventListener('click', generateMap);
    document.getElementById('btnLoadSample').addEventListener('click', loadSampleData);
    document.getElementById('btnDownloadPng').addEventListener('click', downloadPng);
    document.getElementById('btnDownloadSvg').addEventListener('click', downloadSvg);
});
