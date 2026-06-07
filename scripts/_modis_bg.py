"""Simple MODIS download daemon — redirects to log and runs download directly."""
import os, sys, time
from datetime import datetime

os.environ.setdefault("no_proxy", "localhost,127.0.0.1,::1,.nasa.gov,.earthdata.nasa.gov,ladsweb.modaps.eosdis.nasa.gov,urs.earthdata.nasa.gov")
os.environ["NO_PROXY"] = os.environ["no_proxy"]
os.chdir(r"W:\Nature")

log_path = r"W:\Nature\logs\modis_dl_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"

# Create log file with line buffering
import builtins
log_fh = open(log_path, "w", encoding="utf-8", buffering=1)

# Monkey-patch print to write to BOTH stdout and log
_original_print = builtins.print
def _tee_print(*args, **kwargs):
    import io
    # Write to log
    _original_print(*args, file=log_fh, **kwargs)
    log_fh.flush()
_tee_print(f"=== MODIS Download Started: {datetime.now()} ===")
_tee_print(f"PID: {os.getpid()}")
_tee_print(f"Log: {log_path}")

# Override print globally
builtins.print = _tee_print

# Now run the download script by exec-ing its content
sys.argv = ["download_modis_phase1.py", "--max-gb", "100", "--start-year", "2001", "--end-year", "2025", "--products", "MOD13Q1", "MYD13Q1"]

with open(r"W:\Nature\scripts\download_modis_phase1.py", encoding="utf-8") as src:
    code = src.read()

try:
    exec(compile(code, r"W:\Nature\scripts\download_modis_phase1.py", "exec"), {"__name__": "__main__"})
except SystemExit:
    pass
except Exception as e:
    print(f"FATAL: {e}")
    import traceback
    traceback.print_exc()
finally:
    print(f"=== MODIS Download Finished: {datetime.now()} ===")
    log_fh.close()