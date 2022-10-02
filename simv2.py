import math
import pygame as pg
import CursedUtils as cu
import numpy as np
from grid import Grid
from pygame.locals import *

pg.init()

WIDTH = 600
HEIGHT = 800

screen = pg.display.set_mode((WIDTH,HEIGHT))
pg.display.set_caption('Game')

class Cell():
    def __init__(self,grid:Grid, position, size:int, color=(255,255,0)) -> None:
        self.x = position[0]
        self.y = position[1]
        self.surface = pg.Surface((size,size))
        self.surface.fill(color)
        self.rect = pg.Rect(position[0],position[1],size,size)
        self.grid = grid

    def update(self):
        pos = self.grid.get_grid_position((self.x,self.y))

        if self.grid.is_in_grid_bounds((pos[0],pos[1]+1)):
            if self.grid.get_cell((pos[0],pos[1]+1)) == None:
                self.grid.grid[pos[0]][pos[1]] = None
                self.grid.grid[pos[0]][pos[1]+1] = self
                self.x = (pos[0])*self.grid.cell_size
                self.y = (pos[1]+1)*self.grid.cell_size
        
        self.rect.topleft = (self.x,self.y)
        
    def draw(self,screen):
        screen.blit(self.surface,self.rect)

    def is_type(self, object, class_type) -> bool:
        return issubclass(type(object),class_type)
    
    def free(self):
        del(self)

cells_array = []

def main():
    Clock = pg.time.Clock()

    sand_button = cu.Button((WIDTH-60,50),(40,40),(250,250,0),"Sand",(0,0,0),20,border=2)
    water_button = cu.Button((WIDTH-60,100),(40,40),(0,0,170),"water",(0,0,0),20,border=2)
    wood_button = cu.Button((WIDTH-60,150),(40,40),(102, 58, 13),"wood",(0,0,0),20,border=2)

    brush_size = 5

    grid = Grid(WIDTH,HEIGHT,10)

    show_grid_lines = True
    is_running = True
    while is_running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                is_running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    show_grid_lines = not show_grid_lines
            if event.type == pg.MOUSEBUTTONDOWN:
                if pg.mouse.get_pressed()[0]:
                    cu.events.append(cu.MOUSE_LEFT)
            if event.type == pg.MOUSEWHEEL:
                brush_size += event.y
                if brush_size < 1: brush_size = 1
                if brush_size > 50: brush_size = 50
                
        screen.fill((50,50,50))
        delta = Clock.tick(60)/1000
        cu.update()
        mouse = pg.mouse.get_pos()

        for x in np.arange(grid.grid_width):
            for cell in reversed(grid.grid[x]):
                if cell != None:
                    cell.update()

        mouse_keys = pg.mouse.get_pressed()
        pressed_keys = pg.key.get_pressed()
        if mouse_keys[0]:
            pos = grid.get_grid_position(mouse)
            for x in range(brush_size):
                for y in range(brush_size):
                    grid_cell = (pos[0]+x-math.floor(brush_size/2),pos[1]+y-math.floor(brush_size/2))
                    if grid.is_in_grid_bounds(grid_cell):
                        if grid.grid[grid_cell[0]][grid_cell[1]] == None :
                            grid.grid[grid_cell[0]][grid_cell[1]] = Cell(grid, grid.get_world_position(grid_cell), grid.cell_size)
                            cells_array.append(grid.grid[grid_cell[0]][grid_cell[1]])

        if mouse_keys[2]:
            pos = grid.get_grid_position(mouse)
            for x in range(brush_size):
                for y in range(brush_size):
                    grid_cell = (pos[0]+x-math.floor(brush_size/2),pos[1]+y-math.floor(brush_size/2))
                    if grid.is_in_grid_bounds(grid_cell):
                        if grid.grid[grid_cell[0]][grid_cell[1]] != None :
                            cells_array.remove(grid.grid[grid_cell[0]][grid_cell[1]])
                            grid.grid[grid_cell[0]][grid_cell[1]].free()
                            grid.grid[grid_cell[0]][grid_cell[1]] = None

        if show_grid_lines:
            grid.draw_grid_lines(screen)

        for x in range(grid.grid_width):
            for cell in grid.grid[x]:
                if cell != None:
                    cell.draw(screen)

        # draw placement preview
        preview_offset = grid.get_grid_position(((brush_size/2)*grid.cell_size,(brush_size/2)*grid.cell_size))
        placement_preview_grid = grid.get_grid_position((mouse[0],mouse[1]))
        placement_preview_position = (placement_preview_grid[0]-preview_offset[0],placement_preview_grid[1]-preview_offset[1])
        pg.draw.rect(screen,(255,0,0),(placement_preview_position[0]*grid.cell_size,placement_preview_position[1]*grid.cell_size,brush_size*grid.cell_size,brush_size*grid.cell_size),3)

        cu.draw(screen)
        pg.display.flip()
        print(f'game loop-{round(delta*1000, 3)} ms')
    pg.quit()


if __name__ == '__main__':
    main()