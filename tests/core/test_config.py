import pytest

from modules.core.config import ConfigError, build_context, validate_config


def test_existing_data_mode_is_default():
    config = {"project": {"name": "demo", "organism": "Escherichia coli"}}
    validate_config(config)
    assert config.get("data_mode", "existing") == "existing"


def test_download_data_mode_is_valid():
    validate_config(
        {
            "project": {"name": "demo", "organism": "Escherichia coli"},
            "data_mode": "download",
        }
    )


def test_invalid_data_mode_is_rejected():
    with pytest.raises(ConfigError):
        validate_config(
            {
                "project": {"organism": "Escherichia coli"},
                "data_mode": "remote",
            }
        )


def test_missing_organism_is_rejected():
    with pytest.raises(ConfigError):
        validate_config({"project": {"name": "demo"}})


def test_build_context_reads_paths(tmp_path):
    project = tmp_path / "demo"
    config_dir = project / "config"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "project.yaml"
    config_path.write_text(
        "project:\n"
        "  name: demo\n"
        "  organism: Escherichia coli\n"
        "data_mode: existing\n"
        "paths:\n"
        "  input: input\n"
        "  output: output\n",
        encoding="utf-8",
    )

    context = build_context(config_path)
    assert context.project_name == "demo"
    assert context.organism == "Escherichia coli"
    assert context.data_mode == "existing"
    assert context.input_root == project / "input"
    assert context.output_root == project / "output"
