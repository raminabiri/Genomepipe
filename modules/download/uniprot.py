"""UniProt protein-sequence retrieval adapter."""

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen


class UniProt:
    source = "uniprot"

    def __init__(self, organism, output_dir):
        self.organism = str(organism)
        self.output_dir = Path(output_dir)

    def build_search_url(self):
        query = quote(f'organism_name:"{self.organism}"')
        return f"https://rest.uniprot.org/uniprotkb/search?query={query}&format=fasta"

    def plan(self):
        return {
            "source": self.source,
            "search_url": self.build_search_url(),
            "organism": self.organism,
            "output_dir": str(self.output_dir),
            "execute": False,
            "data_type": "protein_sequences",
        }

    def download(self, execute=False):
        if not execute:
            return self.plan()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out = self.output_dir / "uniprot_proteins.fasta"
        with urlopen(self.build_search_url(), timeout=300) as response:
            out.write_bytes(response.read())
        return out
