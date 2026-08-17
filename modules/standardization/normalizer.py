from dataclasses import dataclass
import re


@dataclass(frozen=True)
class GenomeIdentifier:
    original: str
    normalized: str


def normalize_genome_id(identifier: str) -> GenomeIdentifier:
    cleaned = identifier.strip()
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", cleaned)
    return GenomeIdentifier(identifier, cleaned)
