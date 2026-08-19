"""Genomepipe Phase 2.7 - genome filtering and QC reporting.

This module orchestrates the local-genome QC path only. It deliberately has no
network/download dependency and never invokes a database downloader.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import csv

from modules.provenance.record import create_provenance_record, write_provenance
from modules.qc.checksums import sha256_file
from modules.qc.filtering import GenomeFilterCriteria, GenomeFilterResult, filter_genome
from modules.qc.input_manager import GenomeInput, GenomeInputManager
from modules.qc.qc_report import GenomeQCRecord, qc_genome
from modules.qc.quality_assessment import QualityAssessment, assess_quality
from modules.standardization.normalizer import normalize_genome_id


@dataclass(frozen=True)
class QCPipelineResult:
    genome_id: str
    status: str
    steps: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    qc_record: GenomeQCRecord | None = None
    quality_assessment: QualityAssessment | None = None
    checksum_sha256: str | None = None
    validation_errors: tuple[str, ...] = ()


class QCPipeline:
    """Coordinate local genome discovery, validation, standardization and QC."""

    VERSION = "2.7.0"

    def __init__(self, genome_root: Path | None = None):
        self.genome_root = Path(genome_root) if genome_root is not None else None

    def discover(self) -> tuple[GenomeInput, ...]:
        if self.genome_root is None:
            return ()
        return GenomeInputManager(self.genome_root).discover()

    def process_genome(self, genome: GenomeInput) -> QCPipelineResult:
        manager = GenomeInputManager(genome.path.parent)
        validation_errors = manager.validate((genome,))
        if validation_errors:
            return QCPipelineResult(
                genome_id=genome.genome_id,
                status="FAIL",
                steps=("input_validation",),
                metadata={"input_path": str(genome.path)},
                validation_errors=validation_errors,
            )

        steps: list[str] = ["input_validation"]
        normalized = normalize_genome_id(genome.genome_id)
        steps.append("standardization")

        standardized = GenomeInput(path=genome.path, genome_id=normalized.normalized)
        qc_record = qc_genome(standardized)
        steps.append("qc_assessment")

        checksum = sha256_file(standardized.path)
        steps.append("checksum")

        # Completeness/contamination require later external QC tools. Until
        # those metrics are supplied, the quality assessment remains PENDING.
        quality = assess_quality(standardized.genome_id)
        steps.append("quality_assessment")

        status = "PASS" if qc_record.status == "PASS" else "FAIL"
        return QCPipelineResult(
            genome_id=standardized.genome_id,
            status=status,
            steps=tuple(steps),
            metadata={
                "input_path": str(standardized.path),
                "original_genome_id": normalized.original,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            qc_record=qc_record,
            quality_assessment=quality,
            checksum_sha256=checksum,
        )

    def run(self, genomes: tuple[GenomeInput, ...] | None = None) -> tuple[QCPipelineResult, ...]:
        """Run the integrated QC path over already-available local genomes."""
        inputs = genomes if genomes is not None else self.discover()
        return tuple(self.process_genome(genome) for genome in inputs)

    @staticmethod
    def filter_results(
        results: tuple[QCPipelineResult, ...],
        criteria: GenomeFilterCriteria | None = None,
    ) -> tuple[GenomeFilterResult, ...]:
        """Apply configurable acceptance criteria to completed QC results."""
        criteria = criteria or GenomeFilterCriteria()
        filtered: list[GenomeFilterResult] = []
        for result in results:
            if result.qc_record is None:
                filtered.append(
                    GenomeFilterResult(result.genome_id, False, ("qc_result_missing",))
                )
                continue
            filtered.append(filter_genome(result.qc_record, result.quality_assessment, criteria))
        return tuple(filtered)

    def write_provenance(self, result: QCPipelineResult, output_dir: Path) -> Path:
        """Write a machine-readable provenance record for one successful QC result."""
        if result.qc_record is None or result.checksum_sha256 is None:
            raise ValueError("QC result is incomplete; provenance cannot be written")
        record = create_provenance_record(
            genome_id=result.genome_id,
            input_file=Path(result.metadata["input_path"]),
            stage="phase_2.7_qc_filtering",
            checksum=result.checksum_sha256,
            tool="Genomepipe",
            tool_version=self.VERSION,
            parameters={
                "steps": list(result.steps),
                "quality_label": result.quality_assessment.quality_label
                if result.quality_assessment else None,
            },
        )
        return write_provenance(record, output_dir / f"{result.genome_id}.provenance.json")

    @staticmethod
    def write_summary(
        results: tuple[QCPipelineResult, ...],
        output: Path,
        filter_results: tuple[GenomeFilterResult, ...] | None = None,
    ) -> Path:
        """Write the integrated QC and optional filtering summary."""
        output.parent.mkdir(parents=True, exist_ok=True)
        filter_by_id = {item.genome_id: item for item in (filter_results or ())}
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow([
                "genome_id", "status", "filter_status", "filter_reasons",
                "sequence_count", "total_bases", "N50", "GC_percent",
                "quality_label", "checksum_sha256", "errors",
            ])
            for result in results:
                qc = result.qc_record
                errors = result.validation_errors or (qc.errors if qc else ())
                decision = filter_by_id.get(result.genome_id)
                writer.writerow([
                    result.genome_id,
                    result.status,
                    "ACCEPT" if decision and decision.accepted else ("REJECT" if decision else "NOT_APPLIED"),
                    " | ".join(decision.reasons) if decision else "",
                    qc.sequence_count if qc else "",
                    qc.total_bases if qc else "",
                    qc.n50 if qc else "",
                    f"{qc.gc_percent:.4f}" if qc else "",
                    result.quality_assessment.quality_label if result.quality_assessment else "",
                    result.checksum_sha256 or "",
                    " | ".join(errors),
                ])
        return output
