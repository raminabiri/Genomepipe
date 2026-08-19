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
            "sequence_api": "https://www.ebi.ac.uk/ena/browser/api/fasta/{accession}",
            "assembly_levels": list(self.assembly_levels),
            "output_dir": str(self.output_dir),
            "execute": False,
        }

    def _allowed(self, level):
        return not self.assembly_levels or level.strip().lower() in {
            x.lower().replace("_", " ") for x in self.assembly_levels
        }

    def download(self, execute=False):
        if not execute:
            return self.plan()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        metadata = self.output_dir / "ena_assemblies.tsv"
        with urlopen(self.build_search_url(), timeout=300) as response:
            metadata.write_bytes(response.read())

        rows = metadata.read_text(encoding="utf-8").splitlines()
        if not rows:
            return []
        header = rows[0].split("\t")
        acc_i = header.index("assembly_accession")
        level_i = header.index("assembly_level")
        outputs = []
        for row in rows[1:]:
            fields = row.split("\t")
            if len(fields) <= max(acc_i, level_i) or not self._allowed(fields[level_i]):
                continue
            accession = fields[acc_i]
            out = self.output_dir / f"{accession}.fna"
            url = f"https://www.ebi.ac.uk/ena/browser/api/fasta/{accession}"
            with urlopen(url, timeout=300) as response:
                out.write_bytes(response.read())
            outputs.append(out)
        return outputs
