from pathlib import Path

from modules.qc.checksums import sha256_file
from modules.qc.duplicates import find_duplicate_files_by_size, find_duplicate_genome_ids
from modules.qc.input_manager import GenomeInput


def test_duplicate_ids_are_reported(tmp_path: Path):
    genomes = (
        GenomeInput(tmp_path / "a.fasta", "same"),
        GenomeInput(tmp_path / "nested" / "a.fasta", "same"),
    )
    assert find_duplicate_genome_ids(genomes) == ("same",)


def test_same_size_is_only_a_candidate(tmp_path: Path):
    a = tmp_path / "a.fasta"
    b = tmp_path / "b.fasta"
    a.write_text(">a\nAAAA\n")
    b.write_text(">b\nTTTT\n")
    groups = find_duplicate_files_by_size((GenomeInput(a, "a"), GenomeInput(b, "b")))
    assert len(groups) == 1
    assert sha256_file(a) != sha256_file(b)
