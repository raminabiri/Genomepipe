from pathlib import Path

import pytest

from modules.core.data_mode import (
    DataModeError,
    describe_data_source,
    require_existing_input,
)
from modules.core.models import ProjectContext


def make_context(tmp_path: Path, mode: str) -> ProjectContext:
    return ProjectContext(
        project_name="demo",
        project_root=tmp_path,
        organism="Escherichia coli",
        data_mode=mode,
        config_path=tmp_path / "config" / "project.yaml",
        input_root=tmp_path / "input",
        output_root=tmp_path / "output",
    )


def test_existing_mode_never_requires_network(tmp_path):
    context = make_context(tmp_path, "existing")
    source = describe_data_source(context)
    assert source["mode"] == "existing"
    assert source["network_required"] is False


def test_download_mode_is_explicit(tmp_path):
    context = make_context(tmp_path, "download")
    source = describe_data_source(context)
    assert source["mode"] == "download"
    assert source["network_required"] is True


def test_existing_input_requires_local_directory(tmp_path):
    context = make_context(tmp_path, "existing")
    with pytest.raises(DataModeError):
        require_existing_input(context)

    context.input_root.mkdir()
    assert require_existing_input(context) == context.input_root


def test_download_mode_cannot_be_used_as_existing_input(tmp_path):
    context = make_context(tmp_path, "download")
    context.input_root.mkdir()
    with pytest.raises(DataModeError):
        require_existing_input(context)
