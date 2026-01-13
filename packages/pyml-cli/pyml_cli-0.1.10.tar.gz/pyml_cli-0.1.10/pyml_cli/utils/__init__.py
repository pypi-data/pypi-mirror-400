"""Utility functions for pyml."""

from pathlib import Path

import ruamel.yaml


def read_config():
    """Read PyML configuration file.

    The PyML configuration file is always located in the home directory
    and has the name `.pyml.yaml`.

    :returns: A dictionary of PyML configurations.
    :raises FileNotFoundError: when the pyml config file cannot be found.
    """
    try:
        config_path = Path.home() / ".pyml.yaml"
        yaml = ruamel.yaml.YAML()  # defaults to round-trip

        with config_path.open("r+") as f:
            return yaml.load(f.read())
    except FileNotFoundError:
        raise FileNotFoundError("❗️Please run `pyml configure` to configure pyml!")
