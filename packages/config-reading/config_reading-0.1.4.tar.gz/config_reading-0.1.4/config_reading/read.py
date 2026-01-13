import os
from importlib.metadata import entry_points


def read_config(config_path: str | os.PathLike = "config.toml") -> dict | object:
    config_ext = os.path.splitext(config_path)[1].lower().lstrip(".")
    for entry_point in entry_points(group="config_reading.readers"):
        if config_ext == entry_point.name:
            loader = entry_point.load()
            config_data = loader(config_path)
            return config_data

    raise ValueError(f"No loader found for configuration file extension: {config_ext}")
