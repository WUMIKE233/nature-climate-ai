from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .claim_gate import AUTHOR_TOKEN, DATA_TOKEN, RESULT_TOKEN


PLACEHOLDER_TOKENS = (RESULT_TOKEN, AUTHOR_TOKEN, DATA_TOKEN)
CHINESE_REVIEW_HEADING = "\u4e2d\u6587\u5ba1\u9605\u8bf4\u660e"
CHINESE_REVIEW_NOTE = "\u672c\u62a5\u544a\u5c06\u4e3b\u7a3f\u4e2d\u7684\u6bcf\u4e2a\u5360\u4f4d\u7b26\u6620\u5c04\u5230\u66ff\u6362\u524d\u5fc5\u987b\u5b8c\u6210\u7684\u8bc1\u636e\u9879\u6216\u4f5c\u8005\u8f93\u5165\u3002\u5b83\u662f\u4e00\u9053\u9632\u7ebf\uff1a\u9632\u6b62\u628a\u5c1a\u672a\u5b8c\u6210\u7684\u8ba1\u5212\u6027\u5206\u6790\u5199\u6210\u6ca1\u6709\u8bc1\u636e\u652f\u6491\u7684\u8bba\u6587\u7ed3\u8bba\u3002"


@dataclass(frozen=True)
class PlaceholderMapRow:
    manuscript: str
    line: int
    section: str
    token: str
    linked_evidence_ids: str
    resolution_requirement: str
    context: str


@dataclass(frozen=True)
class PlaceholderMap:
    manuscript: Path
    rows: tuple[PlaceholderMapRow, ...]

    @property
    def complete(self) -> bool:
        return not self.rows

    @property
    def mapped_count(self) -> int:
        return len(self.rows)


def _clean_context(text: str) -> str:
    return " ".join(text.split())


def _section_heading(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith("#"):
        return None
    return stripped.lstrip("#").strip() or None


def _result_mapping(section: str, context: str) -> tuple[str, str]:
    lower = f"{section} {context}".lower()
    if "figure 4" in lower or "fluxnet" in lower or "ecosystem-function" in lower or "ecosystem flux" in lower:
        return (
            "ecosystem_validation;figure_package",
            "Replace only after FLUXNET or other independent ecosystem-function validation artifacts support the claim.",
        )
    if "figure 1" in lower or "event catalogue" in lower or "global map" in lower or "number of events" in lower:
        return (
            "stress_event_catalogue;minimum_publishable_evidence_slice;figure_package",
            "Replace only after the stress-event catalogue, QC report and pilot/full Fig. 1 artifacts exist.",
        )
    if "figure 2" in lower or "precursor" in lower or "lag-response" in lower:
        return (
            "precursor_discovery;temporal_holdout_validation;spatial_holdout_validation;robustness_falsification;figure_package",
            "Replace only after candidate precursor states survive interpretability, temporal, spatial and robustness validation.",
        )
    if "figure 3" in lower or "predictive" in lower or "precision" in lower or "baseline" in lower:
        return (
            "baseline_evaluation;predictive_validation;robustness_falsification;figure_package",
            "Replace only after validation metrics, uncertainty intervals and baseline comparisons support the claimed performance.",
        )
    if "code availability" in lower or "commit hash" in lower or "archive doi" in lower:
        return (
            "manuscript_finalization",
            "Replace only after public code release, archive DOI and checkpoint availability are documented.",
        )
    if "references" in lower or "literature" in lower:
        return (
            "manuscript_finalization",
            "Replace only after targeted literature review and reference metadata audit are complete.",
        )
    return (
        "stress_event_catalogue;precursor_discovery;predictive_validation;ecosystem_validation;robustness_falsification",
        "Replace only after the linked scientific evidence chain supports the exact claim in context.",
    )


def _token_mapping(token: str, section: str, context: str) -> tuple[str, str]:
    if token == RESULT_TOKEN:
        return _result_mapping(section, context)
    if token == DATA_TOKEN:
        return (
            "e00_data_qc;data_access_era5;data_access_modis;data_access_fluxnet",
            "Replace only after provider access, product versions, request parameters, policy notes and checksums are recorded.",
        )
    if token == AUTHOR_TOKEN:
        return (
            "AUTHOR_INPUT_REQUIRED",
            "Replace only after authors provide names, affiliations, contributions, acknowledgements and competing-interest statements.",
        )
    raise ValueError(f"Unsupported placeholder token: {token}")


def build_placeholder_map(manuscript_path: str | Path) -> PlaceholderMap:
    path = Path(manuscript_path)
    section = "Untitled"
    rows: list[PlaceholderMapRow] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        heading = _section_heading(line)
        if heading:
            section = heading
        for token in PLACEHOLDER_TOKENS:
            count = line.count(token)
            if not count:
                continue
            evidence_ids, requirement = _token_mapping(token, section, line)
            for _ in range(count):
                rows.append(
                    PlaceholderMapRow(
                        manuscript=path.as_posix(),
                        line=line_number,
                        section=section,
                        token=token,
                        linked_evidence_ids=evidence_ids,
                        resolution_requirement=requirement,
                        context=_clean_context(line),
                    )
                )
    return PlaceholderMap(manuscript=path, rows=tuple(rows))


def write_placeholder_map_csv(mapping: PlaceholderMap, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "manuscript",
                "line",
                "section",
                "token",
                "linked_evidence_ids",
                "resolution_requirement",
                "context",
            ],
        )
        writer.writeheader()
        for row in mapping.rows:
            writer.writerow(row.__dict__)
    return output


def render_placeholder_map(mapping: PlaceholderMap, csv_path: str | Path) -> str:
    status = "READY_NO_PLACEHOLDERS" if mapping.complete else "NOT_READY"
    lines = [
        "# Manuscript placeholder evidence map",
        "",
        f"Status: {status}",
        f"Manuscript: {mapping.manuscript.as_posix()}",
        f"CSV: {Path(csv_path).as_posix()}",
        "",
        "metric | value",
        "--- | ---",
        f"placeholder_rows | {mapping.mapped_count}",
        "",
        "## Placeholder rows",
        "",
    ]
    if mapping.rows:
        lines.extend(
            [
                "line | section | token | linked evidence/input | resolution requirement",
                "---: | --- | --- | --- | ---",
            ]
        )
        for row in mapping.rows:
            lines.append(
                f"{row.line} | {row.section} | {row.token} | {row.linked_evidence_ids} | {row.resolution_requirement}"
            )
    else:
        lines.append("- No placeholder tokens remain in the manuscript.")
    lines.extend(
        [
            "",
            f"## {CHINESE_REVIEW_HEADING}",
            "",
            CHINESE_REVIEW_NOTE,
        ]
    )
    return "\n".join(lines) + "\n"


def run_placeholder_map_command(
    manuscript_path: str | Path,
    output_path: str | Path,
    csv_path: str | Path,
) -> tuple[PlaceholderMap, Path, Path]:
    mapping = build_placeholder_map(manuscript_path)
    csv_output = write_placeholder_map_csv(mapping, csv_path)
    report_output = Path(output_path)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(render_placeholder_map(mapping, csv_output), encoding="utf-8")
    return mapping, report_output, csv_output
