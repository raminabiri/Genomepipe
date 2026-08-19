from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import build_context
from .data_mode import require_existing_input
from .logging import configure_logging, get_logger
from modules.qc.input_manager import GenomeInputManager
from modules.qc.input_validation import validate_genomes
from modules.qc.qc_report import run_qc, write_qc_report


@dataclass(frozen=True)
class PipelineRunResult:
    project: str
    discovered: int
    valid: int
    qc_pass: int
    qc_fail: int


def run_existing_project(config_path: Path, limit: int | None = None) -> PipelineRunResult:
    context = build_context(config_path)
    input_root = require_existing_input(context)
    log_file = context.output_root / "logs" / "pipeline.log"
    configure_logging(log_file)
    logger = get_logger("runner")
    genome_root = input_root / "genomes"
    manager = GenomeInputManager(genome_root)
    genomes = manager.discover()
    if limit is not None:
        genomes = genomes[:limit]
    logger.info("Discovered %d local genome files", len(genomes))
    errors = validate_genomes(genomes)
    valid_genomes = tuple(genome for genome in genomes if genome.genome_id not in errors)
    records = run_qc(valid_genomes)
    write_qc_report(records, context.output_root / "qc" / "qc_report.tsv")
    result = PipelineRunResult(
        project=context.project_name,
        discovered=len(genomes),
        valid=len(valid_genomes),
        qc_pass=sum(record.status == "PASS" for record in records),
        qc_fail=sum(record.status == "FAIL" for record in records),
    )
    logger.info("Pipeline completed: %s", result)
    return result
