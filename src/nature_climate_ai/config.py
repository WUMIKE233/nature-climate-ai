from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_study_config(path: str | Path) -> dict[str, Any]:
    """Load and minimally validate the study configuration."""
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Study config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    if not isinstance(config, dict):
        raise ValueError("Study config must be a YAML mapping.")

    required = {"project", "data_sources", "stress_event_definition", "modeling", "validation"}
    missing = required.difference(config)
    if missing:
        raise ValueError(f"Study config missing required sections: {sorted(missing)}")

    return config
