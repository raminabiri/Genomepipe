from pathlib import Path
import yaml


def read_config(config_file):

    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def make_dir(path):

    Path(path).mkdir(parents=True, exist_ok=True)