from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnnotationJob:
    genome_id: str
    fasta: Path
    tool: str
    output_dir: Path


def prepare_annotation_jobs(genomes: tuple[tuple[str, Path], ...], tool: str, output_root: Path) -> tuple[AnnotationJob, ...]:
    return tuple(
        AnnotationJob(
            genome_id=genome_id,
            fasta=fasta,
            tool=tool,
            output_dir=output_root / genome_id,
        )
        for genome_id, fasta in genomes
    )
