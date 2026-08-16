from dataclasses import dataclass
from pathlib import Path

from .checksums import sha256_file
from .input_manager import GenomeInput


@dataclass(frozen=True)
class GenomeInputSnapshot:
    genome_id: str
    path: Path
    size_bytes: int
    sha256: str


def create_snapshot(genomes: tuple[GenomeInput, ...]) -> tuple[GenomeInputSnapshot, ...]:
    """Capture reproducibility metadata for local genome files only."""
    return tuple(
        GenomeInputSnapshot(
            genome_id=genome.genome_id,
            path=genome.path,
            size_bytes=genome.path.stat().st_size,
            sha256=sha256_file(genome.path),
        )
        for genome in genomes
        if genome.path.is_file()
    )
