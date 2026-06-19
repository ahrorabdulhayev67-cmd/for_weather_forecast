// ============================================
// GIDROMETEOROLOGIYA XIZMATI — PROGNOZ TIZIMI
// ============================================

// Viloyat markazlari
const CITIES = [
    "Toshkent", "Samarqand", "Buxoro", "Namangan",
    "Andijon", "Farg'ona", "Qarshi", "Nukus",
    "Navoiy", "Termiz", "Jizzax", "Urganch",
    "Guliston", "Shahrisabz"
];


// Ob-havo hodisalari (WMO va O'zgidromet standartlariga mos)
const WEATHER_TYPES = [
    { code: "ochiq",         label: "Havo ochiq" },
    { code: "qisman_bulutli", label: "Qisman bulutli" },
    { code: "bulutli",       label: "Bulutli" },
    { code: "tuman",         label: "Tuman" },
    { code: "yomgir",        label: "Yomg'ir" },
    { code: "jala",          label: "Jala" },
    { code: "momaqaldiroq",  label: "Momaqaldiroq" },
    { code: "qor",           label: "Qor" },
    { code: "dol",           label: "Do'l" },
    { code: "chang_boroni",  label: "Chang bo'roni" },
    { code: "qor_boroni",    label: "Qor bo'roni" },
];

// Hafta kunlari, oylar
const DAYS = ["yakshanba","dushanba","seshanba","chorshanba",
              "payshanba","juma","shanba"];
const MONTHS = ["yanvar","fevral","mart","aprel","may","iyun",
                "iyul","avgust","sentabr","oktabr","noyabr","dekabr"];


// ===== MA'LUMOTLAR TUZILMASI =====
let forecastData = {
    days: [
        { date: null, comment: "", cities: {} },
        { date: null, comment: "", cities: {} },
        { date: null, comment: "", cities: {} },
    ]
};
let currentDay = 0;

// ===== INIT =====
document.addEventListener("DOMContentLoaded", function () {
    initDates();
    buildTable();
    bindEvents();
});

function initDates() {
    const today = new Date();
    for (let i = 0; i < 3; i++) {
        const d = new Date(today);
        d.setDate(d.getDate() + i);
        forecastData.days[i].date = d;
    }
    document.getElementById("currentDate").textContent =
        formatDate(today);
    updateDayNav();
}

function formatDate(d) {
    return `${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}, ${DAYS[d.getDay()]}`;
}

function updateDayNav() {
    document.querySelectorAll(".day-nav .day-btn").forEach((btn, i) => {
        const d = forecastData.days[i].date;
        if (d) {
            const labels = ["I kun","II kun","III kun"];
            btn.textContent = `${labels[i]} — ${d.getDate()}.${String(d.getMonth()+1).padStart(2,"0")}`;
        }
    });
}


// ===== JADVAL =====
function buildTable() {
    const tbody = document.getElementById("tableBody");
    tbody.innerHTML = "";
    const cities = forecastData.days[currentDay].cities;

    CITIES.forEach(name => {
        const d = cities[name] || {};
        const row = document.createElement("tr");

        let opts = WEATHER_TYPES.map(w =>
            `<option value="${w.code}" ${d.weather===w.code?"selected":""}>${w.label}</option>`
        ).join("");

        row.innerHTML = `
            <td>${name}</td>
            <td><input type="number" data-city="${name}" data-field="temp_min"
                value="${d.temp_min ?? ""}" step="1" min="-40" max="55"></td>
            <td><input type="number" data-city="${name}" data-field="temp_max"
                value="${d.temp_max ?? ""}" step="1" min="-40" max="55"></td>
            <td><input type="number" data-city="${name}" data-field="wind"
                value="${d.wind ?? ""}" step="1" min="0" max="50"></td>
            <td><input type="number" data-city="${name}" data-field="precip"
                value="${d.precip ?? ""}" step="0.1" min="0" max="200"></td>
            <td><select data-city="${name}" data-field="weather">${opts}</select></td>
        `;
        tbody.appendChild(row);
    });

    // Izoh
    document.getElementById("comment").value =
        forecastData.days[currentDay].comment || "";

    // Inputlarni kuzatish
    tbody.querySelectorAll("input, select").forEach(el => {
        el.addEventListener("change", saveField);
    });
}

function saveField(e) {
    const city = e.target.dataset.city;
    const field = e.target.dataset.field;
    if (!forecastData.days[currentDay].cities[city])
        forecastData.days[currentDay].cities[city] = {};
    let val = e.target.type === "number"
        ? (e.target.value === "" ? null : parseFloat(e.target.value))
        : e.target.value;
    forecastData.days[currentDay].cities[city][field] = val;
}


// ===== EVENT BINDINGS =====
function bindEvents() {
    // Day tabs (kiritish)
    document.querySelectorAll("#inputSection .day-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            saveComment();
            currentDay = parseInt(this.dataset.day);
            document.querySelectorAll("#inputSection .day-btn")
                .forEach((b,i) => b.classList.toggle("active", i===currentDay));
            buildTable();
        });
    });

    // Comment auto-save
    document.getElementById("comment").addEventListener("input", function () {
        forecastData.days[currentDay].comment = this.value;
    });

    // Buttons
    document.getElementById("btnGenerate").addEventListener("click", generate);
    document.getElementById("btnSample").addEventListener("click", loadSample);
    document.getElementById("btnClear").addEventListener("click", clearAll);
    document.getElementById("btnBack").addEventListener("click", goBack);
    document.getElementById("btnCopy").addEventListener("click", copyTelegram);
    document.getElementById("btnDownload").addEventListener("click", downloadImage);

    // Result day tabs
    document.querySelectorAll(".result-day-nav .day-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const day = parseInt(this.dataset.day);
            document.querySelectorAll(".result-day-nav .day-btn")
                .forEach((b,i) => b.classList.toggle("active", i===day));
            showDayResult(day);
        });
    });
}

function saveComment() {
    forecastData.days[currentDay].comment = document.getElementById("comment").value;
}

function goBack() {
    document.getElementById("inputSection").style.display = "";
    document.getElementById("resultSection").style.display = "none";
}

function clearAll() {
    if (!confirm("Barcha ma'lumotlar o'chirilsinmi?")) return;
    forecastData.days.forEach(d => { d.cities = {}; d.comment = ""; });
    buildTable();
}


// ===== GENERATSIYA =====
function generate() {
    saveComment();

    // Tekshirish
    let hasData = false;
    for (const day of forecastData.days) {
        for (const c in day.cities) {
            if (day.cities[c].temp_max != null) { hasData = true; break; }
        }
        if (hasData) break;
    }
    if (!hasData) {
        alert("Kamida bitta shahar uchun harorat kiriting.\n\nYoki \"Namuna yuklash\" tugmasini bosing.");
        return;
    }

    // Serverga yuborish
    const payload = forecastData.days.map((d,i) => ({
        date: d.date ? d.date.toISOString().slice(0,10) : null,
        day_index: i,
        comment: d.comment,
        cities: d.cities
    }));

    document.getElementById("btnGenerate").textContent = "Yaratilmoqda...";
    document.getElementById("btnGenerate").disabled = true;

    fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ days: payload })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            document.getElementById("inputSection").style.display = "none";
            document.getElementById("resultSection").style.display = "";
            window._resultData = data;
            showDayResult(0);
        } else {
            alert("Xatolik: " + (data.error || "Noma'lum xato"));
        }
    })
    .catch(err => {
        alert("Server bilan aloqa xatosi: " + err.message);
    })
    .finally(() => {
        document.getElementById("btnGenerate").textContent = "Xarita va prognozni shakllantirish";
        document.getElementById("btnGenerate").disabled = false;
    });
}

function showDayResult(dayIndex) {
    const data = window._resultData;
    if (!data) return;
    const img = document.getElementById("forecastImage");
    img.src = data.images[dayIndex] + "?t=" + Date.now();
    document.getElementById("telegramText").textContent = data.telegram[dayIndex];
}

function copyTelegram() {
    const text = document.getElementById("telegramText").textContent;
    navigator.clipboard.writeText(text).then(() => {
        document.getElementById("btnCopy").textContent = "Nusxa olindi!";
        setTimeout(() => { document.getElementById("btnCopy").textContent = "Nusxa olish"; }, 2000);
    });
}

function downloadImage() {
    const src = document.getElementById("forecastImage").src;
    if (!src) return;
    const a = document.createElement("a");
    a.href = src; a.download = "prognoz.png"; a.click();
}


// ===== NAMUNA MA'LUMOTLAR =====
function loadSample() {
    const sample = [
        {
            comment: "Respublika hududida harorat mavsumiy me'yordan 3–5°C yuqori saqlanadi. Farg'ona vodiysida mahalliy momaqaldiroqli yog'ingarchilik ehtimoli bor.",
            cities: {
                "Toshkent":   { temp_min:22, temp_max:36, wind:4, precip:0, weather:"ochiq" },
                "Samarqand":  { temp_min:18, temp_max:33, wind:3, precip:0, weather:"qisman_bulutli" },
                "Buxoro":     { temp_min:24, temp_max:40, wind:5, precip:0, weather:"ochiq" },
                "Namangan":   { temp_min:20, temp_max:35, wind:3, precip:0, weather:"qisman_bulutli" },
                "Andijon":    { temp_min:21, temp_max:34, wind:3, precip:2, weather:"jala" },
                "Farg'ona":   { temp_min:22, temp_max:38, wind:2, precip:0, weather:"ochiq" },
                "Qarshi":     { temp_min:23, temp_max:41, wind:4, precip:0, weather:"ochiq" },
                "Nukus":      { temp_min:20, temp_max:38, wind:6, precip:0, weather:"qisman_bulutli" },
                "Navoiy":     { temp_min:21, temp_max:39, wind:5, precip:0, weather:"ochiq" },
                "Termiz":     { temp_min:26, temp_max:44, wind:3, precip:0, weather:"ochiq" },
                "Jizzax":     { temp_min:20, temp_max:36, wind:4, precip:0, weather:"bulutli" },
                "Urganch":    { temp_min:21, temp_max:37, wind:5, precip:0, weather:"qisman_bulutli" },
                "Guliston":   { temp_min:21, temp_max:35, wind:3, precip:0, weather:"qisman_bulutli" },
                "Shahrisabz": { temp_min:19, temp_max:34, wind:2, precip:0, weather:"bulutli" },
            }
        },
        {
            comment: "Shimoliy-sharqiy hududlarda noturg'un ob-havo: momaqaldiroqli yog'ingarchilik, joylariga selsimon oqimlar ehtimoli. Xorazm, Qoraqalpog'istonda shamol kuchayadi (15–18 m/s).",
            cities: {
                "Toshkent":   { temp_min:21, temp_max:34, wind:5, precip:3, weather:"yomgir" },
                "Samarqand":  { temp_min:17, temp_max:31, wind:4, precip:5, weather:"yomgir" },
                "Buxoro":     { temp_min:23, temp_max:38, wind:6, precip:0, weather:"bulutli" },
                "Namangan":   { temp_min:19, temp_max:33, wind:5, precip:8, weather:"momaqaldiroq" },
                "Andijon":    { temp_min:20, temp_max:32, wind:4, precip:10, weather:"momaqaldiroq" },
                "Farg'ona":   { temp_min:21, temp_max:35, wind:3, precip:5, weather:"yomgir" },
                "Qarshi":     { temp_min:22, temp_max:39, wind:5, precip:0, weather:"qisman_bulutli" },
                "Nukus":      { temp_min:19, temp_max:36, wind:8, precip:0, weather:"chang_boroni" },
                "Navoiy":     { temp_min:20, temp_max:37, wind:6, precip:0, weather:"bulutli" },
                "Termiz":     { temp_min:25, temp_max:42, wind:4, precip:0, weather:"ochiq" },
                "Jizzax":     { temp_min:19, temp_max:34, wind:4, precip:2, weather:"jala" },
                "Urganch":    { temp_min:20, temp_max:35, wind:7, precip:0, weather:"chang_boroni" },
                "Guliston":   { temp_min:20, temp_max:33, wind:4, precip:1, weather:"jala" },
                "Shahrisabz": { temp_min:18, temp_max:32, wind:3, precip:4, weather:"yomgir" },
            }
        },
        {
            comment: "Ob-havo barqarorlashadi. Yog'ingarchilik kutilmaydi. Harorat asta-sekin pasayadi.",
            cities: {
                "Toshkent":   { temp_min:20, temp_max:32, wind:3, precip:0, weather:"qisman_bulutli" },
                "Samarqand":  { temp_min:16, temp_max:30, wind:2, precip:0, weather:"qisman_bulutli" },
                "Buxoro":     { temp_min:22, temp_max:37, wind:4, precip:0, weather:"qisman_bulutli" },
                "Namangan":   { temp_min:18, temp_max:31, wind:3, precip:0, weather:"bulutli" },
                "Andijon":    { temp_min:19, temp_max:30, wind:2, precip:0, weather:"bulutli" },
                "Farg'ona":   { temp_min:20, temp_max:33, wind:2, precip:0, weather:"qisman_bulutli" },
                "Qarshi":     { temp_min:21, temp_max:38, wind:3, precip:0, weather:"ochiq" },
                "Nukus":      { temp_min:18, temp_max:35, wind:5, precip:0, weather:"qisman_bulutli" },
                "Navoiy":     { temp_min:19, temp_max:36, wind:4, precip:0, weather:"qisman_bulutli" },
                "Termiz":     { temp_min:24, temp_max:41, wind:3, precip:0, weather:"ochiq" },
                "Jizzax":     { temp_min:18, temp_max:33, wind:3, precip:0, weather:"qisman_bulutli" },
                "Urganch":    { temp_min:19, temp_max:34, wind:4, precip:0, weather:"bulutli" },
                "Guliston":   { temp_min:19, temp_max:32, wind:3, precip:0, weather:"qisman_bulutli" },
                "Shahrisabz": { temp_min:17, temp_max:31, wind:2, precip:0, weather:"qisman_bulutli" },
            }
        }
    ];

    for (let i = 0; i < 3; i++) {
        forecastData.days[i].cities = sample[i].cities;
        forecastData.days[i].comment = sample[i].comment;
    }
    buildTable();
    alert("Namuna ma'lumotlar yuklandi.");
}


// Ob-havo hodisalari (WMO va O'zgidromet terminologiyasi)
const WEATHER_TYPES = [
    { code: "ochiq",          label: "Havo ochiq" },
    { code: "qisman_bulutli", label: "Qisman bulutli" },
    { code: "bulutli",        label: "Bulutli" },
    { code: "tuman",          label: "Tuman" },
    { code: "yomgir",         label: "Yomg'ir" },
    { code: "jala",           label: "Jala" },
    { code: "momaqaldiroq",   label: "Momaqaldiroq" },
    { code: "qor",            label: "Qor" },
    { code: "dol",            label: "Do'l" },
    { code: "chang_boroni",   label: "Chang bo'roni" },
    { code: "qor_boroni",     label: "Qor bo'roni" },
];

const DAYS = ["yakshanba","dushanba","seshanba","chorshanba","payshanba","juma","shanba"];
const MONTHS = ["yanvar","fevral","mart","aprel","may","iyun","iyul","avgust","sentabr","oktabr","noyabr","dekabr"];


// ===== JADVAL =====
function buildTable() {
    const tbody = document.getElementById("tableBody");
    tbody.innerHTML = "";
    const cities = forecastData.days[currentDay].cities;

    CITIES.forEach(name => {
        const d = cities[name] || {};
        const row = document.createElement("tr");
        let opts = WEATHER_TYPES.map(w =>
            `<option value="${w.code}" ${d.weather===w.code?"selected":""}>${w.label}</option>`
        ).join("");

        row.innerHTML = `
            <td>${name}</td>
            <td><input type="number" data-city="${name}" data-field="temp_min" value="${d.temp_min??"}" step="1" min="-40" max="55"></td>
            <td><input type="number" data-city="${name}" data-field="temp_max" value="${d.temp_max??"}" step="1" min="-40" max="55"></td>
            <td><input type="number" data-city="${name}" data-field="wind" value="${d.wind??"}" step="1" min="0" max="50"></td>
            <td><input type="number" data-city="${name}" data-field="precip" value="${d.precip??"}" step="0.1" min="0" max="200"></td>
            <td><select data-city="${name}" data-field="weather">${opts}</select></td>
        `;
        tbody.appendChild(row);
    });

    document.getElementById("comment").value = forecastData.days[currentDay].comment || "";
    tbody.querySelectorAll("input,select").forEach(el => el.addEventListener("change", saveField));
}

function saveField(e) {
    const city = e.target.dataset.city, field = e.target.dataset.field;
    if (!forecastData.days[currentDay].cities[city])
        forecastData.days[currentDay].cities[city] = {};
    forecastData.days[currentDay].cities[city][field] =
        e.target.type==="number" ? (e.target.value===""?null:parseFloat(e.target.value)) : e.target.value;
}


// ===== EVENTLAR =====
function bindEvents() {
    document.querySelectorAll("#inputSection .day-btn").forEach(btn => {
        btn.addEventListener("click", function(){
            saveComment(); currentDay=parseInt(this.dataset.day);
            document.querySelectorAll("#inputSection .day-btn").forEach((b,i)=>b.classList.toggle("active",i===currentDay));
            buildTable();
        });
    });
    document.getElementById("comment").addEventListener("input", function(){ forecastData.days[currentDay].comment=this.value; });
    document.getElementById("btnGenerate").addEventListener("click", generate);
    document.getElementById("btnSample").addEventListener("click", loadSample);
    document.getElementById("btnClear").addEventListener("click", function(){
        if(!confirm("Barcha ma'lumotlar o'chirilsinmi?"))return;
        forecastData.days.forEach(d=>{d.cities={};d.comment="";});
        buildTable();
    });
    document.getElementById("btnBack").addEventListener("click", function(){
        document.getElementById("inputSection").style.display="";
        document.getElementById("resultSection").style.display="none";
    });
    document.getElementById("btnCopy").addEventListener("click", function(){
        navigator.clipboard.writeText(document.getElementById("telegramText").textContent).then(()=>{
            this.textContent="Nusxa olindi!"; setTimeout(()=>{this.textContent="Nusxa olish";},2000);
        });
    });
    document.getElementById("btnDownload").addEventListener("click", function(){
        const s=document.getElementById("forecastImage").src;
        if(s){const a=document.createElement("a");a.href=s;a.download="prognoz.png";a.click();}
    });
    document.querySelectorAll(".result-day-nav .day-btn").forEach(btn=>{
        btn.addEventListener("click",function(){
            const d=parseInt(this.dataset.day);
            document.querySelectorAll(".result-day-nav .day-btn").forEach((b,i)=>b.classList.toggle("active",i===d));
            showDayResult(d);
        });
    });
}
function saveComment(){forecastData.days[currentDay].comment=document.getElementById("comment").value;}


// ===== GENERATSIYA =====
function generate() {
    saveComment();
    let hasData=false;
    for(const day of forecastData.days)for(const c in day.cities)if(day.cities[c].temp_max!=null){hasData=true;break;}
    if(!hasData){alert("Kamida bitta shahar uchun harorat kiriting.");return;}

    const payload=forecastData.days.map((d,i)=>({
        date:d.date?d.date.toISOString().slice(0,10):null, day_index:i, comment:d.comment, cities:d.cities
    }));
    document.getElementById("btnGenerate").textContent="Yaratilmoqda...";
    document.getElementById("btnGenerate").disabled=true;

    fetch("/api/generate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({days:payload})})
    .then(r=>r.json()).then(data=>{
        if(data.success){
            document.getElementById("inputSection").style.display="none";
            document.getElementById("resultSection").style.display="";
            window._resultData=data; showDayResult(0);
        } else alert("Xatolik: "+(data.error||"Noma'lum"));
    }).catch(err=>alert("Server xatosi: "+err.message))
    .finally(()=>{
        document.getElementById("btnGenerate").textContent="Xarita va prognozni shakllantirish";
        document.getElementById("btnGenerate").disabled=false;
    });
}
function showDayResult(i){
    const data=window._resultData; if(!data)return;
    document.getElementById("forecastImage").src=data.images[i]+"?t="+Date.now();
    document.getElementById("telegramText").textContent=data.telegram[i];
}


// ===== NAMUNA =====
function loadSample(){
    const S=[
        {comment:"Respublika hududida harorat mavsumiy me'yordan 3–5°C yuqori. Farg'ona vodiysida momaqaldiroqli yog'ingarchilik ehtimoli bor.",
         cities:{
            "Toshkent":{temp_min:22,temp_max:36,wind:4,precip:0,weather:"ochiq"},
            "Samarqand":{temp_min:18,temp_max:33,wind:3,precip:0,weather:"qisman_bulutli"},
            "Buxoro":{temp_min:24,temp_max:40,wind:5,precip:0,weather:"ochiq"},
            "Namangan":{temp_min:20,temp_max:35,wind:3,precip:0,weather:"qisman_bulutli"},
            "Andijon":{temp_min:21,temp_max:34,wind:3,precip:2,weather:"jala"},
            "Farg'ona":{temp_min:22,temp_max:38,wind:2,precip:0,weather:"ochiq"},
            "Qarshi":{temp_min:23,temp_max:41,wind:4,precip:0,weather:"ochiq"},
            "Nukus":{temp_min:20,temp_max:38,wind:6,precip:0,weather:"qisman_bulutli"},
            "Navoiy":{temp_min:21,temp_max:39,wind:5,precip:0,weather:"ochiq"},
            "Termiz":{temp_min:26,temp_max:44,wind:3,precip:0,weather:"ochiq"},
            "Jizzax":{temp_min:20,temp_max:36,wind:4,precip:0,weather:"bulutli"},
            "Urganch":{temp_min:21,temp_max:37,wind:5,precip:0,weather:"qisman_bulutli"},
            "Guliston":{temp_min:21,temp_max:35,wind:3,precip:0,weather:"qisman_bulutli"},
            "Shahrisabz":{temp_min:19,temp_max:34,wind:2,precip:0,weather:"bulutli"}}},
        {comment:"Shimoliy-sharqda momaqaldiroqli yog'ingarchilik. Xorazm, Qoraqalpog'istonda shamol 15–18 m/s gacha kuchayadi.",
         cities:{
            "Toshkent":{temp_min:21,temp_max:34,wind:5,precip:3,weather:"yomgir"},
            "Samarqand":{temp_min:17,temp_max:31,wind:4,precip:5,weather:"yomgir"},
            "Buxoro":{temp_min:23,temp_max:38,wind:6,precip:0,weather:"bulutli"},
            "Namangan":{temp_min:19,temp_max:33,wind:5,precip:8,weather:"momaqaldiroq"},
            "Andijon":{temp_min:20,temp_max:32,wind:4,precip:10,weather:"momaqaldiroq"},
            "Farg'ona":{temp_min:21,temp_max:35,wind:3,precip:5,weather:"yomgir"},
            "Qarshi":{temp_min:22,temp_max:39,wind:5,precip:0,weather:"qisman_bulutli"},
            "Nukus":{temp_min:19,temp_max:36,wind:8,precip:0,weather:"chang_boroni"},
            "Navoiy":{temp_min:20,temp_max:37,wind:6,precip:0,weather:"bulutli"},
            "Termiz":{temp_min:25,temp_max:42,wind:4,precip:0,weather:"ochiq"},
            "Jizzax":{temp_min:19,temp_max:34,wind:4,precip:2,weather:"jala"},
            "Urganch":{temp_min:20,temp_max:35,wind:7,precip:0,weather:"chang_boroni"},
            "Guliston":{temp_min:20,temp_max:33,wind:4,precip:1,weather:"jala"},
            "Shahrisabz":{temp_min:18,temp_max:32,wind:3,precip:4,weather:"yomgir"}}},
        {comment:"Ob-havo barqarorlashadi. Yog'ingarchilik kutilmaydi.",
         cities:{
            "Toshkent":{temp_min:20,temp_max:32,wind:3,precip:0,weather:"qisman_bulutli"},
            "Samarqand":{temp_min:16,temp_max:30,wind:2,precip:0,weather:"qisman_bulutli"},
            "Buxoro":{temp_min:22,temp_max:37,wind:4,precip:0,weather:"qisman_bulutli"},
            "Namangan":{temp_min:18,temp_max:31,wind:3,precip:0,weather:"bulutli"},
            "Andijon":{temp_min:19,temp_max:30,wind:2,precip:0,weather:"bulutli"},
            "Farg'ona":{temp_min:20,temp_max:33,wind:2,precip:0,weather:"qisman_bulutli"},
            "Qarshi":{temp_min:21,temp_max:38,wind:3,precip:0,weather:"ochiq"},
            "Nukus":{temp_min:18,temp_max:35,wind:5,precip:0,weather:"qisman_bulutli"},
            "Navoiy":{temp_min:19,temp_max:36,wind:4,precip:0,weather:"qisman_bulutli"},
            "Termiz":{temp_min:24,temp_max:41,wind:3,precip:0,weather:"ochiq"},
            "Jizzax":{temp_min:18,temp_max:33,wind:3,precip:0,weather:"qisman_bulutli"},
            "Urganch":{temp_min:19,temp_max:34,wind:4,precip:0,weather:"bulutli"},
            "Guliston":{temp_min:19,temp_max:32,wind:3,precip:0,weather:"qisman_bulutli"},
            "Shahrisabz":{temp_min:17,temp_max:31,wind:2,precip:0,weather:"qisman_bulutli"}}}
    ];
    for(let i=0;i<3;i++){forecastData.days[i].cities=S[i].cities;forecastData.days[i].comment=S[i].comment;}
    buildTable();
}
