/**
 * O'zgidromet — 3 kunlik ob-havo prognozi tizimi
 * Frontend logic: data entry, map visualization, Telegram text
 */
(function() {
"use strict";

// === KONFIGURATSIYA ===
var CITIES = [
    "Toshkent","Samarqand","Buxoro","Namangan","Andijon",
    "Farg'ona","Qarshi","Nukus","Navoiy","Termiz",
    "Jizzax","Urganch","Guliston"
];

var WEATHER_OPTIONS = [
    {value:"ochiq", label:"\u2600\ufe0f Ochiq"},
    {value:"qisman_bulutli", label:"\u26c5 Qisman bulutli"},
    {value:"bulutli", label:"\u2601\ufe0f Bulutli"},
    {value:"tuman", label:"\ud83c\udf2b\ufe0f Tuman"},
    {value:"yomgir", label:"\ud83c\udf27\ufe0f Yomg\u2018ir"},
    {value:"jala", label:"\ud83c\udf26\ufe0f Jala"},
    {value:"momaqaldiroq", label:"\u26c8\ufe0f Momaqaldiroq"},
    {value:"qor", label:"\u2744\ufe0f Qor"},
    {value:"dol", label:"\ud83c\udf28\ufe0f Do\u2018l"},
    {value:"chang_boroni", label:"\ud83d\udca8 Chang bo\u2018roni"},
    {value:"qor_boroni", label:"\ud83c\udf2c\ufe0f Qor bo\u2018roni"}
];

var WEATHER_EMOJI = {
    "ochiq":"\u2600\ufe0f","qisman_bulutli":"\u26c5","bulutli":"\u2601\ufe0f",
    "tuman":"\ud83c\udf2b\ufe0f","yomgir":"\ud83c\udf27\ufe0f","jala":"\ud83c\udf26\ufe0f",
    "momaqaldiroq":"\u26c8\ufe0f","qor":"\u2744\ufe0f","dol":"\ud83c\udf28\ufe0f",
    "chang_boroni":"\ud83d\udca8","qor_boroni":"\ud83c\udf2c\ufe0f"
};

var WEATHER_LABELS = {
    "ochiq":"Ochiq","qisman_bulutli":"Qisman bulutli","bulutli":"Bulutli",
    "tuman":"Tuman","yomgir":"Yomg\u2018ir","jala":"Jala",
    "momaqaldiroq":"Momaqaldiroq","qor":"Qor","dol":"Do\u2018l",
    "chang_boroni":"Chang bo\u2018roni","qor_boroni":"Qor bo\u2018roni"
};

var MONTHS_UZ = ["yanvar","fevral","mart","aprel","may","iyun",
    "iyul","avgust","sentabr","oktabr","noyabr","dekabr"];
var DAYS_UZ = ["yakshanba","dushanba","seshanba","chorshanba",
    "payshanba","juma","shanba"];


// === HOLAT ===
var currentDay = 0;
var daysData = [{}, {}, {}];
var daysComments = ["", "", ""];
var resultCurrentDay = 0;
var allDaysResult = null;

// === INITIALIZATION ===
document.addEventListener("DOMContentLoaded", function() {
    initDates();
    buildTable();
    bindDayTabs();
    bindActions();
    bindResultDayTabs();
});

// === SANA BOSHQARUVI ===
function initDates() {
    var today = new Date();
    var dateInput = document.getElementById("startDate");
    dateInput.value = fmtDate(today);
    updateDayLabels();
    dateInput.addEventListener("change", updateDayLabels);
    var headerMeta = document.getElementById("headerDate");
    headerMeta.textContent = today.getDate() + " " + MONTHS_UZ[today.getMonth()] + " " + today.getFullYear();
}

function updateDayLabels() {
    var startStr = document.getElementById("startDate").value;
    if (!startStr) return;
    var start = new Date(startStr);
    for (var i = 0; i < 3; i++) {
        var d = new Date(start);
        d.setDate(d.getDate() + i);
        var el = document.getElementById("dayDate" + i);
        if (el) el.textContent = d.getDate() + " " + MONTHS_UZ[d.getMonth()];
    }
}

function getDateForDay(dayIndex) {
    var startStr = document.getElementById("startDate").value;
    if (!startStr) return "";
    var d = new Date(startStr);
    d.setDate(d.getDate() + dayIndex);
    return fmtDate(d);
}

function fmtDate(d) {
    var y = d.getFullYear();
    var m = String(d.getMonth() + 1).padStart(2, "0");
    var day = String(d.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + day;
}

function formatDateUz(dateStr) {
    if (!dateStr) return "";
    var d = new Date(dateStr);
    return d.getDate() + " " + MONTHS_UZ[d.getMonth()] + ", " + DAYS_UZ[d.getDay()];
}


// === JADVAL YARATISH ===
function buildTable() {
    var tbody = document.getElementById("forecastTableBody");
    tbody.innerHTML = "";
    var weatherOpts = WEATHER_OPTIONS.map(function(o) {
        return '<option value="' + o.value + '">' + o.label + '</option>';
    }).join("");

    CITIES.forEach(function(city) {
        var tr = document.createElement("tr");
        tr.innerHTML =
            '<td>' + city + '</td>' +
            '<td><input type="number" step="1" data-city="' + city + '" data-field="temp_min" placeholder="\u2014"/></td>' +
            '<td><input type="number" step="1" data-city="' + city + '" data-field="temp_max" placeholder="\u2014"/></td>' +
            '<td><select data-city="' + city + '" data-field="weather">' + weatherOpts + '</select></td>' +
            '<td><input type="number" step="1" data-city="' + city + '" data-field="wind" placeholder="\u2014"/></td>' +
            '<td><input type="number" step="0.1" data-city="' + city + '" data-field="precip" placeholder="0"/></td>';
        tbody.appendChild(tr);
    });
}

// === KUN TABLARI ===
function bindDayTabs() {
    var navBtns = document.querySelectorAll("#dayNav .day-btn");
    navBtns.forEach(function(btn) {
        btn.addEventListener("click", function() {
            saveCurrentDayData();
            navBtns.forEach(function(b) { b.classList.remove("active"); });
            btn.classList.add("active");
            currentDay = parseInt(btn.getAttribute("data-day"));
            loadDayData(currentDay);
        });
    });
}

function saveCurrentDayData() {
    var data = {};
    CITIES.forEach(function(city) {
        var tmin = document.querySelector('[data-city="' + city + '"][data-field="temp_min"]');
        var tmax = document.querySelector('[data-city="' + city + '"][data-field="temp_max"]');
        var weather = document.querySelector('[data-city="' + city + '"][data-field="weather"]');
        var wind = document.querySelector('[data-city="' + city + '"][data-field="wind"]');
        var precip = document.querySelector('[data-city="' + city + '"][data-field="precip"]');
        data[city] = {
            temp_min: tmin && tmin.value !== "" ? parseInt(tmin.value) : null,
            temp_max: tmax && tmax.value !== "" ? parseInt(tmax.value) : null,
            weather: weather ? weather.value : "ochiq",
            wind: wind && wind.value !== "" ? parseInt(wind.value) : null,
            precip: precip && precip.value !== "" ? parseFloat(precip.value) : 0
        };
    });
    daysData[currentDay] = data;
    daysComments[currentDay] = document.getElementById("dayComment").value || "";
}

function loadDayData(dayIndex) {
    var data = daysData[dayIndex] || {};
    CITIES.forEach(function(city) {
        var info = data[city] || {};
        var tmin = document.querySelector('[data-city="' + city + '"][data-field="temp_min"]');
        var tmax = document.querySelector('[data-city="' + city + '"][data-field="temp_max"]');
        var weather = document.querySelector('[data-city="' + city + '"][data-field="weather"]');
        var wind = document.querySelector('[data-city="' + city + '"][data-field="wind"]');
        var precip = document.querySelector('[data-city="' + city + '"][data-field="precip"]');
        if (tmin) tmin.value = info.temp_min != null ? info.temp_min : "";
        if (tmax) tmax.value = info.temp_max != null ? info.temp_max : "";
        if (weather) weather.value = info.weather || "ochiq";
        if (wind) wind.value = info.wind != null ? info.wind : "";
        if (precip) precip.value = info.precip ? info.precip : "";
    });
    document.getElementById("dayComment").value = daysComments[dayIndex] || "";
}


// === HARAKATLAR ===
function bindActions() {
    document.getElementById("btnGenerate").addEventListener("click", handleGenerate);
    document.getElementById("btnClearAll").addEventListener("click", handleClear);
    document.getElementById("btnLoadLast").addEventListener("click", handleLoadLast);
    document.getElementById("btnBackToInput").addEventListener("click", function() {
        document.getElementById("resultPanel").classList.add("hidden");
        document.getElementById("inputPanel").classList.remove("hidden");
    });
    document.getElementById("btnCopyTelegram").addEventListener("click", copyTelegramAll);
    document.getElementById("btnCopyTgText").addEventListener("click", copyTelegramAll);
    document.getElementById("btnExportPNG").addEventListener("click", handleExportPNG);
}

// === GENERATSIYA ===
function handleGenerate() {
    saveCurrentDayData();

    var hasData = false;
    for (var i = 0; i < 3; i++) {
        for (var city in daysData[i]) {
            if (daysData[i][city] && daysData[i][city].temp_max != null) {
                hasData = true;
                break;
            }
        }
        if (hasData) break;
    }
    if (!hasData) {
        showToast("Kamida 1 shahar uchun harorat kiriting!", "error");
        return;
    }

    var days = [];
    for (var d = 0; d < 3; d++) {
        days.push({
            date: getDateForDay(d),
            day_index: d,
            cities: daysData[d],
            comment: daysComments[d] || ""
        });
    }

    var btn = document.getElementById("btnGenerate");
    btn.classList.add("loading");

    fetch("/api/generate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({days: days})
    })
    .then(function(r) { return r.json(); })
    .then(function(result) {
        btn.classList.remove("loading");
        if (result.success) {
            allDaysResult = days;
            showResultPanel(days, result);
            showToast("Prognoz muvaffaqiyatli shakllandi!", "success");
        } else {
            showToast("Xatolik: " + (result.error || "Noma\u2018lum"), "error");
        }
    })
    .catch(function(err) {
        btn.classList.remove("loading");
        allDaysResult = days;
        showResultPanel(days, {telegram: []});
        showToast("Server bilan bog\u2018lanishsiz \u2014 mahalliy rejim", "error");
    });
}


// === NATIJA PANELI ===
function showResultPanel(days, serverResult) {
    document.getElementById("inputPanel").classList.add("hidden");
    document.getElementById("resultPanel").classList.remove("hidden");
    resultCurrentDay = 0;
    updateResultDayTabs();
    renderResultForDay(0, days);

    var tgTexts = [];
    if (serverResult.telegram && serverResult.telegram.length) {
        tgTexts = serverResult.telegram;
    } else {
        for (var i = 0; i < 3; i++) {
            tgTexts.push(buildTelegramText(days[i], i));
        }
    }
    document.getElementById("telegramText").textContent = tgTexts.join("\n\n");
}

function renderResultForDay(dayIndex, days) {
    var day = days[dayIndex];
    if (!day) return;
    var cities = day.cities || {};

    colorizeMap(cities);

    var tbody = document.getElementById("resultTableBody");
    tbody.innerHTML = "";
    for (var city in cities) {
        var info = cities[city];
        if (!info || info.temp_max == null) continue;
        var tempStr = (info.temp_min != null ? info.temp_min + "\u00b0" : "") + "\u2013" + info.temp_max + "\u00b0C";
        var wEmoji = WEATHER_EMOJI[info.weather] || "";
        var wLabel = WEATHER_LABELS[info.weather] || "";
        var windStr = info.wind ? info.wind + " m/s" : "\u2014";
        var tr = document.createElement("tr");
        tr.innerHTML = '<td>' + city + '</td><td><b>' + tempStr + '</b></td><td>' + wEmoji + ' ' + wLabel + '</td><td>' + windStr + '</td>';
        tr.style.cursor = "pointer";
        tr.setAttribute("data-city", city);
        (function(c, ci) {
            tr.addEventListener("click", function() {
                showRegionDetail(c, ci);
                highlightMapRegion(c);
            });
        })(city, info);
        tbody.appendChild(tr);
    }

    renderAlerts(cities, day.comment);
    showOverview(cities);
}

// === NATIJA KUN TABLARI ===
function bindResultDayTabs() {
    var navBtns = document.querySelectorAll("#resultDayNav .day-btn");
    navBtns.forEach(function(btn) {
        btn.addEventListener("click", function() {
            navBtns.forEach(function(b) { b.classList.remove("active"); });
            btn.classList.add("active");
            resultCurrentDay = parseInt(btn.getAttribute("data-day"));
            if (allDaysResult) renderResultForDay(resultCurrentDay, allDaysResult);
        });
    });
}

function updateResultDayTabs() {
    var navBtns = document.querySelectorAll("#resultDayNav .day-btn");
    var labels = ["I kun", "II kun", "III kun"];
    navBtns.forEach(function(btn, i) {
        var dateStr = getDateForDay(i);
        if (dateStr) {
            var d = new Date(dateStr);
            btn.textContent = labels[i] + " \u2014 " + d.getDate() + " " + MONTHS_UZ[d.getMonth()];
        }
    });
}


// === XARITA RANGLASH ===
function colorizeMap(cities) {
    var paths = document.querySelectorAll(".reg-path");
    paths.forEach(function(path) {
        var cityName = path.getAttribute("data-city");
        var info = cities[cityName];
        if (info && info.temp_max != null) {
            path.style.fill = getTempColor(info.temp_max);
        } else {
            path.style.fill = "#cde4f6";
        }
        path.classList.remove("selected");
        path.onclick = function() {
            document.querySelectorAll(".reg-path").forEach(function(p) { p.classList.remove("selected"); });
            path.classList.add("selected");
            if (info && info.temp_max != null) showRegionDetail(cityName, info);
        };
    });
}

function highlightMapRegion(cityName) {
    document.querySelectorAll(".reg-path").forEach(function(p) {
        p.classList.remove("selected");
        if (p.getAttribute("data-city") === cityName) p.classList.add("selected");
    });
}

function getTempColor(t) {
    if (t >= 42) return "#c62828";
    if (t >= 40) return "#F7C1C1";
    if (t >= 37) return "#EF9F27";
    if (t >= 34) return "#FAC775";
    if (t >= 30) return "#FAC775";
    if (t >= 25) return "#85B7EB";
    if (t >= 18) return "#85B7EB";
    if (t >= 10) return "#B8D4E8";
    return "#D4E8F5";
}

// === VILOYAT TAFSILOTI ===
function showRegionDetail(cityName, info) {
    document.getElementById("regionTitle").textContent = cityName;
    document.getElementById("regionSub").textContent = getRegionName(cityName);
    var tempStr = (info.temp_min != null ? info.temp_min + "\u00b0" : "\u2014") + " \u2013 " + info.temp_max + "\u00b0C";
    document.getElementById("mTemp").textContent = tempStr;
    document.getElementById("mTempSub").textContent = getTempDescription(info.temp_max);
    document.getElementById("mWind").textContent = info.wind ? info.wind + " m/s" : "\u2014";
    document.getElementById("mWindSub").textContent = getWindDescription(info.wind);
    document.getElementById("mRain").textContent = info.precip ? info.precip + " mm" : "Yog\u2018insiz";
    document.getElementById("mRainSub").textContent = info.precip > 5 ? "Kuchli yog\u2018in" : info.precip > 0 ? "Yengil yog\u2018in" : "Quruq";
    var wEmoji = WEATHER_EMOJI[info.weather] || "";
    var wLabel = WEATHER_LABELS[info.weather] || "Noma\u2018lum";
    document.getElementById("mWeather").textContent = wEmoji + " " + wLabel;
    document.getElementById("mWeatherSub").textContent = "";
}

function showOverview(cities) {
    var temps = [], winds = [];
    for (var c in cities) {
        if (cities[c] && cities[c].temp_max != null) temps.push(cities[c].temp_max);
        if (cities[c] && cities[c].wind) winds.push(cities[c].wind);
    }
    if (temps.length === 0) return;
    var maxT = Math.max.apply(null, temps);
    var minT = Math.min.apply(null, temps);
    var maxW = winds.length ? Math.max.apply(null, winds) : 0;
    document.getElementById("regionTitle").textContent = "O\u2018zbekiston \u2014 umumiy ko\u2018rinish";
    document.getElementById("regionSub").textContent = "Viloyatni tanlang yoki jadvaldan bosing";
    document.getElementById("mTemp").textContent = minT + "\u00b0\u2013" + maxT + "\u00b0C";
    document.getElementById("mTempSub").textContent = "Barcha mintaqalar";
    document.getElementById("mWind").textContent = maxW ? "gacha " + maxW + " m/s" : "\u2014";
    document.getElementById("mWindSub").textContent = maxW >= 15 ? "Kuchli shamol!" : "";
    document.getElementById("mRain").textContent = "\u2014";
    document.getElementById("mRainSub").textContent = "";
    document.getElementById("mWeather").textContent = "\u2014";
    document.getElementById("mWeatherSub").textContent = "";
}


// === YORDAMCHI ===
var REGION_NAMES = {
    "Toshkent":"Toshkent shahri / viloyati",
    "Samarqand":"Samarqand viloyati",
    "Buxoro":"Buxoro viloyati",
    "Namangan":"Namangan viloyati",
    "Andijon":"Andijon viloyati",
    "Farg\u2018ona":"Farg\u2018ona viloyati",
    "Qarshi":"Qashqadaryo viloyati",
    "Nukus":"Qoraqalpog\u2018iston Respublikasi",
    "Navoiy":"Navoiy viloyati",
    "Termiz":"Surxondaryo viloyati",
    "Jizzax":"Jizzax viloyati",
    "Urganch":"Xorazm viloyati",
    "Guliston":"Sirdaryo viloyati"
};

function getRegionName(city) { return REGION_NAMES[city] || ""; }

function getTempDescription(t) {
    if (t >= 42) return "Haddan tashqari issiq!";
    if (t >= 38) return "Juda issiq";
    if (t >= 34) return "Issiq";
    if (t >= 28) return "Iliq";
    if (t >= 20) return "Mo\u2018tadil";
    if (t >= 10) return "Salqin";
    return "Sovuq";
}

function getWindDescription(w) {
    if (!w) return "";
    if (w >= 20) return "Juda kuchli shamol!";
    if (w >= 15) return "Kuchli shamol";
    if (w >= 10) return "O\u2018rtacha shamol";
    if (w >= 5) return "Yengil shamol";
    return "Deyarli shamolsiz";
}

// === OGOHLANTIRISHLAR ===
function renderAlerts(cities, comment) {
    var section = document.getElementById("alertsSection");
    section.innerHTML = "";
    var alerts = [];
    for (var city in cities) {
        var info = cities[city];
        if (!info || info.temp_max == null) continue;
        if (info.temp_max >= 40) {
            alerts.push({type:"a-red", title:"\ud83d\udd25 Issiqlik xavfi \u2014 " + city,
                body: city + " da harorat " + info.temp_max + "\u00b0C ga yetishi kutilmoqda."});
        }
        if (info.wind && info.wind >= 15) {
            alerts.push({type:"a-amber", title:"\ud83c\udf2a\ufe0f Kuchli shamol \u2014 " + city,
                body: city + " da shamol " + info.wind + " m/s gacha kuchayishi kutilmoqda."});
        }
        if (info.weather === "momaqaldiroq" || info.weather === "dol") {
            alerts.push({type:"a-blue", title:"\u26c8\ufe0f " + WEATHER_LABELS[info.weather] + " \u2014 " + city,
                body: city + " da " + WEATHER_LABELS[info.weather].toLowerCase() + " kutilmoqda."});
        }
        if (info.precip && info.precip >= 10) {
            alerts.push({type:"a-blue", title:"\ud83c\udf0a Kuchli yog\u2018in \u2014 " + city,
                body: city + " da " + info.precip + " mm yog\u2018ingarchilik kutilmoqda."});
        }
    }
    if (comment) {
        alerts.push({type:"a-amber", title:"\ud83d\udccb Sinoptik izohi", body: comment});
    }
    alerts.forEach(function(a) {
        var div = document.createElement("div");
        div.className = "alert " + a.type;
        div.innerHTML = '<div class="alert-title">' + a.title + '</div><div class="alert-body">' + a.body + '</div>';
        section.appendChild(div);
    });
}


// === TELEGRAM MATN ===
function buildTelegramText(dayData, dayIndex) {
    var labels = ["BUGUN", "ERTAGA", "INDINGA"];
    var dateStr = dayData.date || "";
    var header = formatDateUz(dateStr);
    var cities = dayData.cities || {};
    var lines = [];
    lines.push("\ud83c\udf24 OB-HAVO PROGNOZI \u2014 " + labels[dayIndex]);
    lines.push("\ud83d\udcc5 " + header);
    lines.push("\u2500".repeat(28));
    lines.push("");
    for (var city in cities) {
        var info = cities[city];
        if (!info || info.temp_max == null) continue;
        var emoji = WEATHER_EMOJI[info.weather] || "";
        var tmin = info.temp_min != null ? info.temp_min : "";
        var tmax = info.temp_max;
        var line = emoji + " " + city + ": " + tmin + "\u00b0\u2026" + tmax + "\u00b0C";
        if (info.wind) line += ", shamol " + info.wind + " m/s";
        if (info.precip && info.precip > 0) line += ", yog\u2018in " + info.precip + " mm";
        lines.push(line);
    }
    if (dayData.comment) { lines.push(""); lines.push("\ud83d\udccb " + dayData.comment); }
    lines.push("");
    lines.push("\u2500".repeat(28));
    lines.push("\ud83d\udce1 Gidrometeorologiya xizmati");
    lines.push("\ud83d\udd17 hydromet.uz");
    return lines.join("\n");
}

function copyTelegramAll() {
    var text = document.getElementById("telegramText").textContent;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() { showToast("\ud83d\udccb Telegram matni nusxalandi!", "success"); });
    } else {
        var ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
        showToast("\ud83d\udccb Nusxalandi!", "success");
    }
}

// === TOZALASH ===
function handleClear() {
    if (!confirm("Barcha ma\u2018lumotlarni tozalashni xohlaysizmi?")) return;
    daysData = [{}, {}, {}];
    daysComments = ["", "", ""];
    currentDay = 0;
    loadDayData(0);
    document.querySelectorAll("#dayNav .day-btn").forEach(function(btn, i) {
        btn.classList.toggle("active", i === 0);
    });
    showToast("Ma\u2018lumotlar tozalandi", "success");
}

// === OXIRGI YUKLASH ===
function handleLoadLast() {
    fetch("/api/latest")
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.error) { showToast("Arxivda ma\u2018lumot topilmadi", "error"); return; }
        if (data.days) {
            for (var i = 0; i < data.days.length && i < 3; i++) {
                daysData[i] = data.days[i].cities || {};
                daysComments[i] = data.days[i].comment || "";
            }
            loadDayData(currentDay);
            showToast("Oxirgi prognoz yuklandi!", "success");
        }
    })
    .catch(function() { showToast("Server bilan bog\u2018lanib bo\u2018lmadi", "error"); });
}

// === PNG EKSPORT ===
function handleExportPNG() {
    var svg = document.getElementById("uzmap");
    if (!svg) return;
    var svgData = new XMLSerializer().serializeToString(svg);
    var svgBlob = new Blob([svgData], {type: "image/svg+xml;charset=utf-8"});
    var url = URL.createObjectURL(svgBlob);
    var img = new Image();
    img.onload = function() {
        var canvas = document.createElement("canvas");
        canvas.width = 1200; canvas.height = 700;
        var ctx = canvas.getContext("2d");
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 50, 50, 1100, 600);
        ctx.fillStyle = "#0B3D8F";
        ctx.font = "bold 18px sans-serif";
        ctx.fillText("O\u2018zgidromet \u2014 Ob-havo prognozi", 50, 30);
        var link = document.createElement("a");
        link.download = "prognoz_xarita.png";
        link.href = canvas.toDataURL("image/png");
        link.click();
        URL.revokeObjectURL(url);
        showToast("PNG yuklandi!", "success");
    };
    img.src = url;
}

// === TOAST ===
function showToast(message, type) {
    var existing = document.querySelector(".toast");
    if (existing) existing.remove();
    var toast = document.createElement("div");
    toast.className = "toast " + (type || "");
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(function() { if (toast.parentNode) toast.remove(); }, 3000);
}

})();
