from pathlib import Path
from typing import Iterable

from .input_manager import GenomeInput
from .sequence_stats import GenomeSequenceStats, calculate_sequence_stats


def summarize_genomes(genomes: Iterable[GenomeInput]) -> tuple[GenomeSequenceStats, ...]:
    """Calculate local sequence statistics for discovered genomes only."""
    return tuple(calculate_sequence_stats(genome) for genome in genomes)


def write_summary_tsv(stats: Iterable[GenomeSequenceStats], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("genome_id\tsequence_count\ttotal_bases\tmin_length\tmax_length\tN50\tGC_percent\n")
        for item in stats:
            handle.write(
                f"{item.genome_id}\t{item.sequence_count}\t{item.total_bases}\t"
                f"{item.min_length}\t{item.max_length}\t{item.n50}\t{item.gc_percent:.4f}\n"
            )
    return path
