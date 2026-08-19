"""NCBI SRA read-data adapter.

SRA stores raw sequencing reads rather than genome assemblies. Execution uses
SRA Toolkit and therefore requires run/BioProject accessions.
"""

from pathlib import Path
import subprocess


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
            "note": "SRA execution requires run or BioProject accessions; it is not an assembly download.",
        }

    def download(self, execute=False, accessions=None):
        if not execute:
            return self.plan()
        if not accessions:
            raise ValueError("SRA execution requires one or more run/BioProject accessions.")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        results = []
        for accession in accessions:
            prefetch = subprocess.run(
                ["prefetch", str(accession), "--output-directory", str(self.output_dir)],
                text=True,
            )
            if prefetch.returncode != 0:
                raise RuntimeError(f"prefetch failed for {accession}")
            fasterq = subprocess.run(
                ["fasterq-dump", str(accession), "--outdir", str(self.output_dir)],
                text=True,
            )
            if fasterq.returncode != 0:
                raise RuntimeError(f"fasterq-dump failed for {accession}")
            results.append(accession)
        return results
