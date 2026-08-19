"""NCBI Datasets genome downloader.

The downloader is fully parameterized but is only executed when the top-level
runner explicitly enables execution. Assembly choices follow the NCBI Datasets
CLI: complete, chromosome, scaffold and contig. NCBI supports comma-separated
assembly levels, which maps directly to the six Genomepipe choices.
"""

from pathlib import Path
import subprocess
import zipfile

from .filter import GenomeFilter
from .config import ASSEMBLY_CHOICES


class NCBI:
    source = "ncbi"

    def __init__(self, organism, genome_dir, assembly_levels=(), assembly_source="all"):
        self.organism = str(organism)
        self.genome_dir = Path(genome_dir)
        self.assembly_levels = tuple(assembly_levels)
        self.assembly_source = assembly_source
        self.metadata_file = self.genome_dir / "assembly_data_report.jsonl"

    def build_summary_command(self):
        cmd = ["datasets", "summary", "genome", "taxon", self.organism,
               "--as-json-lines", "--limit", "all"]
        if self.assembly_levels:
            cmd += ["--assembly-level", ",".join(self.assembly_levels)]
        if self.assembly_source != "all":
            cmd += ["--assembly-source", self.assembly_source]
        return cmd

    def build_download_command(self, output_zip):
        cmd = [
            "datasets", "download", "genome", "taxon", self.organism,
            "--filename", str(output_zip),
            "--dehydrated",
            "--include", "genome",
        ]
        if self.assembly_levels:
            cmd += ["--assembly-level", ",".join(self.assembly_levels)]
        if self.assembly_source != "all":
            cmd += ["--assembly-source", self.assembly_source]
        return cmd

    def plan(self):
        return {
            "source": self.source,
            "organism": self.organism,
            "assembly_levels": list(self.assembly_levels),
            "assembly_source": self.assembly_source,
            "summary_command": self.build_summary_command(),
            "output_dir": str(self.genome_dir),
            "execute": False,
        }

    def metadata(self):
        self.genome_dir.mkdir(parents=True, exist_ok=True)
        cmd = self.build_summary_command()
        with self.metadata_file.open("w", encoding="utf-8") as out:
            result = subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE,
                                    text=True, timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"NCBI metadata failed: {result.stderr.strip()}")
        return self.metadata_file

    def download(self, execute=False):
        if not execute:
            return self.plan()

        self.genome_dir.mkdir(parents=True, exist_ok=True)
        output_zip = self.genome_dir / "ncbi_genomes.zip"
        cmd = self.build_download_command(output_zip)
        result = subprocess.run(cmd, text=True)
        if result.returncode != 0:
            raise RuntimeError("NCBI genome download failed")
        if not zipfile.is_zipfile(output_zip):
            raise RuntimeError("NCBI returned an invalid genome package")
        return output_zip

    def run(self, execute=False):
        if not execute:
            return self.plan()
        self.metadata()
        return self.download(execute=True)

    @staticmethod
    def assembly_levels_from_choice(choice):
        if choice not in ASSEMBLY_CHOICES:
            raise ValueError(f"Invalid assembly choice: {choice}")
        return ASSEMBLY_CHOICES[choice]
