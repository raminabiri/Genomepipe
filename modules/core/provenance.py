from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProvenanceRecord:
    pipeline_version: str
    module: str
    module_version: str
    timestamp_utc: str
    inputs: tuple[str, ...]
    parameters: dict[str, Any]


def create_record(
    pipeline_version: str,
    module: str,
    module_version: str,
    inputs: list[Path] | tuple[Path, ...],
    parameters: dict[str, Any] | None = None,
) -> ProvenanceRecord:
    return ProvenanceRecord(
        pipeline_version=pipeline_version,
        module=module,
        module_version=module_version,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        inputs=tuple(str(path) for path in inputs),
        parameters=parameters or {},
    )
