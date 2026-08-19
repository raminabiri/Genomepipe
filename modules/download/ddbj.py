"""DDBJ/INSDC accession retrieval adapter."""

from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen


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
            "search_base": "https://getentry.ddbj.nig.ac.jp/getentry",
            "output_dir": str(self.output_dir),
            "execute": False,
            "note": "DDBJ getentry is accession-based; accession discovery is a separate step.",
        }

    def download(self, execute=False, accessions=None):
        if not execute:
            return self.plan()
        if not accessions:
            raise ValueError("DDBJ execution requires one or more accessions.")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        outputs = []
        for accession in accessions:
            url = (
                "https://getentry.ddbj.nig.ac.jp/getentry?database=na&"
                f"accession_number={quote(str(accession))}&format=fasta"
            )
            out = self.output_dir / f"{accession}.fna"
            with urlopen(url, timeout=300) as response:
                out.write_bytes(response.read())
            outputs.append(out)
        return outputs
