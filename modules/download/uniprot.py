"""UniProt protein-sequence data-source adapter.

UniProt is a protein database, not an assembly repository. It is therefore
kept as a complementary source and is not mapped to assembly-level choices.
"""

from pathlib import Path
from urllib.parse import quote


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
        raise NotImplementedError("UniProt execution is enabled only through the pipeline runner.")
