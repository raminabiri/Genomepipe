from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


class ContractError(ValueError):
    """Raised when a module input/output contract is invalid."""


@dataclass(frozen=True)
class ModuleInput:
    """Standard input contract passed to a pipeline module."""

    name: str
    paths: tuple[Path, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ContractError("ModuleInput.name must be non-empty")
        if any(not isinstance(path, Path) for path in self.paths):
            raise ContractError("ModuleInput.paths must contain Path objects")


@dataclass(frozen=True)
class ModuleOutput:
    """Standard output contract produced by a pipeline module."""

    name: str
    paths: tuple[Path, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ContractError("ModuleOutput.name must be non-empty")
        if any(not isinstance(path, Path) for path in self.paths):
            raise ContractError("ModuleOutput.paths must contain Path objects")


@dataclass(frozen=True)
class ModuleContract:
    """Declares the stable interface of a pipeline module."""

    name: str
    version: str
    input_names: tuple[str, ...] = ()
    output_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ContractError("ModuleContract.name must be non-empty")
        if not self.version.strip():
            raise ContractError("ModuleContract.version must be non-empty")
        if len(set(self.input_names)) != len(self.input_names):
            raise ContractError("Duplicate input contract names")
        if len(set(self.output_names)) != len(self.output_names):
            raise ContractError("Duplicate output contract names")

    def validate_input(self, value: ModuleInput) -> None:
        if value.name not in self.input_names:
            raise ContractError(
                f"Input '{value.name}' is not declared by module '{self.name}'"
            )

    def validate_output(self, value: ModuleOutput) -> None:
        if value.name not in self.output_names:
            raise ContractError(
                f"Output '{value.name}' is not declared by module '{self.name}'"
            )
