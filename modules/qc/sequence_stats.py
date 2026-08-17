from dataclasses import dataclass
from pathlib import Path

from .input_manager import GenomeInput


@dataclass(frozen=True)
class GenomeSequenceStats:
    genome_id: str
    path: Path
    sequence_count: int
    total_bases: int
    min_length: int
    max_length: int
    n50: int
    gc_percent: float


def _n50(lengths: list[int]) -> int:
    if not lengths:
        return 0
    target = sum(lengths) / 2
    cumulative = 0
    for length in sorted(lengths, reverse=True):
        cumulative += length
        if cumulative >= target:
            return length
    return 0


def calculate_sequence_stats(genome: GenomeInput) -> GenomeSequenceStats:
    lengths: list[int] = []
    gc = 0
    total = 0
    current = 0
    in_record = False

    with genome.path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if in_record:
                    lengths.append(current)
                current = 0
                in_record = True
                continue
            if not in_record:
                raise ValueError(f"Sequence data appears before FASTA header: {genome.path}")
            sequence = line.upper()
            current += len(sequence)
            total += len(sequence)
            gc += sequence.count("G") + sequence.count("C")

    if in_record:
        lengths.append(current)
    gc_percent = (100.0 * gc / total) if total else 0.0
    return GenomeSequenceStats(
        genome_id=genome.genome_id,
        path=genome.path,
        sequence_count=len(lengths),
        total_bases=total,
        min_length=min(lengths) if lengths else 0,
        max_length=max(lengths) if lengths else 0,
        n50=_n50(lengths),
        gc_percent=gc_percent,
    )
