from pathlib import Path

from modules.core.runner import run_existing_project


def test_runner_processes_limited_existing_genomes(tmp_path: Path):
    project = tmp_path / "demo"
    config = project / "config" / "project.yaml"
    genomes = project / "input" / "genomes"
    genomes.mkdir(parents=True)
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        "project:\n  name: demo\n  organism: Helicobacter pylori\n"
        "data_mode: existing\npaths:\n  input: input\n  output: output\n",
        encoding="utf-8",
    )
    for name in ("g1.fasta", "g2.fasta"):
        (genomes / name).write_text(f">{name}\nATGCGC\n", encoding="utf-8")

    result = run_existing_project(config, limit=1)
    assert result.discovered == 1
    assert result.valid == 1
    assert result.qc_pass == 1
    assert (project / "output" / "qc" / "qc_report.tsv").exists()
