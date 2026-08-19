from pathlib import Path

from modules.qc.input_manager import GenomeInput
from modules.qc.qc_report import run_qc, write_qc_report


def test_qc_report(tmp_path: Path):
    fasta = tmp_path / "g.fasta"
    fasta.write_text(">g1\nATGCNN\n")
    records = run_qc((GenomeInput(fasta, "g1"),))
    assert records[0].status == "PASS"
    output = write_qc_report(records, tmp_path / "qc.tsv")
    assert output.exists()
    assert "PASS" in output.read_text(encoding="utf-8")
