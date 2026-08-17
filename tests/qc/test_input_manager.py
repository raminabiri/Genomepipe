from pathlib import Path

from modules.qc.input_manager import GenomeInputManager


def test_discovers_supported_genome_files(tmp_path: Path):
    (tmp_path / "a.fasta").write_text(">a\nATGC\n")
    (tmp_path / "b.fna").write_text(">b\nATGC\n")
    (tmp_path / "notes.txt").write_text("ignore")
    genomes = GenomeInputManager(tmp_path).discover()
    assert [g.genome_id for g in genomes] == ["a", "b"]


def test_missing_root_is_empty(tmp_path: Path):
    genomes = GenomeInputManager(tmp_path / "missing").discover()
    assert genomes == ()


def test_empty_file_is_reported(tmp_path: Path):
    (tmp_path / "empty.fasta").touch()
    errors = GenomeInputManager(tmp_path).validate()
    assert any("Empty genome file" in error for error in errors)
