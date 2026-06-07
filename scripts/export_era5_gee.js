// GEE Code Editor script: Export ERA5-Land 16-day composites for Nature project
// Paste into https://code.earthengine.google.com/
// Run once per year (change YEAR), or loop 2000-2025
//
// Matches MODIS MOD13Q1 16-day composite schedule:
//   23 windows per year: DoY 1, 17, 33, ..., 353
//   Each window = 16 days (last window 13-14 days depending on leap year)
//
// Output: GeoTIFF with bands T_001, D_001, ... (7 vars x 23 windows = 161 bands)
// Resolution: 0.25° (EPSG:4326, scale: 27780), matching MODIS grid
// Drive folder: Nature_ERA5_Export

var YEAR = 2000;  // Change for each year: 2000-2025
var DRIVE_FOLDER = "Nature_ERA5_Export";

// Shared grid used by MODIS and ERA5 exports.
// Keep these constants identical to scripts/export_modis_gee.js.
// The current working domain is the Australia-focused GEE export footprint.
// For a Nature-global analysis, expand EXPORT_REGION first, then re-export both datasets.
var SHARED_CRS = "EPSG:4326";
var SHARED_TRANSFORM = [0.25, 0, 109.75, 0, -0.25, -10.00];
var EXPORT_REGION = ee.Geometry.Rectangle([109.75, -40.25, 150.25, -10.00], null, false);

// ── 16-day composite windows (same as MOD13Q1) ────────────
var WINDOW_DOYS = [1, 17, 33, 49, 65, 81, 97, 113, 129, 145, 161, 177,
                   193, 209, 225, 241, 257, 273, 289, 305, 321, 337, 353];
var WINDOW_DAYS = 16;

// Load ERA5-Land hourly data for the year (plus Jan 1 of next year for last window)
var startDate = YEAR + "-01-01";
var endDate = (YEAR + 1) + "-01-02";  // +1 day buffer for last window

var hourly = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY")
  .filterDate(startDate, endDate);

// Compute composite for a single 16-day window
function compositeForWindow(startDoy) {
  startDoy = ee.Number(startDoy);
  var windowStart = ee.Date.fromYMD(YEAR, 1, 1).advance(startDoy.subtract(1), "day");
  var windowEnd = windowStart.advance(WINDOW_DAYS, "day");
  var windowImgs = hourly.filterDate(windowStart, windowEnd);
  
  // Mean for instantaneous variables
  var meanVars = windowImgs
    .select(["temperature_2m", "dewpoint_temperature_2m",
             "volumetric_soil_water_layer_1", "volumetric_soil_water_layer_2"])
    .mean();
  
  // Sum for accumulated variables
  var sumVars = windowImgs
    .select(["total_precipitation", "surface_solar_radiation_downwards"])
    .sum();
  
  // Compute VPD (kPa) from mean T and Td
  var tc = meanVars.select("temperature_2m").subtract(273.15);
  var td = meanVars.select("dewpoint_temperature_2m").subtract(273.15);
  var es = tc.multiply(17.27).divide(tc.add(237.3)).exp().multiply(0.6108);
  var ea = td.multiply(17.27).divide(td.add(237.3)).exp().multiply(0.6108);
  var vpd = es.subtract(ea).max(0).rename("vapour_pressure_deficit");
  
  // Band suffix = 3-digit DoY of window start
  var suffix = ee.String(ee.Number(startDoy).format("%03d"));
  
  var tB  = meanVars.select("temperature_2m").rename(ee.String("T_").cat(suffix));
  var dB  = meanVars.select("dewpoint_temperature_2m").rename(ee.String("D_").cat(suffix));
  var s1B = meanVars.select("volumetric_soil_water_layer_1").rename(ee.String("S_").cat(suffix));
  var s2B = meanVars.select("volumetric_soil_water_layer_2").rename(ee.String("U_").cat(suffix));
  var pB  = sumVars.select("total_precipitation").rename(ee.String("P_").cat(suffix));
  var rB  = sumVars.select("surface_solar_radiation_downwards").rename(ee.String("R_").cat(suffix));
  var vB  = vpd.rename(ee.String("V_").cat(suffix));
  
  return tB.addBands(dB).addBands(s1B).addBands(s2B).addBands(pB).addBands(rB).addBands(vB);
}

// Build composite for each 16-day window
var compositeImages = ee.ImageCollection(
  ee.List(WINDOW_DOYS).map(function(doy) {
    return compositeForWindow(ee.Number(doy));
  })
);

// Stack all bands into a single image
var stacked = compositeImages.toBands();
var reprojected = stacked.reproject({crs: SHARED_CRS, crsTransform: SHARED_TRANSFORM});

Export.image.toDrive({
  image: reprojected.toFloat(),
  description: "era5_" + YEAR,
  folder: DRIVE_FOLDER,
  fileNamePrefix: "era5_16day_" + YEAR,
  region: EXPORT_REGION,
  crs: SHARED_CRS,
  crsTransform: SHARED_TRANSFORM,
  maxPixels: 2e9,
  fileFormat: "GeoTIFF"
});

print("ERA5 16-day export submitted for " + YEAR);
print("Windows: " + WINDOW_DOYS.length + " composites x 7 variables = " + (WINDOW_DOYS.length * 7) + " bands");
print("Variables: T(t2m), D(d2m), S(swvl1), U(swvl2), P(precip), R(ssr), V(vpd)");
print("Band naming: {var}_{DoY}  (e.g., T_001 = t2m mean for DoY 1-16 window)");
print("Check tasks at https://code.earthengine.google.com/tasks");
