from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class ProjectContext:
    """Immutable runtime context shared by pipeline modules."""

    project_name: str
    project_root: Path
    organism: str
    config_path: Path
    input_root: Path
    output_root: Path
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModuleResult:
    """Standard result contract for pipeline modules."""

    module: str
    status: str
    outputs: tuple[Path, ...] = ()
    metrics: Mapping[str, Any] = field(default_factory=dict)
    message: str = ""

    def __post_init__(self) -> None:
        if self.status not in {"success", "skipped", "failed"}:
            raise ValueError(f"Invalid module status: {self.status}")


@dataclass(frozen=True)
class ModuleSpec:
    """Description used to register an analysis module."""

    name: str
    version: str
    organisms: tuple[str, ...] = ()
    description: str = ""

    def supports(self, organism: str) -> bool:
        return not self.organisms or organism in self.organisms
