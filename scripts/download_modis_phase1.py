# MODIS Phase 1 downloader — Nature climate/ecology project
# Uses Bearer token (from .edl_token) + no_proxy bypass.
import argparse, time, re, os, sys
from pathlib import Path
import urllib3
urllib3.disable_warnings()
import requests

BASE_URL = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/61"
PRODUCTS = ["MOD13Q1", "MYD13Q1"]
TILES = ["h31v11", "h29v12", "h32v10", "h32v12"]
COLLECTION = "061"
OUTPUT_ROOT = Path(r"W:\Nature\data\raw\modis")
TOKEN_FILE = Path(r"W:\Nature\.edl_token")

# ── No proxy bypass — proxy is required for NASA access in this network ──
# (Previously bypassed proxy, which caused connections to hang)


def get_session():
    token = TOKEN_FILE.read_text().strip()
    if not token:
        raise SystemExit("Token file is empty")
    s = requests.Session()
    s.verify = False
    s.headers.update({"Authorization": f"Bearer {token}"})
    return s


def list_hdf_files(s, product, year, doy):
    doy3 = f"{doy:03d}"
    url = f"{BASE_URL}/{product}/{year}/{doy3}/"
    for attempt in range(3):
        try:
            r = s.get(url, timeout=(30, 300))
            if r.status_code == 404:
                return []
            r.raise_for_status()
            html = r.text
            break
        except Exception as e:
            if attempt < 2:
                time.sleep(10)
                continue
            print(f"  SKIP dir: {url} ({e})")
            return []

    found = []
    for tile in TILES:
        # Build regex: MOD13Q1.A{year}{doy}.h31v11.061.xxxx.hdf
        prefix = re.escape(f"{product}.A{year}{doy3}")
        pat = prefix + r"\." + re.escape(tile) + r"\." + re.escape(COLLECTION) + r"\.[^\s<>\"']+\.hdf"
        for m in re.finditer(pat, html):
            fname = m.group(0)
            if fname not in found:
                found.append(fname)
    return found


def dir_size_gb(root):
    if not root.exists():
        return 0.0
    try:
        return sum(f.stat().st_size for f in root.rglob("*") if f.is_file()) / 1_000_000_000
    except Exception:
        return 0.0


def download_file(s, url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        return "EXISTS"
    headers = {"Authorization": s.headers.get("Authorization", ""), "Connection": "close"}
    for attempt in range(5):
        try:
            r = requests.get(url, headers=headers, timeout=(30, 600), stream=True, verify=False)
            r.raise_for_status()
            # Verify not an auth redirect page
            peek = next(r.iter_content(1024), b"")
            if b"<!DOCTYPE" in peek or b"<html" in peek:
                r.close()
                raise Exception("Got HTML instead of HDF data")
            with open(dest, "wb") as f:
                f.write(peek)
                for chunk in r.iter_content(65536):
                    if chunk:
                        f.write(chunk)
            r.close()
            return "OK"
        except Exception as e:
            try:
                r.close()
            except Exception:
                pass
            if dest.exists():
                try:
                    dest.unlink()
                except OSError:
                    pass
            if attempt < 4:
                wait = min((attempt + 1) * 15, 90)
                time.sleep(wait)
                continue
            raise


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max-gb", type=float, default=100)
    p.add_argument("--start-year", type=int, default=2001)
    p.add_argument("--end-year", type=int, default=2025)
    p.add_argument("--products", nargs="+", default=["MOD13Q1", "MYD13Q1"],
                   help="MODIS products to download (default: MOD13Q1 MYD13Q1)")
    args = p.parse_args()
    products = args.products

    print("Auth: Bearer token from .edl_token")
    s = get_session()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    current = dir_size_gb(OUTPUT_ROOT)
    print(f"Root: {OUTPUT_ROOT}")
    print(f"Initial: {current:.2f} GB | Limit: {args.max_gb} GB")
    print(f"Products: {products} | Tiles: {TILES}")
    print(f"Years: {args.start_year}-{args.end_year}")
    print()

    for year in range(args.start_year, args.end_year + 1):
        for doy in range(1, 367, 16):
            for product in products:
                current = dir_size_gb(OUTPUT_ROOT)
                if current >= args.max_gb:
                    print(f"\nSTOP: {current:.2f} GB >= {args.max_gb} GB")
                    return
                files = list_hdf_files(s, product, year, doy)
                if not files:
                    continue
                for fname in files:
                    current = dir_size_gb(OUTPUT_ROOT)
                    if current >= args.max_gb:
                        print(f"\nSTOP: {current:.2f} GB >= {args.max_gb} GB")
                        return
                    doy3 = f"{doy:03d}"
                    url = f"{BASE_URL}/{product}/{year}/{doy3}/{fname}"
                    dest = OUTPUT_ROOT / product / str(year) / doy3 / fname
                    if dest.exists() and dest.stat().st_size > 1000:
                        continue
                    time.sleep(0.3)
                    print(f"[{year}/{doy3}] {fname[:40]}...", end=" ", flush=True)
                    try:
                        st = download_file(s, url, dest)
                        gb = dir_size_gb(OUTPUT_ROOT)
                        mb = dest.stat().st_size / 1_000_000
                        print(f"{mb:.1f} MB [total={gb:.2f} GB]")
                    except Exception as e:
                        print(f"FAIL: {type(e).__name__}")

    print(f"\nDONE. Final: {dir_size_gb(OUTPUT_ROOT):.2f} GB")


if __name__ == "__main__":
    main()
