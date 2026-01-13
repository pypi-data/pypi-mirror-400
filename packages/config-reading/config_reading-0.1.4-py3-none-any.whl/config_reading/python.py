"""Loader for Python configuration files."""
import importlib.util


def read_python_config(config_path: str) -> dict | object:
    """Load configuration from a Python file."""
    spec = importlib.util.spec_from_file_location("config_module", config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    return config_module.config
