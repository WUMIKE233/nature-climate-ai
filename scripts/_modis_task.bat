@echo off
cd /d W:\Nature
set no_proxy=localhost,127.0.0.1,::1,.nasa.gov,.earthdata.nasa.gov,ladsweb.modaps.eosdis.nasa.gov,urs.earthdata.nasa.gov
set NO_PROXY=%no_proxy%
echo %date% %time% === MODIS Download Task Started === > "W:\Nature\logs\modis_task_20260606_002517.log"
W:\Nature\.venv\Scripts\python.exe -u W:\Nature\scripts\download_modis_phase1.py --max-gb 100 --start-year 2001 --end-year 2025 --products MOD13Q1 MYD13Q1 >> "W:\Nature\logs\modis_task_20260606_002517.log" 2>&1
echo %date% %time% === MODIS Download Task Finished === >> "W:\Nature\logs\modis_task_20260606_002517.log"