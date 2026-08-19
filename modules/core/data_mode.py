from pathlib import Path
from typing import Any

from .models import ProjectContext


class DataModeError(ValueError):
    """Raised when a project data mode cannot be handled safely."""


def resolve_data_mode(context: ProjectContext) -> str:
    """Return the validated execution mode for the project."""
    if context.data_mode not in {"existing", "download"}:
        raise DataModeError(f"Unsupported data mode: {context.data_mode}")
    return context.data_mode


def describe_data_source(context: ProjectContext) -> dict[str, Any]:
    """Return a side-effect-free description of the selected data source."""
    mode = resolve_data_mode(context)
    if mode == "existing":
        return {
            "mode": mode,
            "network_required": False,
            "input_root": context.input_root,
        }

    return {
        "mode": mode,
        "network_required": True,
        "input_root": context.input_root,
    }


def require_existing_input(context: ProjectContext) -> Path:
    """Validate the local input root without downloading or modifying data."""
    if resolve_data_mode(context) != "existing":
        raise DataModeError("Existing input is required for this operation")
    if not context.input_root.exists():
        raise DataModeError(f"Existing input directory not found: {context.input_root}")
    if not context.input_root.is_dir():
        raise DataModeError(f"Existing input path is not a directory: {context.input_root}")
    return context.input_root
