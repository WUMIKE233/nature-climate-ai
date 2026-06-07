from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .config import load_study_config
from .evidence import load_evidence_registry


PLACEHOLDER_TOKENS = ("DATA_ACCESS_REQUIRED", "AUTHOR_REQUIRED", "RESULT_REQUIRED")
IGNORED_PARTS = {".pytest_cache", "__pycache__", ".venv", "results"}
IGNORED_DATA_PARTS = {"metadata", "checksums"}
DATA_EXTENSIONS = {".nc", ".nc4", ".h5", ".hdf", ".hdf5", ".zarr", ".csv", ".parquet", ".tif", ".tiff"}


def _display_access_status(status: str) -> str:
    if status == "DATA_ACCESS_REQUIRED":
        return "PENDING_ACCESS_CONFIRMATION"
    return status


@dataclass(frozen=True)
class PlaceholderSummary:
    path: Path
    data_access_required: int
    author_required: int
    result_required: int

    @property
    def total(self) -> int:
        return self.data_access_required + self.author_required + self.result_required


@dataclass(frozen=True)
class DataInventory:
    root: Path
    candidate_files: tuple[Path, ...]
    total_bytes: int

    @property
    def file_count(self) -> int:
        return len(self.candidate_files)


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_PARTS for part in path.parts)


def scan_data_inventory(root: str | Path) -> DataInventory:
    root_path = Path(root)
    candidates: list[Path] = []
    total_bytes = 0
    for path in root_path.rglob("*"):
        if not path.is_file() or _is_ignored(path):
            continue
        if any(part in IGNORED_DATA_PARTS for part in path.relative_to(root_path).parts):
            continue
        if path.suffix.lower() in DATA_EXTENSIONS or path.name.endswith(".zarr"):
            candidates.append(path)
            total_bytes += path.stat().st_size
    return DataInventory(root=root_path, candidate_files=tuple(sorted(candidates)), total_bytes=total_bytes)


def summarize_placeholders(paths: Iterable[str | Path]) -> tuple[PlaceholderSummary, ...]:
    summaries: list[PlaceholderSummary] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists() or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8")
        summaries.append(
            PlaceholderSummary(
                path=path,
                data_access_required=text.count("DATA_ACCESS_REQUIRED"),
                author_required=text.count("AUTHOR_REQUIRED"),
                result_required=text.count("RESULT_REQUIRED"),
            )
        )
    return tuple(summary for summary in summaries if summary.total)


def metadata_files(root: str | Path) -> tuple[Path, ...]:
    metadata_root = Path(root) / "data" / "metadata"
    if not metadata_root.exists():
        return ()
    return tuple(sorted(path for path in metadata_root.rglob("*") if path.is_file()))


def render_e00_qc_report(config_path: str | Path, registry_path: str | Path, root: str | Path = ".") -> str:
    root_path = Path(root)
    config = load_study_config(config_path)
    evidence = load_evidence_registry(registry_path)
    inventory = scan_data_inventory(root_path / "data")
    placeholders = summarize_placeholders(metadata_files(root_path))

    lines = [
        "# E00 data QC report",
        "",
        "Status: NOT_READY",
        "",
        "This report checks whether public data access and local data metadata are ready for analysis. It does not download data, validate credentials or certify provider-policy compliance.",
        "",
        "## Study scope",
        "",
        f"- Target journal: {config['project']['target_journal']}",
        f"- Working title: {config['project']['working_title']}",
        f"- Spatial scope: {config['spatial_domain']['scope']}",
        f"- MODIS years: {config['temporal_domain']['modis_years'][0]}-{config['temporal_domain']['modis_years'][1]}",
        f"- ERA5 years: {config['temporal_domain']['era5_years'][0]}-{config['temporal_domain']['era5_years'][1]}",
        "",
        "## Public data-source readiness",
        "",
        "source | provider | access status | variables/products",
        "--- | --- | --- | ---",
    ]
    for key, source in config["data_sources"].items():
        variables = source.get("variables") or source.get("indices") or source.get("products") or ()
        lines.append(f"{key} | {source['provider']} | {_display_access_status(source['access_status'])} | {', '.join(variables)}")

    lines.extend(
        [
            "",
            "## Local data inventory",
            "",
            f"- Candidate local data files found: {inventory.file_count}",
            f"- Candidate local data size: {inventory.total_bytes} bytes",
        ]
    )
    if inventory.candidate_files:
        lines.extend(["", "path | bytes", "--- | ---"])
        for path in inventory.candidate_files[:50]:
            lines.append(f"{path.as_posix()} | {path.stat().st_size}")
        if len(inventory.candidate_files) > 50:
            lines.append(f"... | {len(inventory.candidate_files) - 50} more files")

    lines.extend(["", "## Metadata placeholder-token counts", "", "file | data_access_token | author_token | result_token", "--- | ---: | ---: | ---:"])
    if placeholders:
        for summary in placeholders:
            lines.append(
                f"{summary.path.as_posix()} | {summary.data_access_required} | "
                f"{summary.author_required} | {summary.result_required}"
            )
    else:
        lines.append("none | 0 | 0 | 0")

    lines.extend(
        [
            "",
            "## Evidence registry status",
            "",
            f"- Complete evidence items: {evidence.complete_count}/{len(evidence.items)}",
            "- E00 can move forward only after pending access notes are replaced by verified provider-access notes and QC artifacts.",
            "",
            "## Blocking actions",
            "",
            "- Confirm Copernicus CDS access and record ERA5/ERA5-Land request parameters.",
            "- Confirm NASA MODIS access route, product collection and quality-bit rules.",
            "- Confirm FLUXNET dataset/version, Tier policy and redistribution/citation requirements.",
            "- Populate local or remote data pointers and rerun this report.",
        ]
    )
    return "\n".join(lines) + "\n"
