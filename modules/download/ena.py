"""ENA assembly retrieval adapter."""

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen


class ENA:
    source = "ena"

    def __init__(self, organism, output_dir, assembly_levels=()):
        self.organism = str(organism)
        self.output_dir = Path(output_dir)
        self.assembly_levels = tuple(assembly_levels)

    def build_search_url(self):
        query = quote(f'"{self.organism}"')
        return (
            "https://www.ebi.ac.uk/ena/portal/api/search?"
            f"result=assembly&query=tax_tree({query})&format=tsv"
            "&fields=assembly_accession,scientific_name,assembly_level"
        )

    def plan(self):
        return {
            "source": self.source,
            "search_url": self.build_search_url(),
            "assembly_levels": list(self.assembly_levels),
            "output_dir": str(self.output_dir),
            "execute": False,
        }

    def download(self, execute=False):
        if not execute:
            return self.plan()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        metadata = self.output_dir / "ena_assemblies.tsv"
        with urlopen(self.build_search_url(), timeout=300) as response:
            metadata.write_bytes(response.read())
        return metadata
