from pathlib import Path

from modules.core.qc_pipeline import QCPipeline
from modules.qc.filtering import GenomeFilterCriteria
from modules.qc.input_manager import GenomeInput


def test_filter_accepts_passing_genome():
    fasta = Path("passing.fasta")
    fasta.write_text(">c1\nACGTACGT\n", encoding="utf-8")
    try:
        result = QCPipeline().process_genome(GenomeInput(fasta, "passing"))
        decisions = QCPipeline.filter_results((result,))
        assert decisions[0].accepted is True
    finally:
        fasta.unlink(missing_ok=True)


def test_filter_applies_explicit_thresholds(tmp_path: Path):
    fasta = tmp_path / "small.fasta"
    fasta.write_text(">c1\nACGT\n", encoding="utf-8")
    result = QCPipeline().process_genome(GenomeInput(fasta, fasta.stem))
    criteria = GenomeFilterCriteria(min_total_bases=10)
    decision = QCPipeline.filter_results((result,), criteria)[0]
    assert decision.accepted is False
    assert "total_bases_below_threshold" in decision.reasons


def test_filter_can_require_completeness_metrics(tmp_path: Path):
    fasta = tmp_path / "genome.fasta"
    fasta.write_text(">c1\nACGTACGT\n", encoding="utf-8")
    result = QCPipeline().process_genome(GenomeInput(fasta, fasta.stem))
    criteria = GenomeFilterCriteria(require_completeness_metrics=True)
    decision = QCPipeline.filter_results((result,), criteria)[0]
    assert decision.accepted is False
    assert "completeness_contamination_metrics_missing" in decision.reasons
