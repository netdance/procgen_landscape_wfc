import random
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set
import logging

from .biomes import Biomes
from .cell import Cell
from .exceptions import ImpossibleWorld


@dataclass
class Grid:
    width: int
    height: int
    biomes: Biomes
    grid: List[List[Optional[Cell]]] = field(init=False)
    entropy_grid: List[List[int]] = field(init=False)
    potential_states: List[List[Set[str]]] = field(init=False)
    smooth_point: Tuple[int, int] = (0, 0)
    
    connector_name: str = None
    USE_RANDOM = False

    # Creating a logger
    logger = logging.getLogger("CGrid")

    def __post_init__(self):
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        initial_entropy = self.calculate_initial_entropy()
        self.entropy_grid = [[initial_entropy for _ in range(self.width)] for _ in range(self.height)]
        self.potential_states = [[set(biome.id for biome in self.biomes.biomes) for _ in range(self.width)] for _ in range(self.height)]
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
        min_entropy = float('inf')
        min_entropy_index = (None, None)

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] is None:
                    if self.entropy_grid[y][x] < min_entropy:
                        min_entropy = self.entropy_grid[y][x]
                        min_entropy_index = (y, x)
        
        if min_entropy == float('inf'):
            return None, None
        
        return min_entropy_index

    def find_least_entropy_cell_random(self) -> Tuple[Optional[int], Optional[int]]:
        min_entropy = float('inf')
        min_entropy_indices = []

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] is None:
                    if self.entropy_grid[y][x] < min_entropy:
                        min_entropy = self.entropy_grid[y][x]
                        min_entropy_indices = [(y, x)]
                    elif self.entropy_grid[y][x] == min_entropy:
                        min_entropy_indices.append((y, x))
        
        if min_entropy == float('inf'):
            return None, None
        
        return random.choice(min_entropy_indices)
    
    def collapse_cell(self, x: int, y: int):
        if self.grid[y][x] is None:  # Note: numpy uses (row, col), i.e., (y, x)
            possible_states = list(self.potential_states[y][x])
            weights = [self.calculate_weight(x, y, self.biomes.find_by_id(state)) for state in possible_states]
            try:
                chosen_state = random.choices(possible_states, weights=weights)[0]
                chosen_object = self.biomes.find_by_id(chosen_state)
            except ValueError:
                raise ImpossibleWorld(f"Cannot resolve world, stopping at {x},{y}", self.get_neighbors(x, y))
            self.set_cell(x, y, chosen_object)
            
    def set_cell(self, x: int, y: int, cell: Cell):
        self.grid[y][x] = cell
        self.potential_states[y][x] = {cell.id}
        self.entropy_grid[y][x] = 0
        self.propagate_entropy(x, y)

    def propagate_entropy(self, x: int, y: int):
        queue = deque([(x, y)])

        while queue:
            cx, cy = queue.popleft()
            self.logger.debug("deque cx %s cy %s", cx, cy)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] is None:
                        old_potential_states = self.potential_states[ny][nx]
                        new_potential_states = set(obj.id for obj in self.biomes.biomes if self.is_valid_object(nx, ny, obj))
                        if new_potential_states != old_potential_states:
                            self.logger.debug("nx %s ny %s, new potential states %s", nx, ny, len(new_potential_states))
                            self.potential_states[ny][nx] = new_potential_states
                            self.entropy_grid[ny][nx] = len(new_potential_states)
                            queue.append((nx, ny))

    def is_valid_object(self, x: int, y: int, obj: Cell) -> bool:
        neighbors = self.get_neighbors(x, y)
        for neighbor in neighbors:
            if neighbor and (obj.id not in neighbor.allowed_neighbors() or neighbor.id not in obj.allowed_neighbors()):
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
                    neighbors.append(self.grid[ny][nx])
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
        if self.connector_name:
            remove_id = self.biomes.find_by_id(self.connector_name).id
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
            current_object = self.grid[y][x]

            if current_object.id not in most_common_ids_dict:
                most_common_ids_dict[current_object.id] = 0

            if most_common_ids_dict[current_object.id] < 3 and current_object.id != majority_id:
                self.grid[y][x] = self.biomes.find_by_id(majority_id)
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

    def add_random(self, id: str, size: int = 1) -> None:
        offset = size - 1
        x = random.randint(0 + offset, self.width - offset - 1)
        y = random.randint(0 + offset, self.height - offset - 1)
        obj = self.biomes.find_by_id(id)
        for dx in range(-size, size + 1):
            if 0 <= x + dx < self.width:
                self.set_cell(x + dx, y, obj)
        for dy in range(-size, size + 1):
            if 0 <= y + dy < self.height:
                self.set_cell(x, y + dy, obj)

    def needs_work(self) -> bool:
        return any(any(cell is None for cell in row) for row in self.grid)
    
        