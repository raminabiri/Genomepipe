from pathlib import Path

from modules.qc.input_manager import GenomeInput
from modules.qc.input_summary import summarize_genomes, write_summary_tsv


def test_summary_export(tmp_path: Path):
    fasta = tmp_path / "g.fasta"
    fasta.write_text(">c1\nGGCC\n")
    stats = summarize_genomes((GenomeInput(fasta, "g"),))
    output = write_summary_tsv(stats, tmp_path / "summary.tsv")
    text = output.read_text(encoding="utf-8")
    assert "genome_id" in text
    assert "g\t1\t4" in text
