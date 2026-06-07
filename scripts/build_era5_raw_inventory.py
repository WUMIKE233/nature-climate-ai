from __future__ import annotations

import csv
from pathlib import Path

import xarray as xr


ROOT = Path("data/raw/era5")
CHECKSUM_CSV = Path("data/checksums/data_checksums.csv")
OUTPUT_CSV = Path("data/metadata/era5_raw_inventory.csv")
OUTPUT_MD = Path("data/metadata/era5_raw_inventory.md")


def _load_checksums() -> dict[str, str]:
    if not CHECKSUM_CSV.exists():
        return {}
    with CHECKSUM_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        checksums: dict[str, str] = {}
        for row in rows:
            normalized = {key.strip("\ufeff"): value for key, value in row.items() if key is not None}
            path = normalized.get("path") or normalized.get("file")
            checksum = normalized.get("checksum") or normalized.get("sha256")
            if path and checksum:
                checksums[path] = checksum
        return checksums


def main() -> int:
    checksums = _load_checksums()
    rows: list[dict[str, str | int]] = []
    for path in sorted(ROOT.rglob("*.nc")):
        relative = path.as_posix()
        try:
            dataset = xr.open_dataset(path)
        except Exception as exc:
            rows.append(
                {
                    "path": relative,
                    "bytes": path.stat().st_size,
                    "read_status": "UNREADABLE",
                    "variables": "",
                    "dimensions": "",
                    "sha256": checksums.get(relative, ""),
                    "issue": str(exc).replace("\n", " "),
                }
            )
            continue
        try:
            rows.append(
                {
                    "path": relative,
                    "bytes": path.stat().st_size,
                    "read_status": "READABLE",
                    "variables": ";".join(dataset.data_vars),
                    "dimensions": ";".join(f"{name}={size}" for name, size in dataset.sizes.items()),
                    "sha256": checksums.get(relative, ""),
                    "issue": "",
                }
            )
        finally:
            dataset.close()

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["path", "bytes", "read_status", "variables", "dimensions", "sha256", "issue"],
        )
        writer.writeheader()
        writer.writerows(rows)

    unreadable_count = sum(1 for row in rows if row["read_status"] == "UNREADABLE")
    status = "READY_FOR_QC_INPUT" if unreadable_count == 0 else "PARTIAL_WITH_UNREADABLE_FILES"
    lines = [
        "# ERA5 raw inventory",
        "",
        f"Status: {status}",
        "",
        "file | bytes | read_status | variables | dimensions | sha256 | issue",
        "--- | ---: | --- | --- | --- | --- | ---",
    ]
    for row in rows:
        lines.append(
            f"{row['path']} | {row['bytes']} | {row['read_status']} | {row['variables']} | {row['dimensions']} | {row['sha256']} | {row['issue']}"
        )
    lines.extend(
        [
            "",
            "## 中文审阅说明",
            "",
            "本清单记录用户提供并已解压的 ERA5/ERA5-Land NetCDF 原始文件、变量、维度和 SHA-256 校验值。它只证明本地数据文件可被读取，不代表科学质量控制、特征工程或论文结果已经完成。",
        ]
    )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUTPUT_MD)
    print(OUTPUT_CSV)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
