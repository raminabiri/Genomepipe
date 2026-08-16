from dataclasses import asdict, dataclass
from pathlib import Path
import json

from .input_manager import GenomeInput


@dataclass(frozen=True)
class GenomeManifest:
    genomes: tuple[GenomeInput, ...]

    @property
    def count(self) -> int:
        return len(self.genomes)

    def to_dict(self) -> dict:
        return {
            "count": self.count,
            "genomes": [
                {"genome_id": g.genome_id, "path": str(g.path)}
                for g in self.genomes
            ],
        }

    def write_json(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path


def build_manifest(genomes: tuple[GenomeInput, ...]) -> GenomeManifest:
    return GenomeManifest(genomes=genomes)
