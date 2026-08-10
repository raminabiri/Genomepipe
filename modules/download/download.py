from .helper import read_config
from .ncbi import NCBI


def run(project_path):
    
    print(">>> DOWNLOAD RUN STARTED <<<")

    config = read_config(project_path / "config" / "project.yaml")

    organism = config["project"]["organism"]

    genome_dir = config["input"]["genomes"]

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

    if "ncbi" in sources:

        ncbi = NCBI(
            organism,
            genome_dir,
        )

        ncbi.run()