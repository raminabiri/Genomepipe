"""ENA download adapter.

This module builds ENA API/download plans. No network operation is performed
until ``download(..., execute=True)`` is explicitly called by the runner.
"""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


@dataclass(frozen=True)
class ENARequest:
    organism: str
    output_dir: Path
    assembly_levels: tuple[str, ...]


class ENA:
    source = "ena"

    def __init__(self, organism, output_dir, assembly_levels=()):
        self.request = ENARequest(
            organism=str(organism),
            output_dir=Path(output_dir),
            assembly_levels=tuple(assembly_levels),
        )

    def build_search_url(self):
        query = quote(f'"{self.request.organism}"')
        return (
            "https://www.ebi.ac.uk/ena/portal/api/search?"
            f"result=assembly&query=tax_tree({query})&format=tsv"
            "&fields=assembly_accession,scientific_name,assembly_level"
        )

    def plan(self):
        return {
            "source": self.source,
            "search_url": self.build_search_url(),
            "assembly_levels": list(self.request.assembly_levels),
            "output_dir": str(self.request.output_dir),
            "execute": False,
        }

    def download(self, execute=False):
        if not execute:
            return self.plan()
        raise NotImplementedError("ENA execution is enabled only through the pipeline runner.")
