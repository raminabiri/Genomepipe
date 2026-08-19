from dataclasses import dataclass
from pathlib import Path
import csv


@dataclass(frozen=True)
class GenomeMetadata:
    genome_id: str
    accession: str | None = None
    organism: str | None = None
    source: str | None = None
    collection_date: str | None = None
    country: str | None = None


def read_genome_metadata(path: Path) -> tuple[GenomeMetadata, ...]:
    """Read optional local genome metadata; never contacts external databases."""
    if not path.exists():
        return ()
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return tuple(
            GenomeMetadata(
                genome_id=(row.get("genome_id") or "").strip(),
                accession=(row.get("accession") or None),
                organism=(row.get("organism") or None),
                source=(row.get("source") or None),
                collection_date=(row.get("collection_date") or None),
                country=(row.get("country") or None),
            )
            for row in reader
            if (row.get("genome_id") or "").strip()
        )
