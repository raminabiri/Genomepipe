from pathlib import Path

from modules.qc.input_manager import GenomeInput
from modules.qc.input_snapshot import create_snapshot


def test_snapshot_records_local_file_identity(tmp_path: Path):
    fasta = tmp_path / "g.fasta"
    fasta.write_text(">g\nATGC\n")
    snapshot = create_snapshot((GenomeInput(fasta, "g"),))
    assert len(snapshot) == 1
    assert snapshot[0].genome_id == "g"
    assert snapshot[0].size_bytes == fasta.stat().st_size
    assert len(snapshot[0].sha256) == 64
