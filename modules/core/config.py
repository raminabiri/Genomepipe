from pathlib import Path
from typing import Any

import yaml

from .models import ProjectContext


class ConfigError(ValueError):
    """Raised when a GenomePipe project configuration is invalid."""


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.is_file():
        raise ConfigError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    if not isinstance(config, dict):
        raise ConfigError("Project configuration must be a YAML mapping")
    return config


def build_context(config_path: Path) -> ProjectContext:
    config = load_config(config_path)
    project = config.get("project") or {}
    paths = config.get("paths") or config.get("input") or {}

    project_name = project.get("name") or config_path.parents[1].name
    organism = project.get("organism")
    if not organism:
        raise ConfigError("Missing required field: project.organism")

    project_root = config_path.parents[1]
    input_root = Path(paths.get("root", project_root / "input"))
    output_root = Path(paths.get("output", project_root / "output"))

    return ProjectContext(
        project_name=project_name,
        project_root=project_root,
        organism=organism,
        config_path=config_path,
        input_root=input_root,
        output_root=output_root,
        metadata=config.get("metadata") or {},
    )
