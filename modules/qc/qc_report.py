from dataclasses import dataclass
from pathlib import Path
import csv

from .input_manager import GenomeInput
from .integrity import validate_fasta_integrity
from .sequence_stats import calculate_sequence_stats


@dataclass(frozen=True)
class GenomeQCRecord:
    genome_id: str
    path: Path
    status: str
    sequence_count: int
    total_bases: int
    n50: int
    gc_percent: float
    errors: tuple[str, ...]


def qc_genome(genome: GenomeInput) -> GenomeQCRecord:
    integrity = validate_fasta_integrity(genome)
    stats = calculate_sequence_stats(genome)
    status = "FAIL" if not integrity.valid else "PASS"
    return GenomeQCRecord(
        genome_id=genome.genome_id,
        path=genome.path,
        status=status,
        sequence_count=stats.sequence_count,
        total_bases=stats.total_bases,
        n50=stats.n50,
        gc_percent=stats.gc_percent,
        errors=integrity.errors,
    )


def run_qc(genomes: tuple[GenomeInput, ...]) -> tuple[GenomeQCRecord, ...]:
    return tuple(qc_genome(genome) for genome in genomes)


def write_qc_report(records: tuple[GenomeQCRecord, ...], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["genome_id", "path", "status", "sequence_count", "total_bases", "N50", "GC_percent", "errors"])
        for record in records:
            writer.writerow([
                record.genome_id,
                str(record.path),
                record.status,
                record.sequence_count,
                record.total_bases,
                record.n50,
                f"{record.gc_percent:.4f}",
                " | ".join(record.errors),
            ])
    return path
