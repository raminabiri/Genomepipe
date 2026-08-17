from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnnotationConfig:
    tool: str
    output_root: Path
    cpus: int = 1


@dataclass(frozen=True)
class AnnotationInput:
    genome_id: str
    fasta: Path


class AnnotationManager:
    """Prepare annotation jobs without executing annotation tools."""

    SUPPORTED_TOOLS = {"prokka", "bakta"}

    def __init__(self, config: AnnotationConfig):
        if config.tool.lower() not in self.SUPPORTED_TOOLS:
            raise ValueError(f"Unsupported annotation tool: {config.tool}")
        self.config = config

    def output_dirs(self, genome_id: str) -> dict[str, Path]:
        root = self.config.output_root / genome_id
        return {
            "gff": root / "gff",
            "gbk": root / "gbk",
            "faa": root / "faa",
            "fna": root / "fna",
            "proteins": root / "proteins",
            "reports": root / "reports",
        }

    def create_job(self, genome: AnnotationInput) -> dict:
        return {
            "genome_id": genome.genome_id,
            "input_fasta": str(genome.fasta),
            "tool": self.config.tool.lower(),
            "cpus": self.config.cpus,
            "outputs": {k: str(v) for k, v in self.output_dirs(genome.genome_id).items()},
            "execute": False,
        }
