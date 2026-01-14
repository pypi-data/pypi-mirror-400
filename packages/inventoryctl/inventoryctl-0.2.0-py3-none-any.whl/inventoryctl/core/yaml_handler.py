from ruamel.yaml import YAML
from pathlib import Path
from typing import Any, Dict

class YamlHandler:
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=2, offset=2)

    def load(self, file_path: Path) -> Dict[str, Any]:
        if not file_path.exists():
            return {}
        with open(file_path, 'r') as f:
            return self.yaml.load(f) or {}

    def save(self, file_path: Path, data: Any):
        with open(file_path, 'w') as f:
            self.yaml.dump(data, f)
