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


DEFAULT_MANIFEST = Path("data/metadata/fluxnet_retry_manifest.csv")
DEFAULT_OUTPUT_DIR = Path("data/raw/fluxnet")
DEFAULT_LOG = Path("data/metadata/fluxnet_download/fluxnet_retry_download_log.csv")
CHUNK_SIZE = 1024 * 1024


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row.get("download_link")]


def _write_log(log_path: Path, entry: dict[str, str | int]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    exists = log_path.exists()
    fieldnames = [
        "timestamp",
        "site_id",
        "status",
        "retry_path",
        "original_path",
        "download_link",
        "size_bytes",
        "sha256",
        "message",
    ]
    with log_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(entry)


def _retry_target(row: dict[str, str], output_dir: Path) -> Path:
    product = row.get("expected_product", "").strip()
    if not product:
        product = Path(row.get("local_archive", "fluxnet_problem.zip")).name
    return output_dir / f"{product}.retry.zip"


def _download_retry(row: dict[str, str], output_dir: Path, timeout: int) -> dict[str, str | int]:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = _retry_target(row, output_dir)
    part = target.with_suffix(target.suffix + ".part")
    site_id = row.get("site_id", "").strip()
    url = row["download_link"].strip()

    if target.exists() and target.stat().st_size > 0:
        return {
            "timestamp": datetime.now().isoformat(),
            "site_id": site_id,
            "status": "skipped",
            "retry_path": target.as_posix(),
            "original_path": row.get("local_archive", ""),
            "download_link": url,
            "size_bytes": target.stat().st_size,
            "sha256": _sha256(target),
            "message": "Existing retry file",
        }

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
        return {
            "timestamp": datetime.now().isoformat(),
            "site_id": site_id,
            "status": "success",
            "retry_path": target.as_posix(),
            "original_path": row.get("local_archive", ""),
            "download_link": url,
            "size_bytes": target.stat().st_size,
            "sha256": _sha256(target),
            "message": "Downloaded retry copy without replacing original",
        }
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        print()
        return {
            "timestamp": datetime.now().isoformat(),
            "site_id": site_id,
            "status": "failed",
            "retry_path": part.as_posix(),
            "original_path": row.get("local_archive", ""),
            "download_link": url,
            "size_bytes": part.stat().st_size if part.exists() else 0,
            "sha256": "",
            "message": str(exc),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Retry FLUXNET problem archives without overwriting original files.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    rows = _read_manifest(args.manifest)
    if args.limit is not None:
        rows = rows[: args.limit]

    print(f"Retry manifest: {args.manifest}")
    print(f"Rows: {len(rows)}")
    print(f"Output directory: {args.output_dir}")
    print(f"Log: {args.log}")

    if args.dry_run:
        for row in rows[:10]:
            print(f"DRY {row.get('site_id', '')}: {_retry_target(row, args.output_dir)} <- {row.get('download_link', '')}")
        if len(rows) > 10:
            print(f"... {len(rows) - 10} more rows")
        return 0

    success = skipped = failed = 0
    for index, row in enumerate(rows, start=1):
        print(f"[{index}/{len(rows)}] {row.get('site_id', '')} {row.get('zip_status', '')}")
        entry = _download_retry(row, args.output_dir, args.timeout)
        _write_log(args.log, entry)
        print(f"{entry['status'].upper()} {entry['retry_path']} {entry['message']}")
        success += int(entry["status"] == "success")
        skipped += int(entry["status"] == "skipped")
        failed += int(entry["status"] == "failed")

    print(f"Done. success={success} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
