from pathlib import Path

from modules.qc.metadata import read_genome_metadata


def test_reads_optional_local_metadata(tmp_path: Path):
    path = tmp_path / "metadata.csv"
    path.write_text(
        "genome_id,accession,organism,country\n"
        "g1,GCF_001,Escherichia coli,UK\n"
    )
    records = read_genome_metadata(path)
    assert len(records) == 1
    assert records[0].accession == "GCF_001"
    assert records[0].country == "UK"


def test_missing_metadata_is_optional(tmp_path: Path):
    assert read_genome_metadata(tmp_path / "missing.csv") == ()
