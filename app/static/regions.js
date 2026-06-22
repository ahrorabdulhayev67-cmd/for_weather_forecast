/**
 * O'zbekiston viloyatlari SVG polygon ma'lumotlari
 * Koordinatalar: lon/lat -> SVG viewport (1200x800)
 * 
 * Haqiqiy geografik koordinatalar asosida soddalashtirilgan polygonlar
 * Lon range: 56.0 - 73.5 (width=17.5)
 * Lat range: 37.0 - 45.8 (height=8.8)
 */

// Geo koordinatalarni SVG koordinatalarga o'girish
const MAP_BOUNDS = {
    minLon: 55.5,
    maxLon: 73.8,
    minLat: 36.8,
    maxLat: 46.0,
    width: 1200,
    height: 750
};

function geoToSvg(lon, lat) {
    const x = ((lon - MAP_BOUNDS.minLon) / (MAP_BOUNDS.maxLon - MAP_BOUNDS.minLon)) * MAP_BOUNDS.width;
    const y = MAP_BOUNDS.height - ((lat - MAP_BOUNDS.minLat) / (MAP_BOUNDS.maxLat - MAP_BOUNDS.minLat)) * MAP_BOUNDS.height;
    return [Math.round(x * 10) / 10, Math.round(y * 10) / 10];
}

function polygonToPath(coords) {
    return coords.map((c, i) => {
        const [x, y] = geoToSvg(c[0], c[1]);
        return (i === 0 ? 'M' : 'L') + x + ',' + y;
    }).join(' ') + ' Z';
}

// Viloyatlar polygonlari (soddalashtirilgan chegaralar)
const REGIONS = {
    "Qoraqalpogiston": {
        name: "Qoraqalpog'iston",
        capital: "Nukus",
        capitalCoords: [59.60, 42.46],
        polygon: [
            [56.0, 43.8], [56.0, 45.0], [57.5, 45.5], [59.0, 45.5],
            [60.5, 45.0], [61.5, 44.5], [62.0, 44.0], [62.5, 43.5],
            [62.5, 43.0], [62.0, 42.5], [61.8, 42.0], [61.5, 41.5],
            [61.0, 41.2], [60.5, 41.0], [60.0, 40.8], [59.5, 41.0],
            [59.0, 41.2], [58.5, 41.5], [58.0, 41.8], [57.5, 42.0],
            [57.0, 42.5], [56.5, 43.0], [56.0, 43.5]
        ]
    },
    "Xorazm": {
        name: "Xorazm",
        capital: "Urganch",
        capitalCoords: [60.63, 41.55],
        polygon: [
            [60.0, 40.8], [60.5, 41.0], [61.0, 41.2], [61.5, 41.5],
            [61.8, 42.0], [62.0, 42.5], [61.5, 42.3], [61.0, 42.0],
            [60.5, 41.8], [60.0, 41.5], [59.5, 41.3], [59.5, 41.0],
            [60.0, 40.8]
        ]
    },
    "Buxoro": {
        name: "Buxoro",
        capital: "Buxoro",
        capitalCoords: [64.43, 39.77],
        polygon: [
            [62.0, 42.5], [62.5, 43.0], [62.5, 43.5], [63.0, 43.5],
            [63.5, 43.0], [64.0, 42.5], [64.5, 42.0], [65.0, 41.5],
            [65.5, 41.0], [65.5, 40.5], [65.5, 40.0], [65.0, 39.5],
            [64.5, 39.0], [64.0, 38.8], [63.5, 39.0], [63.0, 39.5],
            [62.5, 40.0], [62.0, 40.5], [61.5, 41.0], [61.5, 41.5],
            [61.8, 42.0], [62.0, 42.5]
        ]
    },
    "Navoiy": {
        name: "Navoiy",
        capital: "Navoiy",
        capitalCoords: [65.38, 40.10],
        polygon: [
            [63.0, 43.5], [63.5, 43.0], [64.0, 42.5], [64.5, 42.0],
            [65.0, 41.5], [65.5, 41.0], [66.0, 41.0], [66.5, 41.2],
            [67.0, 41.5], [67.5, 41.8], [67.5, 42.0], [67.0, 42.5],
            [66.5, 43.0], [66.0, 43.5], [65.5, 43.8], [65.0, 44.0],
            [64.5, 43.8], [64.0, 43.5], [63.5, 43.5], [63.0, 43.5]
        ]
    },
    "Samarqand": {
        name: "Samarqand",
        capital: "Samarqand",
        capitalCoords: [66.96, 39.65],
        polygon: [
            [65.5, 41.0], [66.0, 41.0], [66.5, 41.0], [67.0, 40.8],
            [67.2, 40.5], [67.0, 40.0], [66.8, 39.5], [66.5, 39.2],
            [66.0, 39.0], [65.5, 39.0], [65.0, 39.2], [65.0, 39.5],
            [65.2, 40.0], [65.5, 40.5], [65.5, 41.0]
        ]
    },
    "Qashqadaryo": {
        name: "Qashqadaryo",
        capital: "Qarshi",
        capitalCoords: [65.80, 38.86],
        polygon: [
            [65.0, 39.5], [65.0, 39.2], [65.5, 39.0], [66.0, 39.0],
            [66.5, 39.2], [67.0, 39.0], [67.5, 38.8], [67.5, 38.3],
            [67.0, 38.0], [66.5, 37.8], [66.0, 37.8], [65.5, 38.0],
            [65.0, 38.3], [64.5, 38.5], [64.0, 38.8], [64.5, 39.0],
            [65.0, 39.5]
        ]
    },
    "Surxondaryo": {
        name: "Surxondaryo",
        capital: "Termiz",
        capitalCoords: [67.28, 37.22],
        polygon: [
            [67.0, 39.0], [67.5, 38.8], [67.5, 38.3], [67.8, 38.0],
            [68.0, 37.8], [68.2, 37.5], [68.0, 37.2], [67.5, 37.0],
            [67.0, 37.0], [66.5, 37.2], [66.5, 37.5], [66.5, 37.8],
            [67.0, 38.0], [67.0, 38.5], [67.0, 39.0]
        ]
    },
    "Jizzax": {
        name: "Jizzax",
        capital: "Jizzax",
        capitalCoords: [67.84, 40.12],
        polygon: [
            [66.5, 41.0], [67.0, 41.2], [67.5, 41.5], [68.0, 41.2],
            [68.5, 41.0], [68.5, 40.5], [68.2, 40.2], [68.0, 40.0],
            [67.5, 39.8], [67.2, 40.0], [67.0, 40.5], [67.0, 40.8],
            [66.5, 41.0]
        ]
    },
    "Sirdaryo": {
        name: "Sirdaryo",
        capital: "Guliston",
        capitalCoords: [68.78, 40.49],
        polygon: [
            [68.0, 41.2], [68.5, 41.0], [69.0, 41.0], [69.5, 40.8],
            [69.5, 40.5], [69.2, 40.2], [68.8, 40.0], [68.5, 40.2],
            [68.2, 40.5], [68.0, 40.8], [68.0, 41.2]
        ]
    },
    "Toshkent_v": {
        name: "Toshkent vil.",
        capital: "Toshkent",
        capitalCoords: [69.24, 41.30],
        polygon: [
            [68.5, 41.0], [69.0, 41.0], [69.5, 41.2], [70.0, 41.5],
            [70.5, 41.8], [71.0, 41.5], [71.0, 41.0], [70.5, 40.8],
            [70.0, 40.5], [69.5, 40.5], [69.5, 40.8], [69.0, 41.0],
            [68.5, 41.0]
        ]
    },
    "Namangan": {
        name: "Namangan",
        capital: "Namangan",
        capitalCoords: [71.67, 41.00],
        polygon: [
            [70.5, 41.8], [71.0, 41.5], [71.5, 41.5], [72.0, 41.2],
            [72.0, 40.8], [71.5, 40.5], [71.0, 40.5], [71.0, 41.0],
            [70.5, 41.2], [70.5, 41.8]
        ]
    },
    "Andijon": {
        name: "Andijon",
        capital: "Andijon",
        capitalCoords: [72.34, 40.78],
        polygon: [
            [72.0, 41.2], [72.5, 41.0], [73.0, 40.8], [73.2, 40.5],
            [73.0, 40.2], [72.5, 40.2], [72.0, 40.5], [72.0, 40.8],
            [72.0, 41.2]
        ]
    },
    "Fargona": {
        name: "Farg'ona",
        capital: "Farg'ona",
        capitalCoords: [71.79, 40.38],
        polygon: [
            [70.0, 40.5], [70.5, 40.8], [71.0, 40.5], [71.5, 40.5],
            [72.0, 40.5], [72.5, 40.2], [73.0, 40.2], [73.0, 39.8],
            [72.5, 39.5], [72.0, 39.5], [71.5, 39.8], [71.0, 40.0],
            [70.5, 40.2], [70.0, 40.5]
        ]
    }
};

// Shaharlar (viloyat markazlari) koordinatalari
const CITIES = {
    "Toshkent": { lon: 69.24, lat: 41.30, region: "Toshkent_v" },
    "Samarqand": { lon: 66.96, lat: 39.65, region: "Samarqand" },
    "Buxoro": { lon: 64.43, lat: 39.77, region: "Buxoro" },
    "Namangan": { lon: 71.67, lat: 41.00, region: "Namangan" },
    "Andijon": { lon: 72.34, lat: 40.78, region: "Andijon" },
    "Farg'ona": { lon: 71.79, lat: 40.38, region: "Fargona" },
    "Qarshi": { lon: 65.80, lat: 38.86, region: "Qashqadaryo" },
    "Nukus": { lon: 59.60, lat: 42.46, region: "Qoraqalpogiston" },
    "Navoiy": { lon: 65.38, lat: 40.10, region: "Navoiy" },
    "Termiz": { lon: 67.28, lat: 37.22, region: "Surxondaryo" },
    "Jizzax": { lon: 67.84, lat: 40.12, region: "Jizzax" },
    "Urganch": { lon: 60.63, lat: 41.55, region: "Xorazm" },
    "Guliston": { lon: 68.78, lat: 40.49, region: "Sirdaryo" }
};
