# config-reading

`config-reading` is a configuration reading extensibility point for your package via python entry-points mechanism.

## Features
- Bundled formats: TOML, YAML, JSON, Python
- Extensible via Python entry-points

## Installation
Install the core library:
```sh
pip install config-reading
```

To enable YAML support:
```sh
pip install config-reading[yaml]
```

## Usage Example
```python
from config_reading import read_config

config1 = read_config('config.toml')
config2 = read_config('config.json')
config3 = read_config('config.py')
# For YAML (requires optional dependency):
# config = load_yaml_config('config.yaml')
```

## Extensibility
You can add new config formats by registering entry points in your own package.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
© 2025 Vitalii Stepanenko
