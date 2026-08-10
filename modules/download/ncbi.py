from pathlib import Path
import subprocess
import zipfile

from .filter import GenomeFilter


class NCBI:

    def __init__(self, organism, genome_dir):

        self.organism = organism
        self.genome_dir = Path(genome_dir)

        self.metadata_file = self.genome_dir / "assembly_data_report.jsonl"
        self.archive = self.genome_dir / "ncbi_genomes.zip"

    def search(self):

        print(f"\nSearching: {self.organism}")


    def metadata(self):

        print("Getting NCBI metadata...")

        cmd = [
            "datasets",
            "summary",
            "genome",
            "taxon",
            self.organism,
            "--as-json-lines",
        ]

        with open(self.metadata_file, "w") as out:

            result = subprocess.run(
                cmd,
                stdout=out,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300,
            )

        if result.returncode != 0:
            print(result.stderr)
            raise RuntimeError("NCBI metadata failed")

        print("NCBI metadata finished")



    def download_batch(self):

        print("Download batch ...")

    def run(self):

        self.search()

        self.metadata()

        self.download_batch()
        print("STEP 1: after download_batch")

        gf = GenomeFilter(self.metadata_file)

        choice = input(
            "\nNCBI genome set:\n"
            "1. All genomes\n"
            "2. RefSeq genomes\n"
            "3. Complete genomes\n"
            "4. High quality genomes\n"
            "5. All genomes + all filtered datasets\n"
            "\nChoice: "
        )

        df = gf.load()
        print("STEP 2: metadata loaded", len(df))

        meta_dir = self.genome_dir.parent / "metadata"
        meta_dir.mkdir(exist_ok=True)

        df.to_csv(
            meta_dir / "metadata_all.csv",
            index=False,
        )

        df_refseq = gf.refseq(df)

        df_refseq.to_csv(
            meta_dir / "metadata_refseq.csv",
            index=False,
        )

        df_complete = gf.complete(df_refseq)

        df_complete.to_csv(
            meta_dir / "metadata_complete.csv",
            index=False,
        )

        df_hq = gf.high_quality(df_complete)
        print("STEP 3: filters done")

        df_hq.to_csv(
            meta_dir / "metadata_high_quality.csv",
            index=False,
        )

        download_dir = self.genome_dir.parent / "download"
        download_dir.mkdir(exist_ok=True)

        if choice == "1":

            accessions = df["accession"]

        elif choice == "2":

            accessions = df_refseq["accession"]

        elif choice == "3":

            accessions = df_complete["accession"]

        elif choice == "4":

            accessions = df_hq["accession"]

        elif choice == "5":

            accessions = df["accession"]

        else:

            print("\nInvalid choice.")
            return

        accessions.to_csv(
            download_dir / "accessions.txt",
            index=False,
            header=False,
        )

        download_root = download_dir / "genomes"                 
        download_root.mkdir(exist_ok=True)

        for acc in accessions:

            out = download_root / f"{acc}.zip"

            if out.exists() and zipfile.is_zipfile(out):
                print(f"Skip: {acc}")
                continue

            cmd = [
                "datasets",
                "download",
                "genome",
                "accession",
                acc,
                "--filename",
                str(out),
            ]

            print(f"Downloading {acc}")

            result = subprocess.run(cmd)

            if result.returncode != 0:

                print(f"Failed: {acc}")

                if out.exists():
                    out.unlink()

                continue

            if not zipfile.is_zipfile(out):

                print(f"Corrupted: {acc}")

                if out.exists():
                    out.unlink()

                continue

            print(f"Success: {acc}")

        print("\n========== DOWNLOAD SUMMARY ==========")
        print(f"Total genomes        : {len(df)}")
        print(f"RefSeq genomes       : {len(df_refseq)}")
        print(f"Complete genomes     : {len(df_complete)}")
        print(f"High quality genomes : {len(df_hq)}")
        print(f"Downloaded set       : {len(accessions)}")
        print("======================================")