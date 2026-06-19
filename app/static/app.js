// ============================================
// GIDROMETEOROLOGIYA XIZMATI — PROGNOZ TIZIMI
// ============================================

const CITIES = [
    "Toshkent", "Samarqand", "Buxoro", "Namangan",
    "Andijon", "Farg'ona", "Qarshi", "Nukus",
    "Navoiy", "Termiz", "Jizzax", "Urganch",
    "Guliston", "Shahrisabz"
];

const WEATHER_TYPES = [
    { code: "ochiq",          label: "Havo ochiq" },
    { code: "qisman_bulutli", label: "Qisman bulutli" },
    { code: "bulutli",        label: "Bulutli" },
    { code: "tuman",          label: "Tuman" },
    { code: "yomgir",         label: "Yomg\u2018ir" },
    { code: "jala",           label: "Jala" },
    { code: "momaqaldiroq",   label: "Momaqaldiroq" },
    { code: "qor",            label: "Qor" },
    { code: "dol",            label: "Do\u2018l" },
    { code: "chang_boroni",   label: "Chang bo\u2018roni" },
    { code: "qor_boroni",     label: "Qor bo\u2018roni" }
];

const DAYS = ["yakshanba","dushanba","seshanba","chorshanba","payshanba","juma","shanba"];
const MONTHS = ["yanvar","fevral","mart","aprel","may","iyun","iyul","avgust","sentabr","oktabr","noyabr","dekabr"];

var forecastData = { days: [
    { date: null, comment: "", cities: {} },
    { date: null, comment: "", cities: {} },
    { date: null, comment: "", cities: {} }
]};
var currentDay = 0;

document.addEventListener("DOMContentLoaded", function() {
    initDates();
    buildTable();
    bindEvents();
});

function initDates() {
    var today = new Date();
    for (var i = 0; i < 3; i++) {
        var d = new Date(today);
        d.setDate(d.getDate() + i);
        forecastData.days[i].date = d;
    }
    document.getElementById("currentDate").textContent = formatDate(today);
    updateDayNav();
}

function formatDate(d) {
    return d.getDate() + " " + MONTHS[d.getMonth()] + " " + d.getFullYear() + ", " + DAYS[d.getDay()];
}

function updateDayNav() {
    var labels = ["I kun","II kun","III kun"];
    var btns = document.querySelectorAll("#inputSection .day-btn");
    btns.forEach(function(btn, i) {
        var d = forecastData.days[i].date;
        if (d) btn.textContent = labels[i] + " \u2014 " + d.getDate() + "." + String(d.getMonth()+1).padStart(2,"0");
    });
}


function buildTable() {
    var tbody = document.getElementById("tableBody");
    tbody.innerHTML = "";
    var cities = forecastData.days[currentDay].cities;

    CITIES.forEach(function(name) {
        var d = cities[name] || {};
        var row = document.createElement("tr");
        var opts = WEATHER_TYPES.map(function(w) {
            return '<option value="' + w.code + '"' + (d.weather === w.code ? ' selected' : '') + '>' + w.label + '</option>';
        }).join("");

        row.innerHTML =
            '<td>' + name + '</td>' +
            '<td><input type="number" data-city="' + name + '" data-field="temp_min" value="' + (d.temp_min != null ? d.temp_min : '') + '" step="1" min="-40" max="55"></td>' +
            '<td><input type="number" data-city="' + name + '" data-field="temp_max" value="' + (d.temp_max != null ? d.temp_max : '') + '" step="1" min="-40" max="55"></td>' +
            '<td><input type="number" data-city="' + name + '" data-field="wind" value="' + (d.wind != null ? d.wind : '') + '" step="1" min="0" max="50"></td>' +
            '<td><input type="number" data-city="' + name + '" data-field="precip" value="' + (d.precip != null ? d.precip : '') + '" step="0.1" min="0" max="200"></td>' +
            '<td><select data-city="' + name + '" data-field="weather">' + opts + '</select></td>';
        tbody.appendChild(row);
    });

    document.getElementById("comment").value = forecastData.days[currentDay].comment || "";
    tbody.querySelectorAll("input, select").forEach(function(el) {
        el.addEventListener("change", saveField);
        // Validatsiya — ogohlantirish ranglari
        el.addEventListener("input", function() {
            if (this.type === "number" && this.value !== "") {
                var v = parseFloat(this.value);
                var field = this.dataset.field;
                if (field === "temp_max" && v >= 45) this.style.background = "#ffcdd2";
                else if (field === "temp_max" && v >= 40) this.style.background = "#fff9c4";
                else if (field === "wind" && v >= 15) this.style.background = "#ffcdd2";
                else if (field === "wind" && v >= 10) this.style.background = "#fff9c4";
                else this.style.background = "";
            }
        });
    });
}

function saveField(e) {
    var city = e.target.dataset.city;
    var field = e.target.dataset.field;
    if (!forecastData.days[currentDay].cities[city])
        forecastData.days[currentDay].cities[city] = {};
    var val;
    if (e.target.type === "number") {
        val = e.target.value === "" ? null : parseFloat(e.target.value);
    } else {
        val = e.target.value;
    }
    forecastData.days[currentDay].cities[city][field] = val;
}

function saveComment() {
    forecastData.days[currentDay].comment = document.getElementById("comment").value;
}


function bindEvents() {
    document.querySelectorAll("#inputSection .day-btn").forEach(function(btn) {
        btn.addEventListener("click", function() {
            saveComment();
            currentDay = parseInt(this.dataset.day);
            document.querySelectorAll("#inputSection .day-btn").forEach(function(b, i) {
                b.classList.toggle("active", i === currentDay);
            });
            buildTable();
        });
    });

    document.getElementById("comment").addEventListener("input", function() {
        forecastData.days[currentDay].comment = this.value;
    });

    document.getElementById("btnGenerate").addEventListener("click", generate);
    document.getElementById("btnSample").addEventListener("click", loadSample);

    document.getElementById("btnCopyPrev").addEventListener("click", function() {
        if (currentDay === 0) { alert("I kun uchun oldingi kun mavjud emas."); return; }
        var prevCities = forecastData.days[currentDay - 1].cities;
        if (Object.keys(prevCities).length === 0) { alert("Oldingi kunda ma'lumot yo'q."); return; }
        forecastData.days[currentDay].cities = JSON.parse(JSON.stringify(prevCities));
        buildTable();
    });

    document.getElementById("btnClear").addEventListener("click", function() {
        if (!confirm("Barcha ma'lumotlar o'chirilsinmi?")) return;
        forecastData.days.forEach(function(d) { d.cities = {}; d.comment = ""; });
        buildTable();
    });

    document.getElementById("btnBack").addEventListener("click", function() {
        document.getElementById("inputSection").style.display = "";
        document.getElementById("resultSection").style.display = "none";
    });

    document.getElementById("btnCopy").addEventListener("click", function() {
        var text = document.getElementById("telegramText").textContent;
        navigator.clipboard.writeText(text).then(function() {
            document.getElementById("btnCopy").textContent = "Nusxa olindi!";
            setTimeout(function() { document.getElementById("btnCopy").textContent = "Nusxa olish"; }, 2000);
        });
    });

    document.getElementById("btnDownload").addEventListener("click", function() {
        exportMapToPNG(function(url) {
            if (url) { var a = document.createElement("a"); a.href = url; a.download = "prognoz.png"; a.click(); }
            else { alert("Xaritani PNG formatiga aylantirish imkoni bo'lmadi."); }
        });
    });

    document.getElementById("btnPdf").addEventListener("click", function() {
        var data = window._resultData;
        if (!data || !data.forecast_id) return;
        fetch("/api/export-pdf/" + data.forecast_id)
        .then(function(r) { return r.json(); })
        .then(function(res) {
            if (res.pdf_url) {
                var a = document.createElement("a");
                a.href = res.pdf_url; a.download = "prognoz.pdf"; a.click();
            }
        });
    });

    document.getElementById("btnTelegram").addEventListener("click", function() {
        var data = window._resultData;
        if (!data || !data.forecast_id) return;
        if (!confirm("Telegram kanalga yuborilsinmi?")) return;
        fetch("/api/publish-telegram/" + data.forecast_id, { method: "POST" })
        .then(function(r) { return r.json(); })
        .then(function(res) {
            if (res.status === "sent") alert("Telegram ga muvaffaqiyatli yuborildi!");
            else alert("Xatolik: " + JSON.stringify(res));
        });
    });

    document.querySelectorAll(".result-day-nav .day-btn").forEach(function(btn) {
        btn.addEventListener("click", function() {
            var day = parseInt(this.dataset.day);
            document.querySelectorAll(".result-day-nav .day-btn").forEach(function(b, i) {
                b.classList.toggle("active", i === day);
            });
            showDayResult(day);
        });
    });
}


function generate() {
    saveComment();
    var hasData = false;
    for (var i = 0; i < forecastData.days.length; i++) {
        var cities = forecastData.days[i].cities;
        for (var c in cities) {
            if (cities[c] && cities[c].temp_max != null) { hasData = true; break; }
        }
        if (hasData) break;
    }
    if (!hasData) {
        alert("Kamida bitta shahar uchun harorat kiriting.\n\nYoki \"Namuna yuklash\" tugmasini bosing.");
        return;
    }

    var payload = forecastData.days.map(function(d, i) {
        return {
            date: d.date ? d.date.toISOString().slice(0, 10) : null,
            day_index: i,
            comment: d.comment,
            cities: d.cities
        };
    });

    document.getElementById("btnGenerate").textContent = "Yaratilmoqda...";
    document.getElementById("btnGenerate").disabled = true;

    fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ days: payload })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) {
            document.getElementById("inputSection").style.display = "none";
            document.getElementById("resultSection").style.display = "";
            window._resultData = data;
            showDayResult(0);
        } else {
            alert("Xatolik: " + (data.error || "Noma'lum xato"));
        }
    })
    .catch(function(err) {
        alert("Server bilan aloqa xatosi: " + err.message);
    })
    .finally(function() {
        document.getElementById("btnGenerate").textContent = "Xarita va prognozni shakllantirish";
        document.getElementById("btnGenerate").disabled = false;
    });
}

function showDayResult(dayIndex) {
    var data = window._resultData;
    if (!data) return;
    initForecastMap("forecastMapContainer");
    var dayPayload = data.days ? data.days[dayIndex] : null;
    var cities = dayPayload ? dayPayload.cities : (forecastData.days[dayIndex] ? forecastData.days[dayIndex].cities : {});
    renderCityMarkers(cities);
    document.getElementById("telegramText").textContent = data.telegram[dayIndex];
}


function loadSample() {
    var s = [
        { comment: "Respublika hududida harorat mavsumiy me'yordan 3\u20135\u00b0C yuqori saqlanadi. Farg'ona vodiysida mahalliy momaqaldiroqli yog'ingarchilik ehtimoli bor.",
          cities: { "Toshkent":{temp_min:22,temp_max:36,wind:4,precip:0,weather:"ochiq"}, "Samarqand":{temp_min:18,temp_max:33,wind:3,precip:0,weather:"qisman_bulutli"}, "Buxoro":{temp_min:24,temp_max:40,wind:5,precip:0,weather:"ochiq"}, "Namangan":{temp_min:20,temp_max:35,wind:3,precip:0,weather:"qisman_bulutli"}, "Andijon":{temp_min:21,temp_max:34,wind:3,precip:2,weather:"jala"}, "Farg'ona":{temp_min:22,temp_max:38,wind:2,precip:0,weather:"ochiq"}, "Qarshi":{temp_min:23,temp_max:41,wind:4,precip:0,weather:"ochiq"}, "Nukus":{temp_min:20,temp_max:38,wind:6,precip:0,weather:"qisman_bulutli"}, "Navoiy":{temp_min:21,temp_max:39,wind:5,precip:0,weather:"ochiq"}, "Termiz":{temp_min:26,temp_max:44,wind:3,precip:0,weather:"ochiq"}, "Jizzax":{temp_min:20,temp_max:36,wind:4,precip:0,weather:"bulutli"}, "Urganch":{temp_min:21,temp_max:37,wind:5,precip:0,weather:"qisman_bulutli"}, "Guliston":{temp_min:21,temp_max:35,wind:3,precip:0,weather:"qisman_bulutli"}, "Shahrisabz":{temp_min:19,temp_max:34,wind:2,precip:0,weather:"bulutli"} } },
        { comment: "Shimoliy-sharqiy hududlarda momaqaldiroqli yog'ingarchilik. Xorazm, Qoraqalpog'istonda shamol 15\u201318 m/s gacha kuchayadi.",
          cities: { "Toshkent":{temp_min:21,temp_max:34,wind:5,precip:3,weather:"yomgir"}, "Samarqand":{temp_min:17,temp_max:31,wind:4,precip:5,weather:"yomgir"}, "Buxoro":{temp_min:23,temp_max:38,wind:6,precip:0,weather:"bulutli"}, "Namangan":{temp_min:19,temp_max:33,wind:5,precip:8,weather:"momaqaldiroq"}, "Andijon":{temp_min:20,temp_max:32,wind:4,precip:10,weather:"momaqaldiroq"}, "Farg'ona":{temp_min:21,temp_max:35,wind:3,precip:5,weather:"yomgir"}, "Qarshi":{temp_min:22,temp_max:39,wind:5,precip:0,weather:"qisman_bulutli"}, "Nukus":{temp_min:19,temp_max:36,wind:8,precip:0,weather:"chang_boroni"}, "Navoiy":{temp_min:20,temp_max:37,wind:6,precip:0,weather:"bulutli"}, "Termiz":{temp_min:25,temp_max:42,wind:4,precip:0,weather:"ochiq"}, "Jizzax":{temp_min:19,temp_max:34,wind:4,precip:2,weather:"jala"}, "Urganch":{temp_min:20,temp_max:35,wind:7,precip:0,weather:"chang_boroni"}, "Guliston":{temp_min:20,temp_max:33,wind:4,precip:1,weather:"jala"}, "Shahrisabz":{temp_min:18,temp_max:32,wind:3,precip:4,weather:"yomgir"} } },
        { comment: "Ob-havo barqarorlashadi. Yog'ingarchilik kutilmaydi.",
          cities: { "Toshkent":{temp_min:20,temp_max:32,wind:3,precip:0,weather:"qisman_bulutli"}, "Samarqand":{temp_min:16,temp_max:30,wind:2,precip:0,weather:"qisman_bulutli"}, "Buxoro":{temp_min:22,temp_max:37,wind:4,precip:0,weather:"qisman_bulutli"}, "Namangan":{temp_min:18,temp_max:31,wind:3,precip:0,weather:"bulutli"}, "Andijon":{temp_min:19,temp_max:30,wind:2,precip:0,weather:"bulutli"}, "Farg'ona":{temp_min:20,temp_max:33,wind:2,precip:0,weather:"qisman_bulutli"}, "Qarshi":{temp_min:21,temp_max:38,wind:3,precip:0,weather:"ochiq"}, "Nukus":{temp_min:18,temp_max:35,wind:5,precip:0,weather:"qisman_bulutli"}, "Navoiy":{temp_min:19,temp_max:36,wind:4,precip:0,weather:"qisman_bulutli"}, "Termiz":{temp_min:24,temp_max:41,wind:3,precip:0,weather:"ochiq"}, "Jizzax":{temp_min:18,temp_max:33,wind:3,precip:0,weather:"qisman_bulutli"}, "Urganch":{temp_min:19,temp_max:34,wind:4,precip:0,weather:"bulutli"}, "Guliston":{temp_min:19,temp_max:32,wind:3,precip:0,weather:"qisman_bulutli"}, "Shahrisabz":{temp_min:17,temp_max:31,wind:2,precip:0,weather:"qisman_bulutli"} } }
    ];
    for (var i = 0; i < 3; i++) {
        forecastData.days[i].cities = s[i].cities;
        forecastData.days[i].comment = s[i].comment;
    }
    buildTable();
}



