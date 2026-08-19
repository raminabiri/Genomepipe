"""Genomepipe Phase 2.6 - QC pipeline integration.

This module orchestrates the local-genome QC path only. It deliberately has no
network/download dependency and never invokes a database downloader.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    """Coordinate local genome discovery, standardization, QC and provenance data.

    The class is intentionally dependency-light. It can operate on one existing
    FASTA file or on a local genome directory and does not download data.
    """

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
