"""BV-BRC genome-sequence retrieval adapter."""

import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


class BVBRC:
    source = "bvbrc"

    def __init__(self, organism, output_dir, assembly_levels=()):
        self.organism = str(organism)
        self.output_dir = Path(output_dir)
        self.assembly_levels = tuple(assembly_levels)

    def build_query_url(self):
        query = quote(f'eq(genome_name,{self.organism})')
        return f"https://www.bv-brc.org/api/genome/?{query}&http_accept=application/json"

    def plan(self):
        return {
            "source": self.source,
            "search_url": self.build_query_url(),
            "sequence_endpoint": "https://www.bv-brc.org/api/genome_sequence/",
            "assembly_levels": list(self.assembly_levels),
            "output_dir": str(self.output_dir),
            "execute": False,
        }

    @staticmethod
    def _get(url, accept="application/json"):
        request = Request(url, headers={"Accept": accept})
        with urlopen(request, timeout=300) as response:
            return response.read()

    def download(self, execute=False):
        if not execute:
            return self.plan()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        payload = json.loads(self._get(self.build_query_url()).decode("utf-8"))
        genomes = payload if isinstance(payload, list) else payload.get("results", payload)
        outputs = []
        for genome in genomes:
            genome_id = genome.get("genome_id")
            if not genome_id:
                continue
            query = quote(f'eq(genome_id,{genome_id})')
            url = (
                "https://www.bv-brc.org/api/genome_sequence/?"
                f"{query}&http_accept=application/dna+fasta"
            )
            out = self.output_dir / f"{genome_id}.fna"
            out.write_bytes(self._get(url, "application/dna+fasta"))
            outputs.append(out)
        return outputs


# Backward-compatible spelling.
BVBRc = BVBRC
