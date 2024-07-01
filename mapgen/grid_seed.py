
from typing import Dict, Tuple


class GridSeed:

    def __init__(self) -> None:
        self.seed: Dict[Tuple: str] = {}

    def add_seed(self, x: int, y: int, id: str) -> None:
        self.seed[(x,y)] = id

    def get_seeds(self) -> Dict[Tuple: str]:
        return self.seed
