from dataclasses import dataclass, asdict
from pathlib import Path
import json
from datetime import datetime, timezone


@dataclass(frozen=True)
class AnnotationManifest:
    genome_id: str
    input_file: str
    tool: str
    tool_version: str
    parameters: dict
    created_at: str


def create_annotation_manifest(genome_id: str, input_file: Path, tool: str, tool_version: str, parameters: dict) -> AnnotationManifest:
    return AnnotationManifest(
        genome_id=genome_id,
        input_file=str(input_file),
        tool=tool,
        tool_version=tool_version,
        parameters=parameters,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def save_annotation_manifest(manifest: AnnotationManifest, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(manifest), indent=2), encoding="utf-8")
