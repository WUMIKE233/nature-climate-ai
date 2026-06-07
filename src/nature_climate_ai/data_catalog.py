from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DataSource:
    key: str
    provider: str
    source_url: str
    access_status: str
    variables: tuple[str, ...]


def sources_from_config(config: dict) -> list[DataSource]:
    sources: list[DataSource] = []
    for key, value in config["data_sources"].items():
        variables = tuple(value.get("variables") or value.get("indices") or value.get("products") or ())
        sources.append(
            DataSource(
                key=key,
                provider=value["provider"],
                source_url=value["source_url"],
                access_status=value["access_status"],
                variables=variables,
            )
        )
    return sources


def format_source_table(sources: Iterable[DataSource]) -> str:
    rows = ["source | provider | access | variables", "--- | --- | --- | ---"]
    for source in sources:
        rows.append(
            f"{source.key} | {source.provider} | {source.access_status} | "
            f"{', '.join(source.variables) if source.variables else 'not specified'}"
        )
    return "\n".join(rows)
