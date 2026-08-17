from dataclasses import dataclass
from pathlib import Path
import re

from .input_manager import GenomeInput


@dataclass(frozen=True)
class StandardizedGenomeID:
    original: str
    standardized: str


def standardize_genome_id(genome: GenomeInput) -> StandardizedGenomeID:
    """Create a deterministic filesystem-safe ID without modifying the input file."""
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", genome.genome_id).strip("._-")
    if not value:
        value = "genome"
    return StandardizedGenomeID(original=genome.genome_id, standardized=value)


def standardize_genome_ids(genomes: tuple[GenomeInput, ...]) -> tuple[StandardizedGenomeID, ...]:
    return tuple(standardize_genome_id(genome) for genome in genomes)
