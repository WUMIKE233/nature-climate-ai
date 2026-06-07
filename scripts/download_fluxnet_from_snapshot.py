from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_SNAPSHOT = Path("data/metadata/fluxnet_download/fluxnet_shuttle_snapshot_20260605T081233_selectedsites.csv")
DEFAULT_OUTPUT_DIR = Path("data/raw/fluxnet")
DEFAULT_LOG = Path("data/metadata/fluxnet_download/fluxnet_site_download_log.csv")
CHUNK_SIZE = 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_name(row: dict[str, str]) -> str:
    product = row.get("fluxnet_product_name", "").strip()
    if product:
        return product
    site_id = row.get("site_id", "site").strip() or "site"
    return f"{site_id}_FLUXNET.zip"


def _read_rows(snapshot: Path) -> list[dict[str, str]]:
    with snapshot.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if row.get("download_link")]


def _write_log(log_path: Path, entries: list[dict[str, str | int]]) -> None:
    if not entries:
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    exists = log_path.exists()
    fieldnames = [
        "timestamp",
        "site_id",
        "status",
        "local_path",
        "download_link",
        "size_bytes",
        "sha256",
        "message",
    ]
    with log_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerows(entries)


def _download_one(row: dict[str, str], output_dir: Path, timeout: int) -> dict[str, str | int]:
    site_id = row.get("site_id", "").strip()
    url = row["download_link"].strip()
    target = output_dir / _safe_name(row)
    output_dir.mkdir(parents=True, exist_ok=True)

    if target.exists() and target.stat().st_size > 0:
        return {
            "timestamp": datetime.now().isoformat(),
            "site_id": site_id,
            "status": "skipped",
            "local_path": target.as_posix(),
            "download_link": url,
            "size_bytes": target.stat().st_size,
            "sha256": _sha256(target),
            "message": "Existing non-empty file",
        }

    part = target.with_suffix(target.suffix + ".part")
    existing_partial = part.stat().st_size if part.exists() else 0
    headers = {"User-Agent": "nature-climate-ai/0.1"}
    if existing_partial:
        headers["Range"] = f"bytes={existing_partial}-"
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:
            total = int(response.headers.get("Content-Length") or 0)
            resume_supported = existing_partial > 0 and getattr(response, "status", None) == 206
            mode = "ab" if resume_supported else "wb"
            offset = existing_partial if resume_supported else 0
            if offset and total:
                total += offset
            downloaded = offset
            started = time.monotonic()
            with part.open(mode) as handle:
                while True:
                    chunk = response.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    handle.write(chunk)
                    downloaded += len(chunk)
                    elapsed = max(time.monotonic() - started, 0.001)
                    speed = downloaded / elapsed / (1024 * 1024)
                    if total:
                        pct = downloaded / total * 100
                        print(f"\r{site_id}: {pct:5.1f}% {downloaded / (1024 * 1024):.1f}/{total / (1024 * 1024):.1f} MiB {speed:.2f} MiB/s", end="", flush=True)
                    else:
                        print(f"\r{site_id}: {downloaded / (1024 * 1024):.1f} MiB {speed:.2f} MiB/s", end="", flush=True)
            print()
        part.replace(target)
        size = target.stat().st_size
        return {
            "timestamp": datetime.now().isoformat(),
            "site_id": site_id,
            "status": "success",
            "local_path": target.as_posix(),
            "download_link": url,
            "size_bytes": size,
            "sha256": _sha256(target),
            "message": "Downloaded",
        }
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print()
        return {
            "timestamp": datetime.now().isoformat(),
            "site_id": site_id,
            "status": "failed",
            "local_path": part.as_posix(),
            "download_link": url,
            "size_bytes": part.stat().st_size if part.exists() else 0,
            "sha256": "",
            "message": str(exc),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download FLUXNET Shuttle site zip files from a selected-sites CSV.")
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--limit", type=int, default=None, help="Download only the first N rows for a smoke test.")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    rows = _read_rows(args.snapshot)
    if args.limit is not None:
        rows = rows[: args.limit]

    print(f"Snapshot: {args.snapshot}")
    print(f"Rows with download links: {len(rows)}")
    print(f"Output directory: {args.output_dir}")
    print(f"Log: {args.log}")

    if args.dry_run:
        for row in rows[:10]:
            print(f"DRY {row.get('site_id', '')}: {row.get('fluxnet_product_name', '')} -> {row.get('download_link', '')}")
        if len(rows) > 10:
            print(f"... {len(rows) - 10} more rows")
        return 0

    entries: list[dict[str, str | int]] = []
    for index, row in enumerate(rows, start=1):
        site_id = row.get("site_id", "").strip()
        print(f"[{index}/{len(rows)}] {site_id} {_safe_name(row)}")
        entry = _download_one(row, args.output_dir, args.timeout)
        entries.append(entry)
        _write_log(args.log, [entry])
        print(f"{entry['status'].upper()} {entry['local_path']} {entry['message']}")

    success = sum(entry["status"] == "success" for entry in entries)
    skipped = sum(entry["status"] == "skipped" for entry in entries)
    failed = sum(entry["status"] == "failed" for entry in entries)
    print(f"Done. success={success} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
