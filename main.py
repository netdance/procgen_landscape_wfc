import cProfile
import logging
import pstats
import sys
from time import sleep

import numpy as np
import pygame

from mapgen.biomes import Biomes
from mapgen.lgrid import Grid
from mapgen.grid_object import GridObject
from mapgen.exceptions import ImpossibleWorld
from UI.pygame_display import PygameDisplay


PROFILE = False

# Basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Creating a logger
logger = logging.getLogger(__name__)

biomes: Biomes = Biomes()
lbiomes: Biomes = Biomes()

'''
# Define some grid objects with single character IDs and neighbor weights
lbiomes.add_biome(GridObject(id='W', color=(0, 0, 153),
                  neighbor_weights={'W': 1.5, "w": 0.9, 'r': 0.01}))
lbiomes.add_biome(GridObject(id='w', color=(0, 0, 204),
                  neighbor_weights={'w': 1.5, 'W': 0.7, 'g': 0.7, 's': 0.6, 'r': 0.01}))
lbiomes.add_biome(GridObject(id='g', color=(128, 255, 0),
                  neighbor_weights={'g': 2, 'w': 0.25, 'f': 0.38, 's': 0.35, 'h': 0.5, 'r': 0.01}))
lbiomes.add_biome(GridObject(id='f', color=(0, 204, 0),
                  neighbor_weights={'f': 2, 'g': 0.4, 'F': 0.66, 'r': 0.01}))
lbiomes.add_biome(GridObject(id='F', color=(0, 102, 51),
                  neighbor_weights={'F': 2, 'f': 0.85, 'r': 0.01}))
lbiomes.add_biome(GridObject(id='h', color=(102, 51, 0),
                  neighbor_weights={'h': 2, 'g': 0.66, 'm': 0.66, 'r': 0.01}))
lbiomes.add_biome(GridObject(id='m', color=(128, 128, 128),
                  neighbor_weights={'m': 2, 'M': 0.75, 'h': 0.8, 'r': 0.01}))
lbiomes.add_biome(GridObject(id='M', color=(192, 192, 192),
                  neighbor_weights={'M': 2, 'm': 1.0, 'r': 0.01}))
lbiomes.add_biome(GridObject(id='s', color=(153, 153, 0),
                  neighbor_weights={'s': 2, 'w': 0.6, 'g': 0.8, 'r': 0.01}))
lbiomes.add_biome(GridObject(id='r', color=(210, 180, 140),
                  neighbor_weights={'r': 0.001, 'W': 0.1, 'w': 0.1, 'g': 0.1, 
                                    'f': 0.1, 'F': 0.1, 'h': 0.1, 'm': 0.1, 'M': 0.1, 
                                    's': 0.1, 'r': 0.01 }))
'''

# Define some grid objects with single character IDs and neighbor weights
biomes.add_biome(GridObject(id=0, name='W', color=(0, 0, 153),
                  neighbor_weights={'W': 1.3, "w": 0.9, 'r': 0.01}))
biomes.add_biome(GridObject(id=1, name='w', color=(0, 0, 204),
                  neighbor_weights={'w': 1.3, 'W': 0.5, 'g': 0.7, 's': 0.6, 'r': 0.01}))
biomes.add_biome(GridObject(id=2, name='g', color=(128, 255, 0),
                  neighbor_weights={'g': 2.2, 'w': 0.28, 'f': 0.26, 's': 0.25, 'h': 0.42, 'r': 0.01}))
biomes.add_biome(GridObject(id=3, name='f', color=(0, 204, 0),
                  neighbor_weights={'f': 2.25, 'g': 0.34, 'F': 0.6, 'r': 0.01}))
biomes.add_biome(GridObject(id=4, name='F', color=(0, 102, 51),
                  neighbor_weights={'F': 1.65, 'f': 0.9, 'r': 0.01}))
biomes.add_biome(GridObject(id=5, name='h', color=(102, 51, 0),
                  neighbor_weights={'h': 2, 'g': 0.63, 'm': 0.66, 'r': 0.01}))
biomes.add_biome(GridObject(id=6, name='m', color=(128, 128, 128),
                  neighbor_weights={'m': 2, 'M': 0.75, 'h': 0.8, 'r': 0.01}))
biomes.add_biome(GridObject(id=7, name='M', color=(192, 192, 192),
                  neighbor_weights={'M': 1.5, 'm': 1.0, 'r': 0.01}))
biomes.add_biome(GridObject(id=8, name='s', color=(153, 153, 0),
                  neighbor_weights={'s': 2, 'w': 0.6, 'g': 0.8, 'r': 0.01}))
biomes.add_biome(GridObject(id=9, name='r', color=(210, 180, 140),
                  neighbor_weights={'r': 0.001, 'W': 0.1, 'w': 0.1, 'g': 0.1, 
                                    'f': 0.1, 'F': 0.1, 'h': 0.1, 'm': 0.1, 'M': 0.1, 
                                    's': 0.1, 'r': 0.01 }))

# Initialize Pygame
pygame.init()

# Screen dimensions and colors
CELL_SIZE = 8
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255) 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Wave Function Collapse')

CONNECTOR_ID = 'r'

def run_wfc_and_display(grid: Grid) -> bool:
    try:
        count = 0
        #while np.any(grid.grid == None):
        while any(any(cell is None for cell in row) for row in grid.grid):
            grid.collapse_least_entropy_cell()
            count += 1
            if count // 50 == count / 50:
                display_grid(grid)
    except ImpossibleWorld as e:
        display_grid(grid)
        # e.args[1] is the list of objects
        objects_with_ids = e.args[1]
        # Collect all ids in a list and join them into a single string
        ids = [str(obj.id) for obj in objects_with_ids if obj is not None]
        print(" ".join(ids))
        return False
    
    display_grid(grid)
    return True

def run_smooth_and_display(grid: Grid) -> None:
    count = 0
    running = True
    while running:
        count += 1
        running = grid.smooth()
        if count // 5 == count / 5:
            display_grid(grid)
    display_grid(grid)
    return

def display_grid(grid):
    for y in range(grid.height):
        for x in range(grid.width):
            cell: GridObject = grid.grid[y][x]
            color = cell.color if cell else BLACK
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.display.flip()

def init_grid() -> Grid:
    grid_width = int(SCREEN_WIDTH / CELL_SIZE)
    grid_height = int(SCREEN_HEIGHT / CELL_SIZE)
    grid = Grid(width=grid_width, height=grid_height, biomes=biomes)
    grid.connector_name = CONNECTOR_ID
    '''
    grid.add_random('s', 5)
    grid.add_random('s', 5)
    grid.add_random('W', 5)
    grid.add_random('W', 3)
    grid.add_random('W', 3)
    grid.add_random('M', 3)
    grid.add_random('M', 3)
    grid.add_random('M', 5)
    grid.add_random('F', 4)
    grid.add_random('F', 4)
    grid.add_random('F', 5)
    '''
    return grid

def main():
    
    grid = init_grid()
    #display = PygameDisplay(screen_height=SCREEN_HEIGHT, screen_width=SCREEN_WIDTH, cell_size=CELL_SIZE)

    running = True
    while running:
        screen.fill(WHITE)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                logger.debug("Quit recieved")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                    logger.debug("Quit key recieved")
                if event.key == pygame.K_r:
                    logger.debug("Rerun command recieved")
                    grid = init_grid()
                    run_wfc_and_display(grid)

        if run_wfc_and_display(grid):
            run_smooth_and_display(grid)
        else:
            print("problem rendering")
            sleep(1)            

    if not PROFILE:            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":

    if PROFILE:
        profiler = cProfile.Profile()
        profiler.enable()
        main()
        profiler.disable()

        stats = pstats.Stats(profiler)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats()
    else:
        main()