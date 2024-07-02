from dataclasses import dataclass, field
from typing import Dict, Tuple

@dataclass
class Cell:
    id: str
    color: Tuple[int, int, int]
    neighbor_weights: Dict[str, float] = field(default_factory=dict)
