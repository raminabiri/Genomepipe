from pathlib import Path

import pytest

from modules.annotation.engine import AnnotationEngine, AnnotationEngineConfig


def test_engine_creates_prokka_plan_without_execution(tmp_path: Path):
    engine = AnnotationEngine(
        AnnotationEngineConfig("prokka", tmp_path / "out", cpus=4, organism="Helicobacter")
    )
    plan = engine.plan("G001", tmp_path / "G001.fasta", qc_passed=True)

    assert plan.gate.allowed is True
    assert plan.tool.name == "prokka"
    assert plan.output_dir == tmp_path / "out" / "G001"
    assert plan.command[0] == "prokka"
    assert "--cpus" in plan.command
    assert "--genus" in plan.command


def test_engine_blocks_failed_qc(tmp_path: Path):
    engine = AnnotationEngine(AnnotationEngineConfig("bakta", tmp_path / "out"))
    plan = engine.plan("G002", tmp_path / "G002.fasta", qc_passed=False)
    assert plan.gate.allowed is False
    assert "failed QC" in plan.gate.reason


def test_invalid_cpus_rejected(tmp_path: Path):
    with pytest.raises(ValueError):
        AnnotationEngine(AnnotationEngineConfig("prokka", tmp_path, cpus=0))


def test_unknown_tool_rejected(tmp_path: Path):
    with pytest.raises(ValueError):
        AnnotationEngine(AnnotationEngineConfig("unknown", tmp_path))
