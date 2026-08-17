from pathlib import Path

from modules.qc.input_manager import GenomeInput
from modules.qc.manifest import build_manifest


def test_manifest_counts_and_serializes(tmp_path: Path):
    genomes = (
        GenomeInput(tmp_path / "a.fasta", "a"),
        GenomeInput(tmp_path / "b.fasta", "b"),
    )
    manifest = build_manifest(genomes)
    assert manifest.count == 2
    target = manifest.write_json(tmp_path / "manifest.json")
    assert target.exists()
    assert '"count": 2' in target.read_text(encoding="utf-8")
