from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol, cast

from ruamel.yaml import YAML

from .models import CVConfigRoot, EntryConfig, ProfessionalData, SectionConfig


class _EntryWithId(Protocol):
    id: str


def _load_yaml(path: str | Path) -> object:
    yaml = YAML(typ="safe")
    load = cast(Callable[[object], object], yaml.load)
    with Path(path).open() as file:
        return load(file)


def load_professional_data(path: str | Path) -> ProfessionalData:
    """Load and validate professional data YAML."""
    return ProfessionalData.model_validate(_load_yaml(path))


def load_cv_config(path: str | Path) -> CVConfigRoot:
    """Load and validate CV config YAML."""
    return CVConfigRoot.model_validate(_load_yaml(path))


def resolve_section(
    data: ProfessionalData,
    config: CVConfigRoot,
    section_name: str,
) -> list[tuple[object, EntryConfig]]:
    """
    Return list of (data_entry, entry_config) pairs for the section,
    in the order defined by config.

    Raises ValueError if section_name not found in config sections,
    or if an entry ID in config is not found in data.
    """
    section_config = cast(SectionConfig | None, getattr(config.sections, section_name, None))
    if section_config is None:
        raise ValueError(f"Section '{section_name}' not found in config")

    data_entries = cast(list[_EntryWithId], getattr(data, section_name, []))
    entries_by_id = {entry.id: entry for entry in data_entries}

    resolved: list[tuple[object, EntryConfig]] = []
    for entry_config in section_config.entries:
        data_entry = entries_by_id.get(entry_config.id)
        if data_entry is None:
            raise ValueError(
                f"Entry ID '{entry_config.id}' not found in data section '{section_name}'"
            )
        resolved.append((data_entry, entry_config))

    return resolved
