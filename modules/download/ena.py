from pathlib import Path
import requests
import pandas as pd


class ENA:

    API = "https://www.ebi.ac.uk/ena/portal/api"
    TAXONOMY_API = "https://www.ebi.ac.uk/ena/taxonomy/rest"

    def __init__(self, organism, genome_dir):

        self.organism = organism
        self.genome_dir = Path(genome_dir)

        self.ena_dir = self.genome_dir.parent / "ena"
        self.genome_output = self.ena_dir / "genomes"
        self.metadata_dir = self.ena_dir / "metadata"

        self.genome_output.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.metadata_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def get_taxid(self):

        print(f"\nENA taxonomy search: {self.organism}")

        url = (
            f"{self.TAXONOMY_API}"
            f"/scientific-name/{self.organism}"
        )

        response = requests.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            raise RuntimeError(
                f"ENA taxonomy not found: {self.organism}"
            )

        return str(data[0]["taxId"])


    def search(self):

        output = (
            self.metadata_dir /
            "ena_assemblies.tsv"
        )

        # -------------------------------------------------
        # Use existing metadata if available
        # -------------------------------------------------

        if output.exists() and output.stat().st_size > 0:

            print(
                f"\nUsing existing ENA metadata: {output}"
            )

            return pd.read_csv(
                output,
                sep="\t",
            )

        # -------------------------------------------------
        # Query ENA only if metadata does not exist
        # -------------------------------------------------

        taxid = self.get_taxid()

        print(f"ENA taxid: {taxid}")
        print("Searching ENA assemblies ...")

        url = f"{self.API}/search"

        params = {
            "result": "assembly",
            "query": f"tax_eq({taxid})",
            "format": "tsv",
            "fields": (
                "accession,"
                "scientific_name,"
                "tax_id,"
                "assembly_name,"
                "assembly_level"
            ),
            "limit": 0,
        }

        response = requests.get(
            url,
            params=params,
            timeout=120,
        )

        response.raise_for_status()

        output.write_text(
            response.text,
            encoding="utf-8",
        )

        print(
            f"ENA metadata saved: {output}"
        )

        return pd.read_csv(
            output,
            sep="\t",
        )


    def download(self, accessions):

        accessions = list(accessions)

        print(
            f"\nENA genomes to download: "
            f"{len(accessions)}"
        )

        downloaded = 0
        skipped = 0
        failed = 0

        for accession in accessions:

            output = (
                self.genome_output /
                f"{accession}.fasta"
            )

            if (
                output.exists()
                and output.stat().st_size > 0
            ):

                print(
                    f"Skip existing: {accession}"
                )

                skipped += 1
                continue

            url = (
                "https://www.ebi.ac.uk/"
                "ena/browser/api/fasta/"
                f"{accession}"
            )

            print(
                f"Downloading: {accession}"
            )

            try:

                response = requests.get(
                    url,
                    timeout=120,
                )

                response.raise_for_status()

                if not response.text.startswith(">"):

                    print(
                        f"Invalid FASTA: {accession}"
                    )

                    failed += 1
                    continue

                output.write_text(
                    response.text,
                    encoding="utf-8",
                )

                downloaded += 1

            except Exception as e:

                print(
                    f"Failed: {accession}"
                )

                print(
                    f"Reason: {e}"
                )

                if output.exists():
                    output.unlink()

                failed += 1

        print(
            "\n========== ENA DOWNLOAD SUMMARY =========="
        )

        print(
            f"Requested : {len(accessions)}"
        )

        print(
            f"Downloaded: {downloaded}"
        )

        print(
            f"Skipped   : {skipped}"
        )

        print(
            f"Failed    : {failed}"
        )

        print(
            "=========================================="
        )

    def run(self):

        df = self.search()

        return df
