"""Download-layer configuration and shared source definitions."""

DATABASES = (
    "ncbi",
    "ena",
    "gtdb",
    "bvbrc",
    "ddbj",
    "img",
    "sra",
    "uniprot",
)

ASSEMBLY_CHOICES = {
    "1": ("complete_genome",),
    "2": ("chromosome",),
    "3": ("scaffold",),
    "4": ("contig",),
    "5": ("complete_genome", "chromosome"),
    "6": ("complete_genome", "chromosome", "scaffold"),
}

DEFAULT_TIMEOUT = 300
DEFAULT_CHUNK_SIZE = 1024 * 1024
