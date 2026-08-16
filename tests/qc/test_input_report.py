from pathlib import Path

from modules.qc.input_report import inspect_local_inputs


def test_local_input_inspection_returns_manifest(tmp_path: Path):
    (tmp_path / "g1.fasta").write_text(">g1\nATGC\n")
    report = inspect_local_inputs(tmp_path)
    assert report.valid
    assert report.manifest.count == 1


def test_local_input_inspection_reports_empty_files(tmp_path: Path):
    (tmp_path / "empty.fasta").touch()
    report = inspect_local_inputs(tmp_path)
    assert not report.valid
    assert any("Empty genome file" in error for error in report.errors)
