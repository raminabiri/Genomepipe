from pathlib import Path
from typing import Any

import yaml

from .models import ProjectContext


class ConfigError(ValueError):
    """Raised when a GenomePipe project configuration is invalid."""


ALLOWED_DATA_MODES = {"existing", "download"}
REQUIRED_PROJECT_FIELDS = {"organism"}


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.is_file():
        raise ConfigError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    if not isinstance(config, dict):
        raise ConfigError("Project configuration must be a YAML mapping")
    return config


def validate_config(config: dict[str, Any]) -> None:
    project = config.get("project")
    if not isinstance(project, dict):
        raise ConfigError("Missing required mapping: project")

    missing = sorted(REQUIRED_PROJECT_FIELDS - project.keys())
    if missing:
        raise ConfigError(f"Missing required project fields: {', '.join(missing)}")

    organism = project.get("organism")
    if not isinstance(organism, str) or not organism.strip():
        raise ConfigError("project.organism must be a non-empty string")

    data_mode = config.get("data_mode", "existing")
    if data_mode not in ALLOWED_DATA_MODES:
        allowed = ", ".join(sorted(ALLOWED_DATA_MODES))
        raise ConfigError(f"data_mode must be one of: {allowed}")

    paths = config.get("paths", {})
    if not isinstance(paths, dict):
        raise ConfigError("paths must be a YAML mapping")


def build_context(config_path: Path) -> ProjectContext:
    config = load_config(config_path)
    validate_config(config)

    project = config["project"]
    paths = config.get("paths") or {}
    project_root = config_path.parents[1]

    input_root = Path(paths.get("input", project_root / "input"))
    output_root = Path(paths.get("output", project_root / "output"))

    return ProjectContext(
        project_name=project.get("name") or project_root.name,
        project_root=project_root,
        organism=project["organism"].strip(),
        data_mode=config.get("data_mode", "existing"),
        config_path=config_path,
        input_root=input_root,
        output_root=output_root,
        metadata=config.get("metadata") or {},
    )
