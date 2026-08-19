from abc import ABC, abstractmethod

from .contracts import ModuleContract, ModuleInput, ModuleOutput
from .models import ModuleResult, ModuleSpec, ProjectContext


class AnalysisPlugin(ABC):
    """Stable interface for organism-aware Genomepipe analysis plugins."""

    spec: ModuleSpec
    contract: ModuleContract

    @abstractmethod
    def run(self, context: ProjectContext, inputs: ModuleInput) -> ModuleResult:
        """Execute the plugin using validated local inputs."""
        raise NotImplementedError

    @abstractmethod
    def describe(self) -> ModuleSpec:
        """Return plugin capability metadata."""
        raise NotImplementedError

    def validate_input(self, inputs: ModuleInput) -> None:
        self.contract.validate_input(inputs)

    def validate_output(self, output: ModuleOutput) -> None:
        self.contract.validate_output(output)
