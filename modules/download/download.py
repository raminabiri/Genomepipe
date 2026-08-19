from .helper import read_config
from .ncbi import NCBI
from .ena import ENA
from .deduplicate import GenomeDeduplicator
from pathlib import Path


def run(project_path):

    print(">>> DOWNLOAD RUN STARTED <<<")

    config = read_config(
        project_path / "config" / "project.yaml"
    )

    organism = config["project"]["organism"]
    genome_dir = Path(
        config["input"]["genomes"]
    )

    genome_dir = config["input"]["genomes"]
    genome_dir = Path(genome_dir)
    print()

    use_existing = input(
        "Use existing genomes? (y/n): "
    ).lower()

    if use_existing == "y":

        print("Using existing genomes.")

        return

    print("\nDatabases:\n")

    sources = []

    if input("NCBI (y/n): ").lower() == "y":
        sources.append("ncbi")

    if input("ENA (y/n): ").lower() == "y":
        sources.append("ena")

    if input("GTDB (y/n): ").lower() == "y":
        sources.append("gtdb")

    if input("UniProt (y/n): ").lower() == "y":
        sources.append("uniprot")

    if input("SRA (y/n): ").lower() == "y":
        sources.append("sra")

    if input("DDBJ (y/n): ").lower() == "y":
        sources.append("ddbj")

    if input("BV-BRC (y/n): ").lower() == "y":
        sources.append("bvbrc")

    if input("IMG (y/n): ").lower() == "y":
        sources.append("img")

    print("\nSelected databases:")
    print(sources)

    dry_run = input(
        "\nDry run? (y/n): "
    ).lower() == "y"

    if dry_run:
        print("\n*** DRY RUN MODE ***")
        print("No genomes will be downloaded.")


    # -------------------------------------------------
    # NCBI
    # -------------------------------------------------

    if "ncbi" in sources:

        ncbi = NCBI(
            organism,
            genome_dir,
        )

        ncbi.run()

    # -------------------------------------------------
    # ENA
    # -------------------------------------------------

    if "ena" in sources:

        ena = ENA(
            organism,
            genome_dir,
        )

        ena_df = ena.search()

        ena_metadata = (
            genome_dir.parent
            / "ena"
            / "metadata"
            / "ena_assemblies.tsv"
        )

        ncbi_metadata = (
            genome_dir.parent
            / "metadata"
            / "metadata_all.csv"
        )

        # If NCBI was not selected, we cannot perform
        # NCBI ↔ ENA deduplication.
        if "ncbi" in sources:

            deduplicator = GenomeDeduplicator(
                ncbi_metadata,
                ena_metadata,
            )

            ena_unique = deduplicator.run()


        else:

            print(
                "\nNCBI not selected for this run."
            )

            if ncbi_metadata.exists():

                print(
                    "Using existing NCBI metadata "
                    "for cross-database deduplication."
                )

                deduplicator = GenomeDeduplicator(
                    ncbi_metadata,
                    ena_metadata,
                )

                ena_unique = deduplicator.run()

            else:

                print(
                    "No NCBI metadata found."
                )

                print(
                    "Using ENA internal unique assemblies only."
                )

                ena_unique = ena_df.drop_duplicates(
                    subset=["accession"]
                )



        # -------------------------------------------------
        # ENA selection
        # -------------------------------------------------

        print(
            "\nENA genome set:"
        )

        print(
            "1. All assemblies"
        )

        print(
            "2. Complete genome"
        )

        print(
            "3. Chromosome"
        )

        print(
            "4. Scaffold"
        )

        print(
            "5. Contig"
        )

        print(
            "6. Complete genome + Chromosome"
        )

        print(
            "7. Complete genome + Chromosome + Scaffold"
        )

        choice = input(
            "\nChoice: "
        )

        if choice == "1":

            selected = ena_unique

        elif choice == "2":

            selected = ena_unique[
                ena_unique["assembly_level"]
                .str.lower()
                == "complete genome"
            ]

        elif choice == "3":

            selected = ena_unique[
                ena_unique["assembly_level"]
                .str.lower()
                == "chromosome"
            ]

        elif choice == "4":

            selected = ena_unique[
                ena_unique["assembly_level"]
                .str.lower()
                == "scaffold"
            ]

        elif choice == "5":

            selected = ena_unique[
                ena_unique["assembly_level"]
                .str.lower()
                == "contig"
            ]

        elif choice == "6":

            selected = ena_unique[
                ena_unique["assembly_level"]
                .str.lower()
                .isin([
                    "complete genome",
                    "chromosome",
                ])
            ]

        elif choice == "7":

            selected = ena_unique[
                ena_unique["assembly_level"]
                .str.lower()
                .isin([
                    "complete genome",
                    "chromosome",
                    "scaffold",
                ])
            ]

        else:

            print(
                "\nInvalid ENA choice."
            )

            return

        selected = selected.copy()

        accessions_file = (
            genome_dir.parent
            / "ena"
            / "accessions.txt"
        )

        selected["accession"].to_csv(
            accessions_file,
            index=False,
            header=False,
        )

        print(
            "\n========== ENA SELECTION =========="
        )

        print(
            f"ENA original       : {len(ena_df)}"
        )

        print(
            f"ENA selected       : {len(selected)}"
        )

        print(
            f"ENA accessions file: {accessions_file}"
        )

        print(
            "==================================="
        )

        # -------------------------------------------------
        # Download only after deduplication + filtering
        # -------------------------------------------------

        if dry_run:

            print(
                "\n*** DRY RUN: ENA download skipped ***"
            )

        else:

            ena.download(
                selected["accession"]
            )
    return dry_run