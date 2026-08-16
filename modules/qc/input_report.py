from dataclasses import dataclass
from pathlib import Path

from .input_manager import GenomeInput, GenomeInputManager
from .manifest import GenomeManifest, build_manifest


@dataclass(frozen=True)
class InputInspection:
    genomes: tuple[GenomeInput, ...]
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def manifest(self) -> GenomeManifest:
        return build_manifest(self.genomes)


def inspect_local_inputs(genome_root: Path) -> InputInspection:
    manager = GenomeInputManager(genome_root)
    genomes = manager.discover()
    errors = manager.validate(genomes)
    return InputInspection(genomes=genomes, errors=errors)
