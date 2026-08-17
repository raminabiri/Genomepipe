from pathlib import Path

from modules.qc.input_manager_report import prepare_local_input_snapshot


def test_prepare_local_snapshot_writes_manifest_and_summary(tmp_path: Path):
    genome_root = tmp_path / "genomes"
    output_root = tmp_path / "qc"
    genome_root.mkdir()
    (genome_root / "g.fasta").write_text(">g\nATGC\n")
    inspection = prepare_local_input_snapshot(genome_root, output_root)
    assert inspection.valid
    assert (output_root / "genome_manifest.json").exists()
    assert (output_root / "genome_summary.tsv").exists()
