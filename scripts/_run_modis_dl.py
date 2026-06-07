import subprocess, sys, os, time
from datetime import datetime

os.environ.setdefault("no_proxy", "localhost,127.0.0.1,::1,.nasa.gov,.earthdata.nasa.gov,ladsweb.modaps.eosdis.nasa.gov,urs.earthdata.nasa.gov")
os.environ["NO_PROXY"] = os.environ["no_proxy"]

log_path = r"W:\Nature\logs\modis_dl_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"

with open(log_path, "w", encoding="utf-8") as log:
    log.write(f"Started: {datetime.now()}\n")
    log.flush()
    
    proc = subprocess.Popen(
        [sys.executable, "-u", r"W:\Nature\scripts\download_modis_phase1.py",
         "--max-gb", "100", "--start-year", "2001", "--end-year", "2025",
         "--products", "MOD13Q1", "MYD13Q1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=r"W:\Nature",
        text=True,
        bufsize=1,
    )
    
    for line in proc.stdout:
        log.write(line)
        log.flush()
    
    proc.wait()
    log.write(f"\nFinished: {datetime.now()} (exit code {proc.returncode})\n")

print(f"Log: {log_path}")