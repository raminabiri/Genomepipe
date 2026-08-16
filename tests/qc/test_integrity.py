from pathlib import Path

from modules.qc.input_manager import GenomeInput
from modules.qc.integrity import validate_fasta_integrity


def test_valid_fasta(tmp_path: Path):
    path = tmp_path / "valid.fasta"
    path.write_text(">g1\nATGCNN\n")
    result = validate_fasta_integrity(GenomeInput(path, "g1"))
    assert result.valid
    assert result.sequence_count == 1
    assert result.total_bases == 6
    assert result.invalid_bases == 0


def test_invalid_base_is_reported(tmp_path: Path):
    path = tmp_path / "bad.fasta"
    path.write_text(">g1\nATGX\n")
    result = validate_fasta_integrity(GenomeInput(path, "g1"))
    assert not result.valid
    assert result.invalid_bases == 1


def test_sequence_without_header_is_reported(tmp_path: Path):
    path = tmp_path / "bad.fasta"
    path.write_text("ATGC\n")
    result = validate_fasta_integrity(GenomeInput(path, "g1"))
    assert not result.valid
