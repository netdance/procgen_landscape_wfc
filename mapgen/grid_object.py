from dataclasses import dataclass, field
from typing import Dict, Tuple

@dataclass
class GridObject:
    id: int  
    name: str
    color: Tuple[int, int, int]
    neighbor_weights: Dict[str, float] = field(default_factory=dict)
    neighbor_iweights: Dict[int, float] = field(default_factory=dict)
