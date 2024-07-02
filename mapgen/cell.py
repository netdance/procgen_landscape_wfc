from dataclasses import dataclass, field
from typing import Dict, Set, Tuple


@dataclass
class Cell:
    id: str
    color: Tuple[int, int, int]
    neighbor_weights: Dict[str, float] = field(default_factory=dict)

    def allowed_neighbors(self) -> Set[str]:
        return set(self.neighbor_weights.keys())