from .helper import read_config
from .helper import make_dir
from .ncbi import NCBI


def run(project_path):

    config = read_config(project_path / "config" / "project.yaml")

    genome_dir = config["input"]["genomes"]

    make_dir(genome_dir)

    organism = config["project"]["organism"]

    use_existing = input("\nUse existing genomes? (y/n): ").lower()

    if use_existing == "y":
        return

    if input("Download from NCBI? (y/n): ").lower() == "y":

        ncbi = NCBI(
            organism,
            genome_dir,
        )

        ncbi.run()