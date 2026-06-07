"""MODIS download daemon — runs in fully detached background process."""
import subprocess, sys, os, time
from datetime import datetime

os.environ.setdefault("no_proxy", "localhost,127.0.0.1,::1,.nasa.gov,.earthdata.nasa.gov,ladsweb.modaps.eosdis.nasa.gov,urs.earthdata.nasa.gov")
os.environ["NO_PROXY"] = os.environ["no_proxy"]

log_path = r"W:\Nature\logs\modis_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"

with open(log_path, "w", encoding="utf-8") as log:
    log.write(f"Daemon started: {datetime.now()}\n")
    log.flush()
    
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    
    proc = subprocess.Popen(
        [sys.executable, "-u",
         r"W:\Nature\scripts\download_modis_phase1.py",
         "--max-gb", "100", "--start-year", "2001", "--end-year", "2025",
         "--products", "MOD13Q1", "MYD13Q1"],
        stdout=log,
        stderr=subprocess.STDOUT,
        cwd=r"W:\Nature",
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
    )
    
    log.write(f"Child PID: {proc.pid}\n")
    log.write(f"Daemon exiting, child will continue independently\n")
    log.flush()
    
    print(f"Daemon launched. Child PID: {proc.pid}")
    print(f"Log: {log_path}")