from typing import List
from dataclasses import dataclass, field
from .grid_object import GridObject

@dataclass
class Biomes:
    _biomes: List[GridObject] = field(default_factory=list)

    @property
    def biomes(self) -> List[GridObject]:
        # Custom getter for the list
        return self._biomes
    
    def find_by_id(self, target_id: int) -> GridObject:
        return next((obj for obj in self._biomes if obj.id == target_id), None)

    def find_by_name(self, target_name: str) -> GridObject:
        return next((obj for obj in self._biomes if obj.name == target_name), None)
    
    def get_id_from_name(self, target_name: str) -> int:
        return next((obj.id for obj in self._biomes if obj.name == target_name))

    def add_biome(self, grid_obj: GridObject) -> None:
        self._biomes.append(grid_obj)

    def compile_iwieghts(self):
        for biome in self.biomes:
            for key, value in biome.neighbor_weights.items():
                new_key = self.get_id_from_name(key)
                biome.neighbor_iweights[new_key] = value