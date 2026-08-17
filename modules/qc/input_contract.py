from pathlib import Path

from modules.core.contracts import ModuleContract, ModuleInput


LOCAL_GENOME_INPUT_CONTRACT = ModuleContract(
    name="local_genome_input",
    version="1.0",
    required_inputs=("genomes",),
    produced_outputs=("genome_manifest.json", "genome_summary.tsv"),
)


def build_local_genome_input(genome_root: Path) -> ModuleInput:
    return ModuleInput(paths=(genome_root,), metadata={"source": "local", "network": False})
