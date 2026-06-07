from __future__ import annotations

import csv
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class PilotFigureResult:
    completed_for_input: bool
    report_path: Path
    manifest_path: Path
    figure_paths: tuple[Path, ...]


PNG_WIDTH = 960
PNG_HEIGHT = 600


def _chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _write_png(path: str | Path, width: int, height: int, pixels: list[list[tuple[int, int, int]]]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    raw = b"".join(b"\x00" + b"".join(bytes(pixel) for pixel in row) for row in pixels)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _chunk(b"IDAT", zlib.compress(raw, level=9))
        + _chunk(b"IEND", b"")
    )
    output.write_bytes(data)
    return output


def _blank_canvas(width: int = PNG_WIDTH, height: int = PNG_HEIGHT) -> list[list[tuple[int, int, int]]]:
    return [[(255, 255, 255) for _ in range(width)] for _ in range(height)]


def _rect(
    pixels: list[list[tuple[int, int, int]]],
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int],
) -> None:
    height = len(pixels)
    width = len(pixels[0]) if height else 0
    for y in range(max(0, y0), min(height, y1)):
        row = pixels[y]
        for x in range(max(0, x0), min(width, x1)):
            row[x] = color


def _line(
    pixels: list[list[tuple[int, int, int]]],
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int],
) -> None:
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for step in range(steps + 1):
        x = round(x0 + (x1 - x0) * step / steps)
        y = round(y0 + (y1 - y0) * step / steps)
        _rect(pixels, x - 1, y - 1, x + 2, y + 2, color)


def _chart_frame(pixels: list[list[tuple[int, int, int]]]) -> None:
    _rect(pixels, 80, 80, 88, 520, (31, 41, 55))
    _rect(pixels, 80, 512, 880, 520, (31, 41, 55))
    _rect(pixels, 40, 40, 920, 44, (15, 23, 42))


def _numeric_series(frame: pd.DataFrame, preferred: tuple[str, ...]) -> list[float]:
    for column in preferred:
        if column in frame.columns:
            values = pd.to_numeric(frame[column], errors="coerce").dropna().tolist()
            if values:
                return [float(value) for value in values]
    for column in frame.columns:
        values = pd.to_numeric(frame[column], errors="coerce").dropna().tolist()
        if values:
            return [float(value) for value in values]
    return []


def _bar_png(values: list[float], output: str | Path, color: tuple[int, int, int]) -> Path:
    pixels = _blank_canvas()
    _chart_frame(pixels)
    if values:
        selected = values[:24]
        baseline = min(0.0, min(selected))
        top = max(selected)
        spread = top - baseline if top != baseline else 1.0
        bar_width = max(8, int(760 / max(len(selected), 1)))
        for index, value in enumerate(selected):
            x0 = 100 + index * bar_width
            x1 = x0 + max(4, bar_width - 4)
            y1 = 512
            y0 = int(512 - ((value - baseline) / spread) * 420)
            _rect(pixels, x0, min(y0, y1), x1, max(y0, y1), color)
    return _write_png(output, PNG_WIDTH, PNG_HEIGHT, pixels)


def _line_png(values: list[float], output: str | Path, color: tuple[int, int, int]) -> Path:
    pixels = _blank_canvas()
    _chart_frame(pixels)
    if values:
        selected = values[:80]
        bottom = min(selected)
        top = max(selected)
        spread = top - bottom if top != bottom else 1.0
        points: list[tuple[int, int]] = []
        for index, value in enumerate(selected):
            x = 100 + int(index * 760 / max(len(selected) - 1, 1))
            y = int(512 - ((value - bottom) / spread) * 420)
            points.append((x, y))
        for start, end in zip(points, points[1:]):
            _line(pixels, start[0], start[1], end[0], end[1], color)
        for x, y in points:
            _rect(pixels, x - 4, y - 4, x + 5, y + 5, color)
    return _write_png(output, PNG_WIDTH, PNG_HEIGHT, pixels)


def _event_values(path: Path) -> list[float]:
    frame = pd.read_csv(path)
    if "pixel_id" in frame.columns:
        return frame.groupby("pixel_id").size().astype(float).tolist()
    if "event_id" in frame.columns:
        return list(range(1, len(frame) + 1))
    return _numeric_series(frame, ("event_count", "duration_observations", "mean_anomaly", "min_anomaly"))


def _precursor_values(attribution_path: Path, lag_response_path: Path) -> list[float]:
    if attribution_path.exists():
        values = _numeric_series(pd.read_csv(attribution_path), ("absolute_correlation", "importance", "score"))
        if values:
            return values
    return _numeric_series(pd.read_csv(lag_response_path), ("mean_response", "absolute_correlation", "importance", "score"))


def _validation_values(path: Path) -> list[float]:
    return _numeric_series(pd.read_csv(path), ("accuracy", "recall", "precision", "false_alarm_rate"))


def _missing(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    return tuple(path for path in paths if not path.exists())


def render_pilot_figure_report(
    completed: bool,
    figure_paths: tuple[Path, ...],
    manifest_path: Path,
    missing_paths: tuple[Path, ...],
) -> str:
    status = "COMPLETE_FOR_INPUT_DATA" if completed else "NOT_READY"
    lines = [
        "# Pilot figure generation report",
        "",
        f"Status: {status}",
        f"Manifest: {manifest_path.as_posix()}",
        "",
        "## Figures",
        "",
    ]
    if figure_paths:
        lines.extend(f"- {path.as_posix()}" for path in figure_paths)
    else:
        lines.append("- None generated.")
    lines.extend(["", "## Missing inputs", ""])
    if missing_paths:
        lines.extend(f"- {path.as_posix()}" for path in missing_paths)
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Manuscript-use warning",
            "",
            "Pilot figures summarize supplied pilot artifacts only. They do not establish Nature/Science-ready conclusions without human scientific review.",
            "",
            "## 中文审阅说明",
            "",
            "本命令只在真实 pilot 输入文件存在时生成图件；如果输入缺失，只写准备度报告。生成图件本身不代表结论成立，仍需人工审阅信号强度、基线优势和稳健性。",
        ]
    )
    return "\n".join(lines) + "\n"


def write_pilot_figure_manifest(figure_paths: tuple[Path, ...], manifest_path: str | Path) -> Path:
    output = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["figure", "path", "status"])
        writer.writeheader()
        for index, path in enumerate(figure_paths, start=1):
            writer.writerow({"figure": f"pilot_fig{index}", "path": path.as_posix(), "status": "generated_from_input"})
    return output


def run_pilot_figure_generation_command(
    event_path: str | Path,
    attribution_path: str | Path,
    lag_response_path: str | Path,
    predictive_path: str | Path,
    output_dir: str | Path,
    manifest_path: str | Path,
    report_path: str | Path,
) -> PilotFigureResult:
    event_file = Path(event_path)
    attribution_file = Path(attribution_path)
    lag_response_file = Path(lag_response_path)
    predictive_file = Path(predictive_path)
    output_root = Path(output_dir)
    manifest = Path(manifest_path)
    report = Path(report_path)
    output_root.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)

    required = (event_file, lag_response_file, predictive_file)
    missing_paths = _missing(required)
    if missing_paths:
        manifest_output = write_pilot_figure_manifest((), manifest)
        report.write_text(render_pilot_figure_report(False, (), manifest_output, missing_paths), encoding="utf-8")
        return PilotFigureResult(False, report, manifest_output, ())

    fig1 = _bar_png(_event_values(event_file), output_root / "pilot_fig1_stress_event_map.png", (37, 99, 235))
    fig2 = _bar_png(_precursor_values(attribution_file, lag_response_file), output_root / "pilot_fig2_precursor_pathway.png", (147, 51, 234))
    fig3 = _line_png(_validation_values(predictive_file), output_root / "pilot_fig3_predictive_validation.png", (220, 38, 38))
    figure_paths = (fig1, fig2, fig3)
    manifest_output = write_pilot_figure_manifest(figure_paths, manifest)
    report.write_text(render_pilot_figure_report(True, figure_paths, manifest_output, ()), encoding="utf-8")
    return PilotFigureResult(True, report, manifest_output, figure_paths)
