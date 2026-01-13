from dataclasses import dataclass
from importlib.resources import files
from typing import Mapping
import json
import copy

@dataclass
class Distribution():
    name: str|None
    frequency_map: dict[str, float]
    source: str | None = None
    version: str | None = None

    def __post_init__(self): # Create a new pointer to the frequency
        self.frequency_map = dict(self.frequency_map)

    def normalize_map(self):
        total = sum(self.frequency_map.values())
        for key in self.frequency_map:
            self.frequency_map[key] /= total
        return self

    def eliminate_entry(self, key):
        if key in self.frequency_map.keys():
            self.frequency_map.pop(key)



_PACKAGE = "aldepyde.data.distributions"
def load(name: str) -> Distribution:
    path = files(_PACKAGE) / f"{name}.json"
    if not path.is_file():
        available = sorted(p.stem for p in files(_PACKAGE).iterdir() if p.suffix == '.json')
        raise ValueError(f'Unknown distribution "{name}". Available: {available}')

    raw = json.loads(path.read_text(encoding='utf-8'))
    return Distribution(
        name=name,
        frequency_map=raw.get('distribution'),
        source=raw.get('source'),
        version=raw.get('version')
    )

def available_distributions() -> list:
    available = sorted(p.stem for p in files(_PACKAGE).iterdir() if p.suffix == '.json')
    return available