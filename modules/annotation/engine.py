"""Annotation engine design and job planning for Genomepipe Phase 3.1.

This layer is deliberately execution-free. It validates inputs, applies the
QC gate, resolves a tool profile, defines deterministic output locations, and
produces an executable command plan for Phase 3.2 wrappers.
"""

from dataclasses import dataclass
from pathlib import Path

from .qc_gate import AnnotationGateResult, qc_annotation_gate
from .tool_profiles import AnnotationToolProfile, get_tool_profile


@dataclass(frozen=True)
class AnnotationEngineConfig:
    tool: str
    output_root: Path
    cpus: int = 1
    organism: str | None = None
    prefix: str = "genome"

    def __post_init__(self) -> None:
        if self.cpus < 1:
            raise ValueError("cpus must be >= 1")
        if not self.prefix.strip():
            raise ValueError("prefix must not be empty")


@dataclass(frozen=True)
class AnnotationJobPlan:
    genome_id: str
    fasta: Path
    tool: AnnotationToolProfile
    output_dir: Path
    command: tuple[str, ...]
    gate: AnnotationGateResult


class AnnotationEngine:
    """Create deterministic annotation plans without invoking external tools."""

    VERSION = "3.1.0"

    def __init__(self, config: AnnotationEngineConfig):
        self.config = config
        self.profile = get_tool_profile(config.tool)

    def output_dir(self, genome_id: str) -> Path:
        return self.config.output_root / genome_id

    def plan(
        self,
        genome_id: str,
        fasta: Path,
        qc_passed: bool,
    ) -> AnnotationJobPlan:
        gate = qc_annotation_gate(genome_id, qc_passed)
        output_dir = self.output_dir(genome_id)
        command = self._build_command(genome_id, fasta, output_dir)
        return AnnotationJobPlan(
            genome_id=genome_id,
            fasta=fasta,
            tool=self.profile,
            output_dir=output_dir,
            command=command,
            gate=gate,
        )

    def _build_command(self, genome_id: str, fasta: Path, output_dir: Path) -> tuple[str, ...]:
        if self.profile.name == "prokka":
            command = [
                self.profile.executable,
                "--outdir", str(output_dir),
                "--prefix", f"{self.config.prefix}_{genome_id}",
                "--cpus", str(self.config.cpus),
                str(fasta),
            ]
            if self.config.organism:
                command.extend(["--genus", self.config.organism])
            return tuple(command)

        if self.profile.name == "bakta":
            command = [
                self.profile.executable,
                "--output", str(output_dir),
                "--prefix", f"{self.config.prefix}_{genome_id}",
                "--threads", str(self.config.cpus),
                str(fasta),
            ]
            return tuple(command)

        raise ValueError(f"No command builder registered for {self.profile.name}")
