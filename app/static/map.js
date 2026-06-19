// Leaflet xarita moduli
var forecastMap = null;
var geoLayer = null;
var markersLayer = null;
var GEO_URL = "https://raw.githubusercontent.com/akbartus/GeoJSON-Uzbekistan/main/Uzbekistan_regions.json";

var WEATHER_ICONS_MAP = {
    "ochiq": "\u2600\ufe0f", "qisman_bulutli": "\u26c5",
    "bulutli": "\u2601\ufe0f", "tuman": "\ud83c\udf2b\ufe0f",
    "yomgir": "\ud83c\udf27\ufe0f", "jala": "\ud83c\udf26\ufe0f",
    "momaqaldiroq": "\u26c8\ufe0f", "qor": "\u2744\ufe0f",
    "dol": "\ud83c\udf28\ufe0f", "chang_boroni": "\ud83d\udca8",
    "qor_boroni": "\ud83c\udf2c\ufe0f"
};

function initForecastMap(containerId) {
    if (forecastMap) { forecastMap.remove(); forecastMap = null; }
    forecastMap = L.map(containerId, {
        center: [41.0, 64.5], zoom: 6,
        zoomControl: false,
        attributionControl: false,
        preferCanvas: true,
        dragging: false,
        touchZoom: false,
        doubleClickZoom: false,
        scrollWheelZoom: false,
        boxZoom: false,
        keyboard: false
    });
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
        maxZoom: 12, subdomains: "abcd"
    }).addTo(forecastMap);
    markersLayer = L.layerGroup().addTo(forecastMap);
    loadGeoJSON();
}

function loadGeoJSON() {
    fetch(GEO_URL).then(function(r) { return r.json(); }).then(function(data) {
        geoLayer = L.geoJSON(data, {
            style: { color: "#2c3e50", weight: 1.8, opacity: 0.9, fillColor: "#ecf0f1", fillOpacity: 0.12 },
            onEachFeature: function(feature, layer) {
                var name = feature.properties.name || feature.properties.NAME_1 || "";
                if (name) layer.bindTooltip(name, { sticky: true });
            }
        }).addTo(forecastMap);
        forecastMap.fitBounds(geoLayer.getBounds(), { padding: [20, 20] });
    }).catch(function(err) { console.warn("GeoJSON yuklanmadi:", err); });
}

function getTempColorHex(t) {
    if (t >= 42) return "#880e4f";
    if (t >= 38) return "#c62828";
    if (t >= 34) return "#e65100";
    if (t >= 30) return "#ef6c00";
    if (t >= 26) return "#f9a825";
    if (t >= 22) return "#689f38";
    if (t >= 18) return "#2e7d32";
    if (t >= 12) return "#00838f";
    if (t >= 5) return "#1565c0";
    if (t >= 0) return "#1a237e";
    return "#311b92";
}

function renderCityMarkers(citiesData) {
    if (!forecastMap || !markersLayer) return;
    markersLayer.clearLayers();
    var COORDS = {
        "Toshkent": [41.30, 69.24], "Samarqand": [39.65, 66.96],
        "Buxoro": [39.77, 64.43], "Namangan": [41.00, 71.67],
        "Andijon": [40.78, 72.34], "Farg\u2018ona": [40.38, 71.79],
        "Qarshi": [38.86, 65.80], "Nukus": [42.46, 59.60],
        "Navoiy": [40.10, 65.38], "Termiz": [37.22, 67.28],
        "Jizzax": [40.12, 67.84], "Urganch": [41.55, 60.63],
        "Guliston": [40.49, 68.78], "Shahrisabz": [39.06, 66.83]
    };
    for (var city in citiesData) {
        var info = citiesData[city];
        if (!info || info.temp_max == null) continue;
        var coords = COORDS[city];
        if (!coords) continue;
        var tmax = info.temp_max;
        var tmin = info.temp_min;
        var weather = info.weather || "ochiq";
        var wIcon = WEATHER_ICONS_MAP[weather] || "\u2022";
        var clr = getTempColorHex(tmax);
        var tempStr = tmin != null ? (tmin + "\u00b0\u2013" + tmax + "\u00b0") : (tmax + "\u00b0");
        var html = '<div class="forecast-marker"><div class="fm-icon" style="background:' + clr + '">' + wIcon + '</div><div class="fm-info"><span class="fm-city">' + city + '</span><span class="fm-temp" style="color:' + clr + '">' + tempStr + '</span></div></div>';
        var icon = L.divIcon({ className: "forecast-marker-container", html: html, iconSize: [130, 44], iconAnchor: [65, 44] });
        var marker = L.marker(coords, { icon: icon });
        var wind = info.wind || 0;
        var precip = info.precip || 0;
        var popupHtml = '<div class="fm-popup"><h4>' + wIcon + ' ' + city + '</h4><p>Harorat: ' + tempStr + 'C</p><p>Shamol: ' + wind + ' m/s</p><p>Yog\u2018ingarchilik: ' + precip + ' mm</p></div>';
        marker.bindPopup(popupHtml);
        markersLayer.addLayer(marker);
    }
}

function exportMapToPNG(callback) {
    var el = document.getElementById("forecastMapContainer");
    if (!el || typeof domtoimage === "undefined") { callback(null); return; }
    setTimeout(function() {
        domtoimage.toPng(el, { width: el.offsetWidth, height: el.offsetHeight })
        .then(function(url) { callback(url); })
        .catch(function() { callback(null); });
    }, 600);
}
