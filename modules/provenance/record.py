from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import json


@dataclass(frozen=True)
class ProvenanceRecord:
    genome_id: str
    input_file: str
    checksum: str | None = None
    stage: str = ""
    tool: str | None = None
    tool_version: str | None = None
    created_at: str = ""

    def to_dict(self):
        return asdict(self)


def create_provenance_record(genome_id: str, input_file: Path, stage: str, **kwargs) -> ProvenanceRecord:
    return ProvenanceRecord(
        genome_id=genome_id,
        input_file=str(input_file),
        stage=stage,
        created_at=datetime.now(timezone.utc).isoformat(),
        **kwargs,
    )


def write_provenance(record: ProvenanceRecord, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record.to_dict(), indent=2), encoding="utf-8")
    return output
