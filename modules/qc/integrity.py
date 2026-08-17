from dataclasses import dataclass
from pathlib import Path

from .input_manager import GenomeInput

VALID_BASES = set("ACGTNRYSWKMBDHV")


@dataclass(frozen=True)
class FastaIntegrityResult:
    genome_id: str
    valid: bool
    sequence_count: int
    total_bases: int
    invalid_bases: int
    errors: tuple[str, ...] = ()


def validate_fasta_integrity(genome: GenomeInput) -> FastaIntegrityResult:
    errors: list[str] = []
    sequence_count = 0
    total_bases = 0
    invalid_bases = 0
    in_record = False

    try:
        with genome.path.open("r", encoding="utf-8") as handle:
            for line_number, raw in enumerate(handle, start=1):
                line = raw.strip()
                if not line:
                    continue
                if line.startswith(">"):
                    sequence_count += 1
                    in_record = True
                    if not line[1:].strip():
                        errors.append(f"Empty FASTA header at line {line_number}")
                    continue
                if not in_record:
                    errors.append(f"Sequence before FASTA header at line {line_number}")
                    continue
                sequence = line.upper()
                bad = sum(base not in VALID_BASES for base in sequence)
                invalid_bases += bad
                total_bases += len(sequence)

    except (OSError, UnicodeError) as exc:
        errors.append(f"Cannot read FASTA: {exc}")

    if sequence_count == 0:
        errors.append("No FASTA records found")
    if total_bases == 0:
        errors.append("No sequence bases found")
    if invalid_bases:
        errors.append(f"Found {invalid_bases} invalid nucleotide characters")

    return FastaIntegrityResult(
        genome_id=genome.genome_id,
        valid=not errors,
        sequence_count=sequence_count,
        total_bases=total_bases,
        invalid_bases=invalid_bases,
        errors=tuple(errors),
    )
