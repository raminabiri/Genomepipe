from pathlib import Path

from modules.annotation.manager import AnnotationConfig, AnnotationInput, AnnotationManager


def test_annotation_job_preparation_without_execution(tmp_path: Path):
    manager = AnnotationManager(AnnotationConfig("prokka", tmp_path / "out", 4))
    job = manager.create_job(AnnotationInput("genome1", tmp_path / "g.fasta"))
    assert job["tool"] == "prokka"
    assert job["cpus"] == 4
    assert job["execute"] is False
    assert "gff" in job["outputs"]


def test_invalid_tool_rejected(tmp_path: Path):
    try:
        AnnotationManager(AnnotationConfig("unknown", tmp_path))
        assert False
    except ValueError:
        assert True
