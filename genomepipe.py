from pathlib import Path
from modules.download.download import run
from modules.extract.extract import run as extract_run

ROOT = Path(__file__).resolve().parent
PROJECTS_DIR = ROOT / "projects"


def select_project():

    projects = sorted(
        [p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()]
    )

    print("\nAvailable projects:\n")

    for i, p in enumerate(projects, 1):
        print(f"{i}. {p}")

    choice = int(input("\nSelect project: "))

    return projects[choice - 1]


def main():

    project = select_project()

    print(f"\nCurrent project: {project}")

    project_path = ROOT / "projects" / project

    print(f"Project path: {project_path}")

    dry_run = run(project_path)

    if not dry_run:
        extract_run(project_path)
    else:
        print("\n*** DRY RUN: extraction skipped ***")
if __name__ == "__main__":
    main()