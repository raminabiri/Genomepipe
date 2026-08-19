from pathlib import Path

from modules.core.qc_pipeline import QCPipeline
from modules.qc.input_manager import GenomeInput


def test_qc_pipeline_processes_local_fasta(tmp_path: Path):
    fasta = tmp_path / "Genome 01.fasta"
    fasta.write_text(">contig1\nACGTACGT\n>contig2\nGGCC\n", encoding="utf-8")

    result = QCPipeline().process_genome(GenomeInput(fasta, fasta.stem))

    assert result.genome_id == "Genome_01"
    assert result.status == "PASS"
    assert result.qc_record is not None
    assert result.qc_record.sequence_count == 2
    assert result.qc_record.total_bases == 12
    assert result.qc_record.n50 == 8
    assert result.quality_assessment is not None
    assert result.quality_assessment.quality_label == "PENDING"
    assert result.checksum_sha256 is not None


def test_qc_pipeline_rejects_invalid_fasta(tmp_path: Path):
    fasta = tmp_path / "bad.fasta"
    fasta.write_text(">contig1\nACGTX\n", encoding="utf-8")

    result = QCPipeline().process_genome(GenomeInput(fasta, fasta.stem))

    assert result.status == "FAIL"
    assert result.qc_record is not None
    assert result.qc_record.invalid_bases == 1
    assert result.qc_record.errors


def test_qc_pipeline_discovers_local_genomes(tmp_path: Path):
    (tmp_path / "a.fna").write_text(">a\nACGT\n", encoding="utf-8")
    (tmp_path / "b.fasta").write_text(">b\nGGCC\n", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not a genome", encoding="utf-8")

    genomes = QCPipeline(tmp_path).discover()

    assert [genome.genome_id for genome in genomes] == ["a", "b"]


def test_qc_pipeline_writes_provenance(tmp_path: Path):
    fasta = tmp_path / "genome.fasta"
    fasta.write_text(">contig1\nACGTACGT\n", encoding="utf-8")

    pipeline = QCPipeline()
    result = pipeline.process_genome(GenomeInput(fasta, fasta.stem))
    provenance = pipeline.write_provenance(result, tmp_path / "provenance")

    assert provenance.exists()
    text = provenance.read_text(encoding="utf-8")
    assert '"stage": "phase_2.6_qc"' in text
    assert result.checksum_sha256 in text
