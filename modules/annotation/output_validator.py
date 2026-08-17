from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnnotationValidationResult:
    genome_id: str
    valid: bool
    missing_files: tuple[str, ...] = ()


REQUIRED_ANNOTATION_FILES = ("gff", "gbk", "faa", "fna")


def validate_annotation_output(genome_id: str, output_dir: Path) -> AnnotationValidationResult:
    missing = tuple(
        extension
        for extension in REQUIRED_ANNOTATION_FILES
        if not list(output_dir.glob(f"*.{extension}"))
    )
    return AnnotationValidationResult(
        genome_id=genome_id,
        valid=not missing,
        missing_files=missing,
    )
