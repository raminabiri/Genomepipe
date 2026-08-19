"""Top-level multi-database download dispatcher.

Network I/O is disabled until the caller explicitly sets ``execute=True`` and
confirms execution in the interactive runner.
"""

from pathlib import Path
import yaml

from .config import DATABASES, ASSEMBLY_CHOICES
from .ncbi import NCBI
from .ena import ENA
from .gtdb import GTDB
from .bvbrc import BVBRC
from .ddbj import DDBJ
from .img import IMG
from .sra import SRA
from .uniprot import UniProt


ASSEMBLY_SOURCES = {"ncbi", "ena", "gtdb", "bvbrc", "ddbj", "img"}


def _choose_sources():
    print("\nAvailable databases:")
    for index, source in enumerate(DATABASES, start=1):
        print(f"{index}. {source.upper()}")
    raw = input("Select database numbers (comma-separated): ").strip()
    selected = []
    for token in raw.split(","):
        if token.strip():
            index = int(token.strip())
            if not 1 <= index <= len(DATABASES):
                raise ValueError(f"Invalid database selection: {index}")
            selected.append(DATABASES[index - 1])
    if not selected:
        raise ValueError("At least one database must be selected")
    return list(dict.fromkeys(selected))


def _choose_assembly():
    labels = {
        "1": "Complete genome",
        "2": "Chromosome",
        "3": "Scaffold",
        "4": "Contig",
        "5": "Complete genome + Chromosome",
        "6": "Complete genome + Chromosome + Scaffold",
    }
    print("\nAssembly set:")
    for key, label in labels.items():
        print(f"{key}. {label}")
    choice = input("Choice: ").strip()
    if choice not in ASSEMBLY_CHOICES:
        raise ValueError(f"Invalid assembly choice: {choice}")
    return choice, ASSEMBLY_CHOICES[choice]


def _provider(source, organism, output_dir, assembly_levels):
    root = Path(output_dir) / source
    if source == "ncbi":
        return NCBI(organism, root, assembly_levels)
    if source == "ena":
        return ENA(organism, root, assembly_levels)
    if source == "gtdb":
        return GTDB(organism, root, assembly_levels)
    if source == "bvbrc":
        return BVBRC(organism, root, assembly_levels)
    if source == "ddbj":
        return DDBJ(organism, root, assembly_levels)
    if source == "img":
        return IMG(organism, root, assembly_levels)
    if source == "sra":
        return SRA(organism, root)
    if source == "uniprot":
        return UniProt(organism, root)
    raise ValueError(f"Unsupported source: {source}")


def build_plans(organism, output_dir, sources=None, assembly_choice=None):
    """Build provider plans without performing network I/O."""
    sources = list(DATABASES if sources is None else sources)
    levels = ASSEMBLY_CHOICES[assembly_choice] if assembly_choice else ()
    return [
        _provider(source, organism, output_dir, levels).plan()
        for source in sources
    ]


def run(project_path, execute=None):
    project_path = Path(project_path)
    with (project_path / "config" / "project.yaml").open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    organism = config["project"]["organism"]
    output_dir = config["input"]["genomes"]

    if input("Use existing genomes? (y/n): ").strip().lower() == "y":
        return {"status": "existing_input", "plans": []}

    sources = _choose_sources()
    assembly_choice = None
    if any(source in ASSEMBLY_SOURCES for source in sources):
        assembly_choice, _ = _choose_assembly()

    plans = build_plans(organism, output_dir, sources, assembly_choice)

    if execute is None:
        execute = input("Execute downloads now? (y/n): ").strip().lower() == "y"
    if not execute:
        return {"status": "plan_only", "plans": plans}

    results = []
    for source in sources:
        provider = _provider(source, organism, output_dir,
                             ASSEMBLY_CHOICES[assembly_choice] if assembly_choice else ())
        results.append({"source": source, "result": provider.download(execute=True)})
    return {"status": "executed", "results": results, "plans": plans}
