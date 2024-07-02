import numpy as np
import time

entropy_grid1 = np.full((1000, 1000), np.random.randint(0,10), dtype=int)

def find_least_entropy_cell_first(entropy_grid):
    flat_index = np.argmin(entropy_grid)
    min_entropy_index = np.unravel_index(flat_index, entropy_grid.shape)
    return min_entropy_index

def find_first_min_location(entropy_grid):
    it = np.nditer(entropy_grid, flags=['multi_index'])
    min_value = next(it)
    min_location = it.multi_index
    for value in it:
        if value < min_value:
            min_value = value
            min_location = it.multi_index
    return min_location

start_time = time.time()
for _ in range(5):
    arg = find_least_entropy_cell_first(entropy_grid1)
    
print(arg)
arg_time = time.time() - start_time

start_time = time.time()
for _ in range(5):
    it = find_first_min_location(entropy_grid1)

print(it)
it_time = time.time() - start_time

print(f"Arg time {arg_time}")
print(f"It time {it_time}")