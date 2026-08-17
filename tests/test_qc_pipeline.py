"""Tests for Phase 2.6 QC pipeline integration."""

from modules.core.qc_pipeline import QCPipeline


class MockStandardizer:
    def normalize(self, value):
        return "STD_" + value


class MockQC:
    pass


class MockProvenance:
    pass


def test_qc_pipeline_connects_modules():
    pipeline = QCPipeline(
        qc_module=MockQC(),
        standardizer=MockStandardizer(),
        provenance=MockProvenance(),
    )

    result = pipeline.run("genome_001")

    assert result.genome_id == "STD_genome_001"
    assert result.status == "READY_FOR_VALIDATION"
    assert result.steps == [
        "standardization",
        "qc_assessment",
        "provenance_record",
    ]
