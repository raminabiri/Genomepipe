from dataclasses import dataclass


@dataclass(frozen=True)
class AnnotationGateResult:
    genome_id: str
    allowed: bool
    reason: str


def qc_annotation_gate(genome_id: str, qc_passed: bool) -> AnnotationGateResult:
    if qc_passed:
        return AnnotationGateResult(genome_id, True, "QC passed")
    return AnnotationGateResult(genome_id, False, "Genome failed QC; annotation blocked")
