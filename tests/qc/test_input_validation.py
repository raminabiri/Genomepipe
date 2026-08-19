from pathlib import Path

from modules.qc.input_manager import GenomeInput, GenomeInputManager
from modules.qc.input_validation import validate_fasta_file, validate_genomes


def test_valid_fasta(tmp_path: Path):
    path = tmp_path / "ok.fasta"
    path.write_text(">genome\nATGCNNRY\n")
    assert validate_fasta_file(path) == ()


def test_invalid_fasta_character(tmp_path: Path):
    path = tmp_path / "bad.fasta"
    path.write_text(">genome\nATGCZ\n")
    assert validate_fasta_file(path)


def test_missing_header(tmp_path: Path):
    path = tmp_path / "bad.fasta"
    path.write_text("ATGC\n")
    assert any("Missing FASTA header" in e for e in validate_fasta_file(path))


def test_validate_genomes_reports_by_id(tmp_path: Path):
    path = tmp_path / "bad.fasta"
    path.write_text(">g\nATGCZ\n")
    genome = GenomeInput(path, "bad")
    report = validate_genomes((genome,))
    assert "bad" in report


def test_manager_validation_does_not_read_non_genome_files(tmp_path: Path):
    (tmp_path / "notes.txt").write_text("not a fasta")
    manager = GenomeInputManager(tmp_path)
    assert manager.discover() == ()
