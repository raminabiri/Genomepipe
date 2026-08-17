from dataclasses import dataclass
from pathlib import Path


SUPPORTED_GENOME_SUFFIXES = {".fa", ".fasta", ".fna"}


@dataclass(frozen=True)
class GenomeInput:
    path: Path
    genome_id: str


class GenomeInputManager:
    """Discover and validate locally available genome sequence files."""

    def __init__(self, genome_root: Path):
        self.genome_root = genome_root

    def discover(self) -> tuple[GenomeInput, ...]:
        if not self.genome_root.exists():
            return ()
        files = sorted(
            path for path in self.genome_root.rglob("*")
            if path.is_file() and path.suffix.lower() in SUPPORTED_GENOME_SUFFIXES
        )
        return tuple(GenomeInput(path=path, genome_id=path.stem) for path in files)

    def validate(self, inputs: tuple[GenomeInput, ...] | None = None) -> tuple[str, ...]:
        genomes = inputs if inputs is not None else self.discover()
        errors: list[str] = []
        seen: set[str] = set()
        for genome in genomes:
            if not genome.path.is_file():
                errors.append(f"Missing genome file: {genome.path}")
            if genome.path.stat().st_size == 0:
                errors.append(f"Empty genome file: {genome.path}")
            if genome.genome_id in seen:
                errors.append(f"Duplicate genome ID: {genome.genome_id}")
            seen.add(genome.genome_id)
        return tuple(errors)
