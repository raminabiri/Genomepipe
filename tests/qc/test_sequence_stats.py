from pathlib import Path

from modules.qc.input_manager import GenomeInput
from modules.qc.sequence_stats import calculate_sequence_stats


def test_sequence_statistics(tmp_path: Path):
    fasta = tmp_path / "g.fasta"
    fasta.write_text(">c1\nGGCC\n>c2\nAAAA\n")
    stats = calculate_sequence_stats(GenomeInput(fasta, "g"))
    assert stats.sequence_count == 2
    assert stats.total_bases == 8
    assert stats.min_length == 4
    assert stats.max_length == 4
    assert stats.n50 == 4
    assert stats.gc_percent == 50.0
