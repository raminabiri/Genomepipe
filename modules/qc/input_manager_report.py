from pathlib import Path

from .input_manager import GenomeInputManager
from .manifest import build_manifest
from .input_report import InputInspection, inspect_local_inputs
from .sequence_stats import calculate_sequence_stats
from .input_summary import write_summary_tsv


def prepare_local_input_snapshot(genome_root: Path, output_root: Path) -> InputInspection:
    """Inspect local genomes and persist a deterministic input snapshot."""
    inspection = inspect_local_inputs(genome_root)
    if inspection.valid:
        manifest = build_manifest(inspection.genomes)
        manifest.write_json(output_root / "genome_manifest.json")
        stats = tuple(calculate_sequence_stats(genome) for genome in inspection.genomes)
        write_summary_tsv(stats, output_root / "genome_summary.tsv")
    return inspection
