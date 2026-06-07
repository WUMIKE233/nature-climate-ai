// GEE Code Editor script: Export MODIS MOD13Q1/MYD13Q1 for Nature project
// Paste into https://code.earthengine.google.com/
// Run once per year (change YEAR variable, or loop manually)

var YEAR = 2001;  // Change this for each year: 2001-2025
var DRIVE_FOLDER = "Nature_MODIS_Export";

// Shared grid used by MODIS and ERA5 exports.
// Keep these constants identical to scripts/export_era5_gee.js.
// The current working domain is the Australia-focused GEE export footprint.
// For a Nature-global analysis, expand EXPORT_REGION first, then re-export both datasets.
var SHARED_CRS = "EPSG:4326";
var SHARED_TRANSFORM = [0.25, 0, 109.75, 0, -0.25, -10.00];
var EXPORT_REGION = ee.Geometry.Rectangle([109.75, -40.25, 150.25, -10.00], null, false);

// Quality filter: same logic as modis_quality.py
function addQualityMask(image) {
  var qa = image.select("SummaryQA");
  var modland = qa.bitwiseAnd(3);
  var viUse = qa.rightShift(2).bitwiseAnd(15);
  var aerosol = qa.rightShift(6).bitwiseAnd(3);
  var adjCloud = qa.rightShift(8).bitwiseAnd(1);
  var mixedCloud = qa.rightShift(10).bitwiseAnd(1);
  var snowIce = qa.rightShift(14).bitwiseAnd(1);
  var shadow = qa.rightShift(15).bitwiseAnd(1);
  
  var ok = modland.lte(1)
    .and(viUse.lte(11))
    .and(aerosol.lte(1))
    .and(adjCloud.eq(0))
    .and(mixedCloud.eq(0))
    .and(snowIce.eq(0))
    .and(shadow.eq(0));
  
  return image.addBands(ok.rename("qa_ok").uint8());
}

// Load both MODIS products
var startDate = YEAR + "-01-01";
var endDate = (YEAR + 1) + "-01-01";

var mod = ee.ImageCollection("MODIS/061/MOD13Q1")
  .filterDate(startDate, endDate)
  .map(addQualityMask)
  .select(["NDVI", "EVI", "qa_ok"]);

var myd = ee.ImageCollection("MODIS/061/MYD13Q1")
  .filterDate(startDate, endDate)
  .map(addQualityMask)
  .select(["NDVI", "EVI", "qa_ok"]);

var combined = mod.merge(myd);
var count = combined.size();
print("Year " + YEAR + ": " + count.getInfo() + " images");

// Stack all images into bands: N_YYYYMMDD, E_YYYYMMDD, Q_YYYYMMDD
var imgList = combined.toList(count);

function dateBands(i) {
  i = ee.Number(i);
  var img = ee.Image(imgList.get(i));
  var dateStr = ee.Date(img.get("system:time_start")).format("YYYYMMdd");
  var ndvi = img.select("NDVI").rename(ee.String("N_").cat(dateStr));
  var evi = img.select("EVI").rename(ee.String("E_").cat(dateStr));
  var qa = img.select("qa_ok").rename(ee.String("Q_").cat(dateStr));
  return ndvi.addBands(evi).addBands(qa);
}

var stacked = ee.ImageCollection(ee.List.sequence(0, count.subtract(1)).map(dateBands)).toBands();
var reprojected = stacked.reproject({crs: SHARED_CRS, crsTransform: SHARED_TRANSFORM});

// Export to Google Drive
Export.image.toDrive({
  image: reprojected.toFloat(),
  description: "modis_" + YEAR,
  folder: DRIVE_FOLDER,
  fileNamePrefix: "modis_obs_" + YEAR,
  region: EXPORT_REGION,
  crs: SHARED_CRS,
  crsTransform: SHARED_TRANSFORM,
  maxPixels: 1e10,
  fileFormat: "GeoTIFF"
});

print("Export task submitted for " + YEAR);
print("Monitor: https://code.earthengine.google.com/tasks");
