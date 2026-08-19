from pathlib import Path

import pytest

from modules.standardization.fasta_headers import normalize_fasta_headers
from modules.standardization.genome_id import normalize_genome_id


def test_genome_id_normalization_is_deterministic():
    result = normalize_genome_id("  Genome / 01:complete  ")
    assert result.original == "  Genome / 01:complete  "
    assert result.normalized == "Genome_01_complete"


def test_empty_genome_id_gets_safe_fallback():
    assert normalize_genome_id(" ... ").normalized == "unknown_genome"


def test_fasta_headers_are_normalized_without_modifying_input(tmp_path: Path):
    source = tmp_path / "input.fasta"
    output = tmp_path / "normalized.fasta"
    mapping = tmp_path / "header_map.tsv"
    original = ">NCBI accession 123|chromosome 1\nACGT\n>weird header/2\nGGCC\n"
    source.write_text(original, encoding="utf-8")

    records = normalize_fasta_headers(source, output, "Genome / 01", mapping)

    assert output.read_text(encoding="utf-8") == (
        ">Genome_01|contig_000001\nACGT\n>Genome_01|contig_000002\nGGCC\n"
    )
    assert source.read_text(encoding="utf-8") == original
    assert len(records) == 2
    assert records[0].original_header == "NCBI accession 123|chromosome 1"
    assert records[1].standardized_header == "Genome_01|contig_000002"
    assert mapping.read_text(encoding="utf-8").count("\n") == 3


def test_empty_fasta_header_is_rejected(tmp_path: Path):
    source = tmp_path / "bad.fasta"
    output = tmp_path / "normalized.fasta"
    source.write_text(">\nACGT\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Empty FASTA header"):
        normalize_fasta_headers(source, output, "genome1")
