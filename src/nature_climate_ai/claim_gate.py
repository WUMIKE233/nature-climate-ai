from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


RESULT_TOKEN = "RESULT_REQUIRED"
AUTHOR_TOKEN = "AUTHOR_REQUIRED"
DATA_TOKEN = "DATA_ACCESS_REQUIRED"


@dataclass(frozen=True)
class ClaimGateReport:
    path: Path
    result_placeholders: int
    author_placeholders: int
    data_placeholders: int

    @property
    def is_evidence_gated(self) -> bool:
        return self.result_placeholders > 0


def inspect_manuscript(path: str | Path) -> ClaimGateReport:
    manuscript_path = Path(path)
    text = manuscript_path.read_text(encoding="utf-8")
    return ClaimGateReport(
        path=manuscript_path,
        result_placeholders=text.count(RESULT_TOKEN),
        author_placeholders=text.count(AUTHOR_TOKEN),
        data_placeholders=text.count(DATA_TOKEN),
    )
