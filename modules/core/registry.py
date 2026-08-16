from collections.abc import Callable

from .models import ModuleSpec


ModuleFactory = Callable[[], object]


class ModuleRegistry:
    """Registry for organism-aware analysis modules.

    Core code never imports organism-specific implementations directly.
    """

    def __init__(self) -> None:
        self._modules: dict[str, tuple[ModuleSpec, ModuleFactory]] = {}

    def register(self, spec: ModuleSpec, factory: ModuleFactory) -> None:
        if spec.name in self._modules:
            raise ValueError(f"Module already registered: {spec.name}")
        self._modules[spec.name] = (spec, factory)

    def get(self, name: str, organism: str) -> object:
        try:
            spec, factory = self._modules[name]
        except KeyError as exc:
            raise KeyError(f"Unknown module: {name}") from exc

        if not spec.supports(organism):
            raise ValueError(
                f"Module '{name}' does not support organism '{organism}'"
            )
        return factory()

    def specs(self) -> tuple[ModuleSpec, ...]:
        return tuple(spec for spec, _ in self._modules.values())
