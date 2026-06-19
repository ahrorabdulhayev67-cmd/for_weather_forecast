// Leaflet xarita moduli — statik, viloyatlar ranglangan
var forecastMap = null;
var geoLayer = null;
var markersLayer = null;
var currentCitiesData = null;
var GEO_URL = "https://raw.githubusercontent.com/akbartus/GeoJSON-Uzbekistan/main/Uzbekistan_regions.json";

var WEATHER_ICONS_MAP = {
    "ochiq": "\u2600\ufe0f", "qisman_bulutli": "\u26c5",
    "bulutli": "\u2601\ufe0f", "tuman": "\ud83c\udf2b\ufe0f",
    "yomgir": "\ud83c\udf27\ufe0f", "jala": "\ud83c\udf26\ufe0f",
    "momaqaldiroq": "\u26c8\ufe0f", "qor": "\u2744\ufe0f",
    "dol": "\ud83c\udf28\ufe0f", "chang_boroni": "\ud83d\udca8",
    "qor_boroni": "\ud83c\udf2c\ufe0f"
};

// Viloyat nomi -> shahar nomi
var REGION_TO_CITY = {
    "Toshkent":"Toshkent","Tashkent":"Toshkent",
    "Samarqand":"Samarqand","Samarkand":"Samarqand",
    "Buxoro":"Buxoro","Bukhara":"Buxoro","Bukhoro":"Buxoro",
    "Namangan":"Namangan",
    "Andijon":"Andijon","Andijan":"Andijon",
    "Farg\u2018ona":"Farg\u2018ona","Fergana":"Farg\u2018ona","Fargona":"Farg\u2018ona",
    "Qashqadaryo":"Qarshi","Kashkadarya":"Qarshi",
    "Qoraqalpog\u2018iston":"Nukus","Karakalpakstan":"Nukus",
    "Navoiy":"Navoiy","Navoi":"Navoiy",
    "Surxondaryo":"Termiz","Surkhandarya":"Termiz",
    "Jizzax":"Jizzax","Jizzakh":"Jizzax",
    "Xorazm":"Urganch","Khorezm":"Urganch",
    "Sirdaryo":"Guliston","Syrdarya":"Guliston"
};

function initForecastMap(containerId) {
    if (forecastMap) { forecastMap.remove(); forecastMap = null; }
    forecastMap = L.map(containerId, {
        center: [41.0, 64.5], zoom: 6,
        zoomControl: false, attributionControl: false,
        preferCanvas: true, dragging: false, touchZoom: false,
        doubleClickZoom: false, scrollWheelZoom: false,
        boxZoom: false, keyboard: false
    });
    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager_nolabels/{z}/{x}/{y}{r}.png", {
        maxZoom: 12, subdomains: "abcd"
    }).addTo(forecastMap);
    markersLayer = L.layerGroup().addTo(forecastMap);
    loadGeoJSON();
}

function loadGeoJSON() {
    fetch(GEO_URL).then(function(r){return r.json();}).then(function(data){
        geoLayer = L.geoJSON(data, {
            style: function(feature){ return getRegionStyle(feature); },
            onEachFeature: function(feature, layer){
                var name = feature.properties.name || feature.properties.NAME_1 || "";
                if(name) layer.bindTooltip(name, {sticky:true});
            }
        }).addTo(forecastMap);
        forecastMap.fitBounds(geoLayer.getBounds(), {padding:[10,10]});
    }).catch(function(err){console.warn("GeoJSON yuklanmadi:",err);});
}

function getRegionStyle(feature) {
    var regionName = feature.properties.name || feature.properties.NAME_1 || "";
    var city = findCityForRegion(regionName);
    var fillClr = "#ecf0f1", fillOp = 0.2;
    if(city && currentCitiesData && currentCitiesData[city]) {
        var tmax = currentCitiesData[city].temp_max;
        if(tmax != null) { fillClr = getTempFillColor(tmax); fillOp = 0.55; }
    }
    return {color:"#2c3e50", weight:1.5, opacity:0.8, fillColor:fillClr, fillOpacity:fillOp};
}

function findCityForRegion(regionName) {
    if(REGION_TO_CITY[regionName]) return REGION_TO_CITY[regionName];
    for(var key in REGION_TO_CITY){
        if(regionName.toLowerCase().indexOf(key.toLowerCase())>=0) return REGION_TO_CITY[key];
    }
    return null;
}

function getTempFillColor(t) {
    if(t>=44)return"#4a0000";if(t>=42)return"#7f0000";if(t>=40)return"#b71c1c";
    if(t>=38)return"#d32f2f";if(t>=36)return"#e53935";if(t>=34)return"#ef5350";
    if(t>=32)return"#ef6c00";if(t>=30)return"#f57c00";if(t>=28)return"#ff9800";
    if(t>=26)return"#ffc107";if(t>=24)return"#ffeb3b";if(t>=22)return"#cddc39";
    if(t>=20)return"#8bc34a";if(t>=18)return"#66bb6a";if(t>=15)return"#4dd0e1";
    if(t>=10)return"#4fc3f7";if(t>=5)return"#42a5f5";if(t>=0)return"#90caf9";
    return"#e3f2fd";
}

function getTempColorHex(t) {
    if(t>=42)return"#880e4f";if(t>=38)return"#c62828";if(t>=34)return"#e65100";
    if(t>=30)return"#ef6c00";if(t>=26)return"#f57f17";if(t>=22)return"#689f38";
    if(t>=18)return"#2e7d32";if(t>=12)return"#00838f";if(t>=5)return"#1565c0";
    if(t>=0)return"#1a237e";return"#311b92";
}

function renderCityMarkers(citiesData) {
    if(!forecastMap||!markersLayer) return;
    markersLayer.clearLayers();
    currentCitiesData = citiesData;
    if(geoLayer) geoLayer.setStyle(function(f){return getRegionStyle(f);});

    var COORDS = {
        "Toshkent":[41.30,69.24],"Samarqand":[39.65,66.96],
        "Buxoro":[39.77,64.43],"Namangan":[41.00,71.67],
        "Andijon":[40.78,72.34],"Farg\u2018ona":[40.38,71.79],
        "Qarshi":[38.86,65.80],"Nukus":[42.46,59.60],
        "Navoiy":[40.10,65.38],"Termiz":[37.22,67.28],
        "Jizzax":[40.12,67.84],"Urganch":[41.55,60.63],
        "Guliston":[40.49,68.78],"Shahrisabz":[39.06,66.83]
    };
    for(var city in citiesData){
        var info=citiesData[city];
        if(!info||info.temp_max==null)continue;
        var coords=COORDS[city]; if(!coords)continue;
        var tmax=info.temp_max, tmin=info.temp_min;
        var weather=info.weather||"ochiq";
        var wIcon=WEATHER_ICONS_MAP[weather]||"\u2022";
        var clr=getTempColorHex(tmax);
        var tempStr=tmin!=null?(tmin+"\u00b0\u2013"+tmax+"\u00b0"):(tmax+"\u00b0");
        var html='<div class="forecast-marker"><div class="fm-icon" style="background:'+clr+'">'+wIcon+'</div><div class="fm-info"><span class="fm-city">'+city+'</span><span class="fm-temp" style="color:'+clr+'">'+tempStr+'</span></div></div>';
        var icon=L.divIcon({className:"forecast-marker-container",html:html,iconSize:[130,44],iconAnchor:[65,44]});
        var marker=L.marker(coords,{icon:icon});
        markersLayer.addLayer(marker);
    }
}

function exportMapToPNG(callback) {
    var el=document.getElementById("forecastMapContainer");
    if(!el||typeof domtoimage==="undefined"){callback(null);return;}
    setTimeout(function(){
        domtoimage.toPng(el,{width:el.offsetWidth,height:el.offsetHeight})
        .then(function(url){callback(url);})
        .catch(function(){callback(null);});
    },800);
}
