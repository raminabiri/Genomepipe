from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class QualityAssessment:
    genome_id: str
    completeness: float | None
    contamination: float | None
    quality_label: str


def assess_quality(genome_id: str, completeness: float | None = None, contamination: float | None = None) -> QualityAssessment:
    if completeness is None or contamination is None:
        label = "PENDING"
    elif completeness >= 90 and contamination <= 5:
        label = "HIGH_QUALITY"
    else:
        label = "LOW_QUALITY"
    return QualityAssessment(genome_id, completeness, contamination, label)
