"""Top-level download dispatcher.

The dispatcher builds source-specific plans and only performs network I/O when
``execute=True``. Running this module without explicit execution therefore
cannot start a download accidentally.
"""

from pathlib import Path

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
        token = token.strip()
        if not token:
            continue
        index = int(token)
        if not 1 <= index <= len(DATABASES):
            raise ValueError(f"Invalid database selection: {index}")
        selected.append(DATABASES[index - 1])
    return list(dict.fromkeys(selected))


def _choose_assembly():
    print("\nAssembly set:")
    print("1. Complete genome")
    print("2. Chromosome")
    print("3. Scaffold")
    print("4. Contig")
    print("5. Complete genome + Chromosome")
    print("6. Complete genome + Chromosome + Scaffold")
    choice = input("Choice: ").strip()
    if choice not in ASSEMBLY_CHOICES:
        raise ValueError(f"Invalid assembly choice: {choice}")
    return choice, ASSEMBLY_CHOICES[choice]


def build_plans(organism, output_dir, sources=None, assembly_choice=None):
    """Build download plans without performing network I/O."""
    output_dir = Path(output_dir)
    if sources is None:
        sources = list(DATABASES)

    assembly_levels = ASSEMBLY_CHOICES[assembly_choice] if assembly_choice else ()
    plans = []

    for source in sources:
        if source == "ncbi":
            provider = NCBI(organism, output_dir / source, assembly_levels)
        elif source == "ena":
            provider = ENA(organism, output_dir / source, assembly_levels)
        elif source == "gtdb":
            provider = GTDB(organism, output_dir / source, assembly_levels)
        elif source == "bvbrc":
            provider = BVBRC(organism, output_dir / source, assembly_levels)
        elif source == "ddbj":
            provider = DDBJ(organism, output_dir / source, assembly_levels)
        elif source == "img":
            provider = IMG(organism, output_dir / source, assembly_levels)
        elif source == "sra":
            provider = SRA(organism, output_dir / source)
        elif source == "uniprot":
            provider = UniProt(organism, output_dir / source)
        else:
            raise ValueError(f"Unsupported source: {source}")
        plans.append(provider.plan())

    return plans


def run(project_path, execute=None):
    """Interactive dispatcher.

    If ``execute`` is None, the user is explicitly asked before any network
    operation. This keeps code preparation and actual downloading separate.
    """
    project_path = Path(project_path)
    config_path = project_path / "config" / "project.yaml"

    import yaml
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    organism = config["project"]["organism"]
    output_dir = config["input"]["genomes"]

    use_existing = input("Use existing genomes? (y/n): ").strip().lower()
    if use_existing == "y":
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
    for plan in plans:
        source = plan["source"]
        if source == "ncbi":
            provider = NCBI(organism, Path(output_dir) / source,
                            tuple(plan["assembly_levels"]))
        else:
            # Non-NCBI providers are deliberately gated until their provider-
            # specific execution implementation is enabled.
            results.append({"source": source, "status": "plan_only", "plan": plan})
            continue
        results.append({"source": source, "result": provider.download(execute=True)})

    return {"status": "executed", "results": results, "plans": plans}
