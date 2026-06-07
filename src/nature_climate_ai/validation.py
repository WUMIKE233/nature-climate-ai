from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationDesign:
    temporal_holdout_years: tuple[int, int]
    spatial_holdout: str
    statistical_checks: tuple[str, ...]
    external_validation_source: str


def validation_design_from_config(config: dict) -> ValidationDesign:
    validation = config["validation"]
    external = validation["external_validation"]
    return ValidationDesign(
        temporal_holdout_years=tuple(validation["temporal_holdout_years"]),
        spatial_holdout=validation["spatial_holdout"],
        statistical_checks=tuple(validation["statistical_checks"]),
        external_validation_source=external["source"],
    )
