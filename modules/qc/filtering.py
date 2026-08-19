"""Configurable genome filtering for Phase 2.7.

The filter is intentionally conservative: it never invents species-specific
thresholds. Callers provide thresholds appropriate to the organism/project.
"""

from dataclasses import dataclass

from .qc_report import GenomeQCRecord
from .quality_assessment import QualityAssessment


@dataclass(frozen=True)
class GenomeFilterCriteria:
    """Optional acceptance criteria for a genome QC result."""

    require_qc_pass: bool = True
    min_total_bases: int | None = None
    min_sequence_count: int | None = None
    max_sequence_count: int | None = None
    min_n50: int | None = None
    min_gc_percent: float | None = None
    max_gc_percent: float | None = None
    require_quality_label: str | None = None
    require_completeness: float | None = None
    max_contamination: float | None = None
    require_completeness_metrics: bool = False


@dataclass(frozen=True)
class GenomeFilterResult:
    genome_id: str
    accepted: bool
    reasons: tuple[str, ...] = ()


def filter_genome(
    qc: GenomeQCRecord,
    quality: QualityAssessment | None = None,
    criteria: GenomeFilterCriteria | None = None,
) -> GenomeFilterResult:
    criteria = criteria or GenomeFilterCriteria()
    reasons: list[str] = []

    if criteria.require_qc_pass and qc.status != "PASS":
        reasons.append("basic_qc_failed")

    if criteria.min_total_bases is not None and qc.total_bases < criteria.min_total_bases:
        reasons.append("total_bases_below_threshold")
    if criteria.min_sequence_count is not None and qc.sequence_count < criteria.min_sequence_count:
        reasons.append("sequence_count_below_threshold")
    if criteria.max_sequence_count is not None and qc.sequence_count > criteria.max_sequence_count:
        reasons.append("sequence_count_above_threshold")
    if criteria.min_n50 is not None and qc.n50 < criteria.min_n50:
        reasons.append("n50_below_threshold")
    if criteria.min_gc_percent is not None and qc.gc_percent < criteria.min_gc_percent:
        reasons.append("gc_below_threshold")
    if criteria.max_gc_percent is not None and qc.gc_percent > criteria.max_gc_percent:
        reasons.append("gc_above_threshold")

    if criteria.require_quality_label is not None:
        if quality is None or quality.quality_label != criteria.require_quality_label:
            reasons.append("quality_label_not_met")

    completeness = quality.completeness if quality else None
    contamination = quality.contamination if quality else None
    if criteria.require_completeness is not None:
        if completeness is None:
            reasons.append("completeness_missing")
        elif completeness < criteria.require_completeness:
            reasons.append("completeness_below_threshold")
    if criteria.max_contamination is not None:
        if contamination is None:
            reasons.append("contamination_missing")
        elif contamination > criteria.max_contamination:
            reasons.append("contamination_above_threshold")
    if criteria.require_completeness_metrics and (completeness is None or contamination is None):
        reasons.append("completeness_contamination_metrics_missing")

    return GenomeFilterResult(qc.genome_id, not reasons, tuple(reasons))
