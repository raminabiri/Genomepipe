from pathlib import Path

from modules.core.config import build_context


ROOT = Path(__file__).resolve().parent
PROJECTS_DIR = ROOT / "projects"


def select_project() -> Path:
    projects = sorted(p for p in PROJECTS_DIR.iterdir() if p.is_dir())
    if not projects:
        raise RuntimeError(f"No projects found in {PROJECTS_DIR}")

    print("\nAvailable projects:\n")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project.name}")

    choice = int(input("\nSelect project: "))
    if choice < 1 or choice > len(projects):
        raise ValueError("Invalid project selection")
    return projects[choice - 1]


def main() -> None:
    project_path = select_project()
    config_path = project_path / "config" / "project.yaml"
    context = build_context(config_path)

    print(f"\nCurrent project: {context.project_name}")
    print(f"Organism: {context.organism}")
    print(f"Project path: {context.project_root}")
    print(f"Input root: {context.input_root}")
    print(f"Output root: {context.output_root}")
    print("Core context initialized. No download or analysis stage is executed.")


if __name__ == "__main__":
    main()
