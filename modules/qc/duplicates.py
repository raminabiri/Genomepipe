from collections import defaultdict
from pathlib import Path

from .input_manager import GenomeInput


def find_duplicate_genome_ids(genomes: tuple[GenomeInput, ...]) -> tuple[str, ...]:
    """Return duplicate genome IDs without inspecting or modifying sequence data."""
    paths_by_id: dict[str, list[Path]] = defaultdict(list)
    for genome in genomes:
        paths_by_id[genome.genome_id].append(genome.path)
    return tuple(sorted(genome_id for genome_id, paths in paths_by_id.items() if len(paths) > 1))


def find_duplicate_files_by_size(genomes: tuple[GenomeInput, ...]) -> tuple[tuple[Path, ...], ...]:
    """Flag same-sized files as candidates; size equality is not treated as proof of duplication."""
    groups: dict[int, list[Path]] = defaultdict(list)
    for genome in genomes:
        if genome.path.is_file():
            groups[genome.path.stat().st_size].append(genome.path)
    return tuple(tuple(sorted(paths)) for paths in groups.values() if len(paths) > 1)
