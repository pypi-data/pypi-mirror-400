"""TOML configuration loader."""
import tomllib


def read_toml_config(config_path: str) -> dict:
    """Loads configuration from a TOML file."""
    with open(config_path, "rb") as f:
        return tomllib.load(f)
