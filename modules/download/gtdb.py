"""GTDB download adapter.

GTDB distributes release datasets through its data site. This adapter keeps
release selection separate from execution and never downloads on import.
"""

from pathlib import Path


class GTDB:
    source = "gtdb"

    def __init__(self, organism, output_dir, assembly_levels=(), release="latest"):
        self.organism = str(organism)
        self.output_dir = Path(output_dir)
        self.assembly_levels = tuple(assembly_levels)
        self.release = release

    def plan(self):
        return {
            "source": self.source,
            "release": self.release,
            "organism": self.organism,
            "assembly_levels": list(self.assembly_levels),
            "catalog_url": f"https://data.gtdb.ecogenomic.org/releases/{self.release}/",
            "output_dir": str(self.output_dir),
            "execute": False,
            "note": "GTDB is release-oriented; assembly-level filtering is applied after catalog metadata is resolved.",
        }

    def download(self, execute=False):
        if not execute:
            return self.plan()
        raise NotImplementedError("GTDB execution is enabled only through the pipeline runner.")
