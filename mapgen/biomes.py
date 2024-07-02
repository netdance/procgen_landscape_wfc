from typing import List, Optional
from dataclasses import dataclass, field
from .cell import Cell

@dataclass
class Biomes:
    _biomes: List[Cell] = field(default_factory=list)

    @property
    def biomes(self) -> List[Cell]:
        # Custom getter for the list
        return self._biomes
    
    def find_by_id(self, target_id: str) -> Optional[Cell]:
        return next((obj for obj in self._biomes if obj.id == target_id), None)

    def add_biome(self, grid_obj: Cell) -> None:
        self._biomes.append(grid_obj)
        return
