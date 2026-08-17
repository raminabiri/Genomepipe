from hashlib import sha256
from pathlib import Path


def calculate_sha256(path: Path) -> str:
    """Return SHA256 checksum for a file."""
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
