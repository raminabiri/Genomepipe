from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class ProvenanceRecord:
    pipeline_version: str
    module: str
    module_version: str
    timestamp_utc: str
    inputs: tuple[str, ...]
    parameters: dict[str, Any]
    outputs: tuple[str, ...] = ()
    project: str | None = None
    organism: str | None = None
    data_mode: str | None = None


def create_record(
    pipeline_version: str,
    module: str,
    module_version: str,
    inputs: list[Path] | tuple[Path, ...],
    parameters: dict[str, Any] | None = None,
    outputs: list[Path] | tuple[Path, ...] = (),
    project: str | None = None,
    organism: str | None = None,
    data_mode: str | None = None,
) -> ProvenanceRecord:
    return ProvenanceRecord(
        pipeline_version=pipeline_version,
        module=module,
        module_version=module_version,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        inputs=tuple(str(path) for path in inputs),
        parameters=parameters or {},
        outputs=tuple(str(path) for path in outputs),
        project=project,
        organism=organism,
        data_mode=data_mode,
    )


def write_record(record: ProvenanceRecord, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(record), indent=2, sort_keys=True), encoding="utf-8")
    return path
