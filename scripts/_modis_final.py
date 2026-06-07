"""FINAL MODIS downloader — runs download_modis_phase1.main() directly with log capture."""
import os, sys, time, io
from datetime import datetime
from pathlib import Path

os.environ.setdefault("no_proxy", "localhost,127.0.0.1,::1,.nasa.gov,.earthdata.nasa.gov,ladsweb.modaps.eosdis.nasa.gov,urs.earthdata.nasa.gov")
os.environ["NO_PROXY"] = os.environ["no_proxy"]
os.chdir(r"W:\Nature")

log_path = r"W:\Nature\logs\modis_final_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"

class TeeWriter:
    def __init__(self, log_path):
        self.log = open(log_path, "w", encoding="utf-8", buffering=1)
        self.stdout = sys.__stdout__
    def write(self, s):
        self.stdout.write(s)
        self.log.write(s)
        self.log.flush()
    def flush(self):
        self.stdout.flush()
        self.log.flush()

tee = TeeWriter(log_path)
sys.stdout = tee
sys.stderr = tee

print(f"=== FINAL MODIS Download: {datetime.now()} ===")
print(f"PID: {os.getpid()}")
print(f"Log: {log_path}")

# Import and call main directly
sys.path.insert(0, str(Path(r"W:\Nature\scripts").resolve()))
from download_modis_phase1 import main
main()

print(f"=== FINAL MODIS Complete: {datetime.now()} ===")