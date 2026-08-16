from pathlib import Path

from modules.core.provenance import create_record, write_record


def test_provenance_record_contains_reproducibility_context(tmp_path: Path):
    record = create_record(
        "0.1.0", "qc", "1.0", [tmp_path / "genomes"],
        {"min_length": 1000}, [tmp_path / "qc.json"],
        project="demo", organism="Escherichia coli", data_mode="existing",
    )
    assert record.data_mode == "existing"
    assert record.organism == "Escherichia coli"
    assert record.outputs == (str(tmp_path / "qc.json"),)


def test_provenance_can_be_serialized(tmp_path: Path):
    record = create_record("0.1.0", "qc", "1.0", [])
    target = write_record(record, tmp_path / "provenance.json")
    assert target.exists()
    assert '"module": "qc"' in target.read_text(encoding="utf-8")
