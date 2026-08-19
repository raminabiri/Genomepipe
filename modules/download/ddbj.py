"""DDBJ/INSDC sequence-source adapter.

DDBJ records are handled as accession-based sequence retrieval. The adapter
builds a retrieval plan and leaves network execution to the pipeline runner.
"""

from pathlib import Path


class DDBJ:
    source = "ddbj"

    def __init__(self, organism, output_dir, assembly_levels=()):
        self.organism = str(organism)
        self.output_dir = Path(output_dir)
        self.assembly_levels = tuple(assembly_levels)

    def plan(self):
        return {
            "source": self.source,
            "organism": self.organism,
            "assembly_levels": list(self.assembly_levels),
            "search_base": "https://getentry.ddbj.nig.ac.jp/getentry/",
            "output_dir": str(self.output_dir),
            "execute": False,
            "note": "DDBJ retrieval is accession-based; assembly classification is resolved from returned metadata.",
        }

    def download(self, execute=False):
        if not execute:
            return self.plan()
        raise NotImplementedError("DDBJ execution is enabled only through the pipeline runner.")
