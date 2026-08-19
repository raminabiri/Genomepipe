from dataclasses import dataclass
import re


@dataclass(frozen=True)
class GenomeIdentifier:
    original: str
    normalized: str


def normalize_genome_id(identifier: str) -> GenomeIdentifier:
    """Return a deterministic, filesystem/tool-safe genome identifier."""
    original = identifier
    cleaned = identifier.strip()
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", cleaned)
    cleaned = cleaned.strip("._-")
    return GenomeIdentifier(original, cleaned or "unknown_genome")
