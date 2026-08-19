"""Genomepipe Phase 2.6 - QC pipeline integration.

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


class QCPipeline:
    """Coordinate local genome discovery, standardization, QC and provenance."""

    VERSION = "2.6.0"

    def __init__(self, genome_root: Path | None = None):
        self.genome_root = Path(genome_root) if genome_root is not None else None

    def discover(self) -> tuple[GenomeInput, ...]:
        if self.genome_root is None:
            return ()
        return GenomeInputManager(self.genome_root).discover()

    def process_genome(self, genome: GenomeInput) -> QCPipelineResult:
        steps: list[str] = ["input_discovery"]

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

    def write_provenance(self, result: QCPipelineResult, output_dir: Path) -> Path:
        """Write a machine-readable provenance record for one QC result."""
        if result.qc_record is None or result.checksum_sha256 is None:
            raise ValueError("QC result is incomplete; provenance cannot be written")
        record = create_provenance_record(
            genome_id=result.genome_id,
            input_file=Path(result.metadata["input_path"]),
            stage="phase_2.6_qc",
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
    def write_summary(results: tuple[QCPipelineResult, ...], output: Path) -> Path:
        """Write the integrated QC summary without requiring external tools."""
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t")
            writer.writerow([
                "genome_id", "status", "sequence_count", "total_bases",
                "N50", "GC_percent", "quality_label", "checksum_sha256", "errors",
            ])
            for result in results:
                qc = result.qc_record
                writer.writerow([
                    result.genome_id,
                    result.status,
                    qc.sequence_count if qc else "",
                    qc.total_bases if qc else "",
                    qc.n50 if qc else "",
                    f"{qc.gc_percent:.4f}" if qc else "",
                    result.quality_assessment.quality_label if result.quality_assessment else "",
                    result.checksum_sha256 or "",
                    " | ".join(qc.errors) if qc else "",
                ])
        return output
