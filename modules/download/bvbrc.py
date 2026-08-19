"""BV-BRC genome download adapter."""

from pathlib import Path
from urllib.parse import quote


class BVBRc:
    source = "bvbrc"

    def __init__(self, organism, output_dir, assembly_levels=()):
        self.organism = str(organism)
        self.output_dir = Path(output_dir)
        self.assembly_levels = tuple(assembly_levels)

    def build_query_url(self):
        query = quote(f'eq(genome_name,{self.organism})')
        return f"https://www.bv-brc.org/api/genome/?{query}&http_accept=text/tsv"

    def plan(self):
        return {
            "source": self.source,
            "search_url": self.build_query_url(),
            "sequence_endpoint": "https://www.bv-brc.org/api/genome_sequence/",
            "assembly_levels": list(self.assembly_levels),
            "output_dir": str(self.output_dir),
            "execute": False,
        }

    def download(self, execute=False):
        if not execute:
            return self.plan()
        raise NotImplementedError("BV-BRC execution is enabled only through the pipeline runner.")


# Backward-compatible spelling.
BVBRC = BVBRc
