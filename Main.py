import pygame, math
from math import floor
from pygame.locals import *

pygame.init()

WIDTH = 600
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Game')


class Grid():

    def __init__(self,width:int,height:int,cell_size:int=1) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = round(self.width/self.cell_size)
        self.grid_height = round(self.height/self.cell_size)
        self.grid = []
        self.is_finished = False

    def generate_grid(self):
        for x in range(round(self.width/self.cell_size)):
            self.grid.append([])
            for y in range(round(self.height/self.cell_size)):
                self.grid[x].append(None)
        self.is_finished = True
    
    def generate_borders(self,size):
        for s in range(size-1):
            for x in range(self.grid_width):
                border = Border(self,(x*self.cell_size,s*self.cell_size),self.cell_size,(0,0,0),-1,0)
                self.grid[x][s] = border
                border = Border(self,(x*self.cell_size,(self.grid_height-s-1)*self.cell_size),self.cell_size,(0,0,0),-1,0)
                self.grid[x][self.grid_height-s-1] = border
            for y in range(self.grid_height):
                border = Border(self,(s*self.cell_size,y*self.cell_size),self.cell_size,(0,0,0),-1,0)
                self.grid[s][y] = border
                border = Border(self,((self.grid_width-s-1)*self.cell_size,y*self.cell_size),self.cell_size,(0,0,0),-1,0)
                self.grid[self.grid_width-s-1][y] = border

    def draw_grid_lines(self):
        for x in range(self.width+1):
            pygame.draw.line(screen,(255,255,255),(x*self.cell_size,0),(x*self.cell_size,self.height*self.cell_size))
        for y in range(self.height+1):
            pygame.draw.line(screen,(255,255,255),(0,y*self.cell_size),(self.width*self.cell_size,y*self.cell_size))

    def swap_grid_cells(self,grid_cell,target_grid_cell):
        temp = self.grid[target_grid_cell[0]][target_grid_cell[1]]
        self.grid[target_grid_cell[0]][target_grid_cell[1]] = self.grid[grid_cell[0]][grid_cell[1]]
        self.grid[grid_cell[0]][grid_cell[1]] = temp
    
    def get_closest_empty_cell(self,current_position,direction,Velocity):
        if Velocity <= 0: return self.grid[current_position[0]][current_position[1]]
        grid_cell = (current_position[0]+direction[0],current_position[1]+direction[1])
        if self.grid[grid_cell[0]][grid_cell[1]] == None:
            return self.get_closest_empty_cell(grid_cell,direction,Velocity-1)
        return self.grid[current_position[0]][current_position[1]]
    
    def get_closest_empty_cell_position(self,current_position,direction,Velocity):
        while Velocity > 0:
            if Velocity <= 0: return current_position
            grid_cell = (current_position[0]+direction[0],current_position[1]+direction[1])
            if grid_cell[0] < 0 or grid_cell[0] > len(self.grid)-1 or grid_cell[1] < 0 or grid_cell[1] > len(self.grid[0])-1: return current_position
            if self.grid[grid_cell[0]][grid_cell[1]] == None:
                current_position = grid_cell
            else: return current_position
            Velocity-=1
        return current_position

    def get_neighbours_cells(self,grid_position):
        neighbours = []
        neighbours.append(self.grid[grid_position[0]-1][grid_position[1]+1]) #top left
        neighbours.append(self.grid[grid_position[0]+1][grid_position[1]+1]) #top right
        neighbours.append(self.grid[grid_position[0]-1][grid_position[1]-1]) #bottom left
        neighbours.append(self.grid[grid_position[0]+1][grid_position[1]-1]) #bottom right
        neighbours.append(self.grid[grid_position[0]][grid_position[1]+1]) #top
        neighbours.append(self.grid[grid_position[0]][grid_position[1]-1]) #bottom
        neighbours.append(self.grid[grid_position[0]+1][grid_position[1]]) #left
        neighbours.append(self.grid[grid_position[0]-1][grid_position[1]]) #right
        return neighbours

    def get_grid_position(self,position):
        if position[0] >= 0 and position[0] <= self.width or position[1] >= 0 and position[1] <= self.height:
            return math.floor(position[0]/self.cell_size), math.floor(position[1]/self.cell_size)
        return False

    def get_world_position(self,position):
        if position[0] >= 0 and position[0] <= self.width and position[1] >= 0 and position[1] <= self.height:
            return math.floor(position[0]*self.cell_size), math.floor(position[1]*self.cell_size)
    
class Cell():

    list_of_cells = []

    def __init__(self,grid:Grid,position,size,color,life_time,velocity,fluid=False) -> None:
        self.x = position[0]
        self.y = position[1]
        self.surface = pygame.Surface((size,size))
        self.rect = self.surface.get_rect(topleft=(self.x,self.y))
        self.rect.topleft = (self.x,self.y)
        self.color = color
        self.life_time = life_time
        self.velocity = velocity
        self.fluid = fluid
        self.grid = grid
        Cell.list_of_cells.append(self)

    def update(self):
        pass
    
    def draw(self):
        self.surface.fill(self.color)
        screen.blit(self.surface,self.rect)
    
    def free(self):
        Cell.list_of_cells.remove(self)
        del(self)

class Sand(Cell):
    def __init__(self, grid: Grid, position, size, color, life_time, velocity, fluid=False) -> None:
        super().__init__(grid, position, size, color, life_time, velocity, fluid)

    def update(self):
        self.rect.topleft = (self.x,self.y)
        current_pos = self.grid.get_grid_position((self.x,self.y))

        bottom = (current_pos[0],current_pos[1]+1)
        right = (current_pos[0]+1,current_pos[1])
        left = (current_pos[0]-1,current_pos[1])
        bottom_left = (current_pos[0]-1,current_pos[1]+1)
        bottom_right = (current_pos[0]+1,current_pos[1]+1)

        if self.grid.grid[current_pos[0]][current_pos[1]+1] == None:  # TODO FIX THE CRASH AND CELLS GOING DIAGNAL IF THERE IS A BLOCK NEXT TO THEM
            self.grid.swap_grid_cells(current_pos,bottom)
            self.x = current_pos[0]*self.grid.cell_size
            self.y = (current_pos[1]+1)*self.grid.cell_size
            return

        elif self.grid.grid[current_pos[0]][current_pos[1]+1].fluid == True:
            self.grid.grid[current_pos[0]][current_pos[1]] = self.grid.grid[current_pos[0]][current_pos[1]+1]
            self.grid.grid[current_pos[0]][current_pos[1]+1].x = self.x = current_pos[0]*self.grid.cell_size
            self.grid.grid[current_pos[0]][current_pos[1]+1].y = (current_pos[1])*self.grid.cell_size
            self.grid.grid[current_pos[0]][current_pos[1]+1] = self
            self.x = current_pos[0]*self.grid.cell_size
            self.y = (current_pos[1]+1)*self.grid.cell_size
            return

        if self.grid.grid[current_pos[0]-1][current_pos[1]] == None:
            if self.grid.grid[current_pos[0]-1][current_pos[1]+1] == None:
                self.grid.swap_grid_cells(current_pos,bottom_left)
                self.x = (current_pos[0]-1)*self.grid.cell_size
                self.y = (current_pos[1]+1)*self.grid.cell_size
                return
            elif self.grid.grid[current_pos[0]-1][current_pos[1]+1].fluid == True:
                self.grid.grid[current_pos[0]][current_pos[1]] = self.grid.grid[current_pos[0]-1][current_pos[1]+1]
                self.grid.grid[current_pos[0]-1][current_pos[1]+1].x = self.x = current_pos[0]*self.grid.cell_size
                self.grid.grid[current_pos[0]-1][current_pos[1]+1].y = (current_pos[1])*self.grid.cell_size
                self.grid.grid[current_pos[0]-1][current_pos[1]+1] = self
                self.x = (current_pos[0]-1)*self.grid.cell_size
                self.y = (current_pos[1]+1)*self.grid.cell_size
                return

        if self.grid.grid[current_pos[0]-1][current_pos[1]] != None and self.grid.grid[current_pos[0]-1][current_pos[1]+1] != None:
            if self.grid.grid[current_pos[0]-1][current_pos[1]+1].fluid == True:
                self.grid.grid[current_pos[0]][current_pos[1]] = self.grid.grid[current_pos[0]-1][current_pos[1]+1]
                self.grid.grid[current_pos[0]-1][current_pos[1]+1].x = self.x = current_pos[0]*self.grid.cell_size
                self.grid.grid[current_pos[0]-1][current_pos[1]+1].y = (current_pos[1])*self.grid.cell_size
                self.grid.grid[current_pos[0]-1][current_pos[1]+1] = self
                self.x = (current_pos[0]-1)*self.grid.cell_size
                self.y = (current_pos[1]+1)*self.grid.cell_size
                return

        if self.grid.grid[current_pos[0]+1][current_pos[1]] == None:
            if self.grid.grid[current_pos[0]+1][current_pos[1]+1] == None:
                self.grid.swap_grid_cells(current_pos,bottom_right)
                self.x = (current_pos[0]+1)*self.grid.cell_size
                self.y = (current_pos[1]+1)*self.grid.cell_size
                return
            if self.grid.grid[current_pos[0]+1][current_pos[1]+1].fluid == True:
                self.grid.grid[current_pos[0]][current_pos[1]] = self.grid.grid[current_pos[0]+1][current_pos[1]+1]
                self.grid.grid[current_pos[0]+1][current_pos[1]+1].x = self.x = current_pos[0]*self.grid.cell_size
                self.grid.grid[current_pos[0]+1][current_pos[1]+1].y = (current_pos[1])*self.grid.cell_size
                self.grid.grid[current_pos[0]+1][current_pos[1]+1] = self
                self.x = (current_pos[0]+1)*self.grid.cell_size
                self.y = (current_pos[1]+1)*self.grid.cell_size
                return
        
        if self.grid.grid[current_pos[0]+1][current_pos[1]] != None and self.grid.grid[current_pos[0]+1][current_pos[1]+1] != None:
            if self.grid.grid[current_pos[0]+1][current_pos[1]+1].fluid == True:
                self.grid.grid[current_pos[0]][current_pos[1]] = self.grid.grid[current_pos[0]+1][current_pos[1]+1]
                self.grid.grid[current_pos[0]+1][current_pos[1]+1].x = self.x = current_pos[0]*self.grid.cell_size
                self.grid.grid[current_pos[0]+1][current_pos[1]+1].y = (current_pos[1])*self.grid.cell_size
                self.grid.grid[current_pos[0]+1][current_pos[1]+1] = self
                self.x = (current_pos[0]+1)*self.grid.cell_size
                self.y = (current_pos[1]+1)*self.grid.cell_size
                return

class Water(Cell):
    def __init__(self, grid: Grid, position, size, color, life_time, velocity=2, fluid=True) -> None:
        super().__init__(grid, position, size, color, life_time, velocity, fluid)
    
    def update(self):
        self.rect.topleft = (self.x,self.y)
        current_pos = self.grid.get_grid_position((self.x,self.y))

        bottom = (current_pos[0],current_pos[1]+1)
        right = (current_pos[0]+1,current_pos[1])
        left = (current_pos[0]-1,current_pos[1])
        bottom_left = (current_pos[0]-1,current_pos[1]+1)
        bottom_right = (current_pos[0]+1,current_pos[1]+1)

        closest = self.grid.get_closest_empty_cell_position(current_pos,(0,1),self.velocity)
        if self.grid.grid[closest[0]][closest[1]] == None:
            self.grid.swap_grid_cells(current_pos,closest)
            self.x = closest[0]*self.grid.cell_size
            self.y = closest[1]*self.grid.cell_size
            return

        closest = self.grid.get_closest_empty_cell_position(current_pos,(-1,1),self.velocity)
        if self.grid.grid[current_pos[0]-1][current_pos[1]+1] == None and self.grid.grid[current_pos[0]-1][current_pos[1]] == None:
            self.grid.swap_grid_cells(current_pos,bottom_left)
            self.x = (current_pos[0]-1)*self.grid.cell_size
            self.y = (current_pos[1]+1)*self.grid.cell_size
            return

        closest = self.grid.get_closest_empty_cell_position(current_pos,(1,1),self.velocity)
        if self.grid.grid[current_pos[0]+1][current_pos[1]+1] == None and self.grid.grid[current_pos[0]+1][current_pos[1]] == None:
            self.grid.swap_grid_cells(current_pos,bottom_right)
            self.x = (current_pos[0]+1)*self.grid.cell_size
            self.y = (current_pos[1]+1)*self.grid.cell_size
            return

        closest = self.grid.get_closest_empty_cell_position(current_pos,(-1,0),self.velocity)
        if self.grid.grid[closest[0]][closest[1]] == None:
            self.grid.swap_grid_cells(current_pos,closest)
            self.x = closest[0]*self.grid.cell_size
            self.y = closest[1]*self.grid.cell_size
            return

        closest = self.grid.get_closest_empty_cell_position(current_pos,(1,0),self.velocity)
        if self.grid.grid[closest[0]][closest[1]] == None:
            self.grid.swap_grid_cells(current_pos,closest)
            self.x = closest[0]*self.grid.cell_size
            self.y = closest[1]*self.grid.cell_size
            return

        # if self.grid.grid[current_pos[0]][current_pos[1]+1] == None:
        #     self.grid.swap_grid_cells(current_pos,bottom)
        #     self.x = current_pos[0]*self.grid.cell_size
        #     self.y = (current_pos[1]+1)*self.grid.cell_size

        # elif self.grid.grid[current_pos[0]-1][current_pos[1]+1] == None and self.grid.grid[current_pos[0]-1][current_pos[1]] == None:
        #     self.grid.swap_grid_cells(current_pos,bottom_left)
        #     self.x = (current_pos[0]-1)*self.grid.cell_size
        #     self.y = (current_pos[1]+1)*self.grid.cell_size

        # elif self.grid.grid[current_pos[0]+1][current_pos[1]+1] == None and self.grid.grid[current_pos[0]+1][current_pos[1]] == None:
        #     self.grid.swap_grid_cells(current_pos,bottom_right)
        #     self.x = (current_pos[0]+1)*self.grid.cell_size
        #     self.y = (current_pos[1]+1)*self.grid.cell_size

        # elif self.grid.grid[current_pos[0]-1][current_pos[1]] == None:
        #     self.grid.swap_grid_cells(current_pos,left)
        #     self.x = (current_pos[0]-1)*self.grid.cell_size
        #     self.y = (current_pos[1])*self.grid.cell_size

        # elif self.grid.grid[current_pos[0]+1][current_pos[1]] == None:
        #     self.grid.swap_grid_cells(current_pos,right)
        #     self.x = (current_pos[0]+1)*self.grid.cell_size
        #     self.y = (current_pos[1])*self.grid.cell_size

class Wood(Cell):
    def __init__(self, grid: Grid, position, size, color, life_time, velocity, fluid=False) -> None:
        super().__init__(grid, position, size, color, life_time, velocity, fluid)
    
    def update(self):
        pass

class Border(Cell):
    def __init__(self, grid: Grid, position, size, color, life_time, velocity, fluid=False) -> None:
        super().__init__(grid, position, size, color, life_time, velocity, fluid)
    
    def update(self):
        pass

def main():
    Clock = pygame.time.Clock()

    is_paused = False

    brush_size = 5  # TODO ADD DRAWING MORE CELLS WITH A BRUSH SIZE
    current_type = "S"

    grid = Grid(WIDTH,HEIGHT,5)
    grid.generate_grid()
    grid.generate_borders(2)
    
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_paused = not is_paused
            if event.type == pygame.MOUSEWHEEL:
                brush_size += event.y
                if brush_size < 1: brush_size = 1
                if brush_size > 50: brush_size = 50
                
        screen.fill((50,50,50))
        delta = Clock.tick(60)/1000

        if pygame.key.get_pressed()[pygame.K_1]:
            current_type = "S"
        if pygame.key.get_pressed()[pygame.K_2]:
            current_type = "W"
        if pygame.key.get_pressed()[pygame.K_3]:
            current_type = "WO"
        
        mouse = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            pos = grid.get_grid_position(mouse)
            for x in range(brush_size):
                for y in range(brush_size):
                    grid_cell = (pos[0]+x-floor(brush_size/2),pos[1]+y-floor(brush_size/2))
                    if grid_cell[0] < 0 or grid_cell[0] > len(grid.grid)-1 or grid_cell[1] < 0 or grid_cell[1] > len(grid.grid[0])-1: continue
                    if grid.grid[grid_cell[0]][grid_cell[1]] == None :
                        if current_type == "S":
                            cel = Sand(grid,(grid_cell[0]*grid.cell_size,grid_cell[1]*grid.cell_size),grid.cell_size,(250,250,0),-1,1)
                            grid.grid[grid_cell[0]][grid_cell[1]] = cel
                        elif current_type == "W":
                            cel = Water(grid,(grid_cell[0]*grid.cell_size,grid_cell[1]*grid.cell_size),grid.cell_size,(0,0,170),-1,2)
                            grid.grid[grid_cell[0]][grid_cell[1]] = cel
                        elif current_type == "WO":
                            cel = Wood(grid,(grid_cell[0]*grid.cell_size,grid_cell[1]*grid.cell_size),grid.cell_size,(102, 58, 13),-1,1)
                            grid.grid[grid_cell[0]][grid_cell[1]] = cel
        
        if pygame.mouse.get_pressed()[2]:
            pos = grid.get_grid_position(mouse)
            for x in range(brush_size):
                for y in range(brush_size):
                    grid_cell = (pos[0]+x-floor(brush_size/2),pos[1]+y-floor(brush_size/2))
                    if grid_cell[0] < 0 or grid_cell[0] > len(grid.grid)-1 or grid_cell[1] < 0 or grid_cell[1] > len(grid.grid[0])-1: continue
                    if grid.grid[grid_cell[0]][grid_cell[1]] != None and type((grid.grid[grid_cell[0]][grid_cell[1]])) != Border:
                        grid.grid[grid_cell[0]][grid_cell[1]].free()
                        grid.grid[grid_cell[0]][grid_cell[1]] = None

        for cell in reversed(Cell.list_of_cells):
            if not is_paused:
                cell.update()
            cell.draw()

        # draw placement preview
        preview_offset = grid.get_grid_position(((brush_size/2)*grid.cell_size,(brush_size/2)*grid.cell_size))
        placement_preview_grid = grid.get_grid_position((mouse[0],mouse[1]))
        placement_preview_position = (placement_preview_grid[0]-preview_offset[0],placement_preview_grid[1]-preview_offset[1])
        pygame.draw.rect(screen,(255,0,0),(placement_preview_position[0]*grid.cell_size,placement_preview_position[1]*grid.cell_size,brush_size*grid.cell_size,brush_size*grid.cell_size),3)

        #grid.draw_grid_lines()

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()