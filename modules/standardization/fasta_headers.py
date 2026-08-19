"""Deterministic FASTA header standardization for Genomepipe.

Input FASTA files are never modified in place. A normalized FASTA and an
optional mapping table are written to caller-selected output paths.
"""

from dataclasses import dataclass
from pathlib import Path

from .normalizer import normalize_genome_id


@dataclass(frozen=True)
class HeaderMapping:
    genome_id: str
    contig_index: int
    original_header: str
    standardized_header: str


def normalize_fasta_headers(
    input_path: Path,
    output_path: Path,
    genome_id: str,
    mapping_path: Path | None = None,
) -> tuple[HeaderMapping, ...]:
    """Write a normalized FASTA and optionally a TSV mapping of old headers.

    Headers become ``>{genome_id}|contig_000001`` etc. Sequence content is
    preserved exactly apart from normalizing line endings and whitespace.
    Existing input files are never overwritten by this function.
    """
    normalized_id = normalize_genome_id(genome_id).normalized
    mappings: list[HeaderMapping] = []
    output_path.parent.mkdir(parents=True, exist_ok=True)

    record_index = 0
    seen_header = False
    with input_path.open("r", encoding="utf-8") as source, output_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as target:
        for line_number, raw in enumerate(source, start=1):
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                original = line[1:].strip()
                if not original:
                    raise ValueError(f"Empty FASTA header at line {line_number}")
                record_index += 1
                standardized = f">{normalized_id}|contig_{record_index:06d}"
                mappings.append(
                    HeaderMapping(
                        genome_id=normalized_id,
                        contig_index=record_index,
                        original_header=original,
                        standardized_header=standardized[1:],
                    )
                )
                target.write(standardized + "\n")
                seen_header = True
                continue
            if not seen_header:
                raise ValueError(f"Sequence data before FASTA header at line {line_number}")
            target.write(line + "\n")

    if not mappings:
        raise ValueError("No FASTA records found")

    if mapping_path is not None:
        mapping_path.parent.mkdir(parents=True, exist_ok=True)
        with mapping_path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write("genome_id\tcontig_index\toriginal_header\tstandardized_header\n")
            for mapping in mappings:
                handle.write(
                    f"{mapping.genome_id}\t{mapping.contig_index}\t"
                    f"{mapping.original_header}\t{mapping.standardized_header}\n"
                )

    return tuple(mappings)
