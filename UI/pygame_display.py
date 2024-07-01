import numpy as np
import pygame

from mapgen.exceptions import ImpossibleWorld

class PygameDisplay:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255) 
    
    def __init__(self, screen_width, screen_height, cell_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = cell_size

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Wave Function Collapse')

    def display_grid(self, grid):
        for y in range(grid.height):
            for x in range(grid.width):
                cell = grid.grid[y][x]
                color = cell.color if cell else self.BLACK
                pygame.draw.rect(self.screen, color, (x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size))

    def update_display(self):
        pygame.display.flip()


    def run_wfc_and_display(self, grid) -> bool:
        try:
            count = 0
            while np.any(grid.grid == None):
                grid.collapse_least_entropy_cell()
                count += 1
                if count // 50 == count / 50:
                    self.display_grid(grid)
        except ImpossibleWorld as e:
            ## Should no longer be raised.  But leave this in case a bug is introduced.
            self.display_grid(grid)
            # e.args[1] is the list of objects
            objects_with_ids = e.args[1]
            # Collect all ids in a list and join them into a single string
            ids = [str(obj.id) for obj in objects_with_ids if obj is not None]
            print(" ".join(ids))
            return False
        
        self.display_grid(grid)
        return True

    def run_smooth_and_display(self, grid) -> None:
        count = 0
        running = True
        while running:
            count += 1
            running = grid.smooth()
            if count // 5 == count / 5:
                self.display_grid(grid)
        self.display_grid(grid)
        return