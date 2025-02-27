import logging
import random
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from .biomes import Biomes
from .exceptions import ImpossibleWorld
from .cell import Cell

# Creating a logger
logger: logging.Logger = logging.getLogger(__name__)

@dataclass
class Grid:
    width: int
    height: int
    biomes: Biomes
    grid: np.ndarray = field(init=False)
    entropy_grid: np.ndarray = field(init=False)
    smooth_point: Tuple[int, int] = (0, 0)

    # Keey the ability to generate based on either random or first index methods - they produce different looking results
    USE_RANDOM = False
    connector_id: str = None
    LARGE_INT = 10**9  # Use a large integer to represent 'infinity'

    def __post_init__(self):
        self.grid = np.full((self.height, self.width), None, dtype=object)
        self.entropy_grid = np.full((self.height, self.width), self.calculate_initial_entropy(), dtype=int)
        self.smoothed = set()  # Track smoothed cells
        self._smooth_change: bool = False  # Trace if we've changed anything through a pass of the grid

    def calculate_initial_entropy(self) -> int:
        return len(self.biomes.biomes)

    def collapse_least_entropy_cell(self):
        if self.USE_RANDOM:
            y, x = self.find_least_entropy_cell_random()
        else:
            y, x = self.find_least_entropy_cell_first()
        if x is not None and y is not None:
            self.collapse_cell(x, y)

    def find_least_entropy_cell_first(self) -> Tuple[Optional[int], Optional[int]]:
        flat_index = np.argmin(self.entropy_grid)
        min_entropy_index = np.unravel_index(flat_index, self.entropy_grid.shape)
        # Check if the minimum value is LARGE_INT, which means there are no valid cells left
        if self.entropy_grid[min_entropy_index] == self.LARGE_INT:
            return None, None
        return min_entropy_index
    
    def find_first_min_location(array):
        it = np.nditer(array, flags=['multi_index'])
        min_value = next(it)
        min_location = it.multi_index
        for value in it:
            if value < min_value:
                min_value = value
                min_location = it.multi_index
        return min_location

    def find_least_entropy_cell_random(self) -> Tuple[Optional[int], Optional[int]]:
        min_entropy = np.min(self.entropy_grid)
        if min_entropy == self.LARGE_INT:
            return None, None        
        min_entropy_indices = np.argwhere(self.entropy_grid == min_entropy)
        chosen_index = random.choice(min_entropy_indices)        
        return tuple(chosen_index)

    def collapse_cell(self, x: int, y: int):
        if self.grid[y, x] is None:  # Note: numpy uses (row, col), i.e., (y, x)
            weights = [self.calculate_weight(x, y, obj) for obj in self.biomes.biomes]
            try:
                chosen_object = random.choices(self.biomes.biomes, weights=weights)[0]
            except ValueError:
                raise ImpossibleWorld(f"Cannot resolve world, stopping at {x},{y}", self.get_neighbors(x, y))
            self.set_cell(x, y, chosen_object)

    def set_cell(self, x: int, y: int, cell: Cell) -> None:
            self.grid[y, x] = cell
            # Set entropy to LARGE_INT for the assigned cell
            self.entropy_grid[y, x] = self.LARGE_INT
            self.update_neighbors_entropy(x, y)
            return

    def update_neighbors_entropy(self, x: int, y: int):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny, nx] is None:
                    valid_objects = [obj for obj in self.biomes.biomes if self.is_valid_object(nx, ny, obj)]
                    self.entropy_grid[ny, nx] = len(valid_objects)
                    logger.debug("entropy after update of x %s y%s \n%s", x, y, self.entropy_grid)

    def is_valid_object(self, x: int, y: int, obj: Cell) -> bool:
        neighbors = self.get_neighbors(x, y)
        for neighbor in neighbors:
            if neighbor:
                if obj.id not in neighbor.neighbor_weights or neighbor.id not in obj.neighbor_weights:
                    return False
        return True

    def get_neighbors(self, x: int, y: int) -> List[Optional[Cell]]:
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append(self.grid[ny, nx])
        return neighbors

    def calculate_weight(self, x: int, y: int, obj: Cell) -> float:
        weight = 1.0
        neighbors = self.get_neighbors(x, y)
        for neighbor in neighbors:
            if neighbor:
                weight *= neighbor.neighbor_weights.get(obj.id, 0)
        return weight

    def smooth(self) -> bool:
        remove_id = None
        if self.connector_id:
            remove_id = self.biomes.find_by_id(self.connector_id).id
        while True:
            x, y = self.smooth_point
            
            # If we have reached the end of the grid, if we changed anything, start from the beginning, else return
            if y >= self.height:
                if self._smooth_change:
                    self.smooth_point = (0,0)
                    x, y = self.smooth_point
                    self._smooth_change = False
                else:
                    return False
            
            # Get the neighbors of the current cell
            neighbors = self.get_neighbors(x, y)
            
            # Collect the IDs of the neighbors
            neighbor_ids = [neighbor.id for neighbor in neighbors if neighbor is not None]
            
            # Count the occurrences of each ID in the neighbors
            id_counts = Counter(neighbor_ids)
            
            # Find the majority ID and its count
            most_common_ids = id_counts.most_common()
            most_common_ids_dict = dict(most_common_ids)
            majority_id = most_common_ids[0][0]
            if remove_id and majority_id == remove_id:
                if len(most_common_ids) > 1:
                    majority_id = most_common_ids[1][0]

            # Get the current object
            current_object = self.grid[y, x]

            if current_object.id not in most_common_ids_dict:
                most_common_ids_dict[current_object.id] = 0

            if most_common_ids_dict[current_object.id] < 3 and current_object.id != majority_id:
                self.grid[y, x] = self.biomes.find_by_id(majority_id)
                self._smooth_change = True
                return True  # Return after smoothing one cell
            
            # Move to the next cell if no change was made
            self.update_smooth_point()

    # Advance smooth point to next entry in grid
    def update_smooth_point(self):
        x, y = self.smooth_point
        if x + 1 < self.width:
            self.smooth_point = (x + 1, y)
        else:
            self.smooth_point = (0, y + 1)

    def is_valid_object(self, x: int, y: int, obj: Cell) -> bool:
        neighbors = self.get_neighbors(x, y)
        for neighbor in neighbors:
            if neighbor:
                if obj.id not in neighbor.neighbor_weights or neighbor.id not in obj.neighbor_weights:
                    return False
        return True

    def add_random(self, id: str, size: int = 1) -> None:
        offset = size - 1
        x = np.random.randint(0 + offset, self.width - offset)
        y = np.random.randint(0 + offset, self.height - offset)
        obj = self.biomes.find_by_id(id)
        for dx in range(-size, size):
            self.set_cell(x+dx, y, obj)
        for dy in range(-size, size):
            self.set_cell(x, y+dy, obj)

    def needs_work(self) -> bool:
        return np.any(self.grid == None)