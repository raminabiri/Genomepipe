"""NCBI SRA read-data adapter.

SRA provides sequencing reads rather than assembled genome records. It is kept
in the download layer as a complementary source and is intentionally not
subject to the six assembly-level options.
"""

from pathlib import Path


class SRA:
    source = "sra"

    def __init__(self, organism, output_dir):
        self.organism = str(organism)
        self.output_dir = Path(output_dir)

    def plan(self):
        return {
            "source": self.source,
            "organism": self.organism,
            "tool": "sra-tools",
            "output_dir": str(self.output_dir),
            "execute": False,
            "data_type": "raw_reads",
            "note": "SRA is a read archive, not an assembly database.",
        }

    def download(self, execute=False):
        if not execute:
            return self.plan()
        raise NotImplementedError("SRA execution is enabled only through the pipeline runner.")
