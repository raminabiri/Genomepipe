from pathlib import Path

from modules.qc.input_manager import GenomeInput
from modules.qc.standardize import standardize_genome_id


def test_genome_id_is_deterministically_standardized(tmp_path: Path):
    genome = GenomeInput(tmp_path / "x.fasta", "NCBI:abc/123")
    result = standardize_genome_id(genome)
    assert result.original == "NCBI:abc/123"
    assert result.standardized == "NCBI_abc_123"


def test_empty_identifier_gets_safe_fallback(tmp_path: Path):
    genome = GenomeInput(tmp_path / "x.fasta", "///")
    assert standardize_genome_id(genome).standardized == "genome"
