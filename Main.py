import pygame, math
import CursedUtils as cu
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
    
    def update_cells(self,start_range,end_range):
        for index,_ in enumerate(self.grid,start_range):
            for cell in self.grid[index]:
                if cell != None:
                    cell.update()
            if index == end_range: break
    
    def generate_borders(self,size):
        for s in range(size-1):
            for x in range(self.grid_width):
                border = Border(self,(x*self.cell_size,s*self.cell_size),self.cell_size)
                self.grid[x][s] = border
                border = Border(self,(x*self.cell_size,(self.grid_height-s-1)*self.cell_size),self.cell_size)
                self.grid[x][self.grid_height-s-1] = border
            for y in range(self.grid_height):
                border = Border(self,(s*self.cell_size,y*self.cell_size),self.cell_size)
                self.grid[s][y] = border
                border = Border(self,((self.grid_width-s-1)*self.cell_size,y*self.cell_size),self.cell_size)
                self.grid[self.grid_width-s-1][y] = border

    def draw_grid_lines(self):
        for x in range(self.width+1):
            pygame.draw.line(screen,(30,30,30),(x*self.cell_size,0),(x*self.cell_size,self.height*self.cell_size))
        for y in range(self.height+1):
            pygame.draw.line(screen,(30,30,30),(0,y*self.cell_size),(self.width*self.cell_size,y*self.cell_size))

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
    
    @staticmethod
    def traverse_matrix(start_pos, end_pos):
        if start_pos == None or end_pos == None: return
        if start_pos[0] == end_pos[0] and start_pos[1] == end_pos[1]: return
        list_of_positions = []
        list_of_positions.append(start_pos)

        x_diff = end_pos[0] - start_pos[0]
        y_diff = end_pos[1] - start_pos[1]
        x_diff_is_larger = abs(x_diff) > abs(y_diff)

        x_modifier = 1 if x_diff > 0 else -1
        y_modifier = 1 if y_diff > 0 else -1

        longer_side = max(abs(x_diff),abs(y_diff))
        shorter_side = min(abs(x_diff),abs(y_diff))
        step = 1
        slope = 0 if x_diff == 0 or y_diff == 0 else shorter_side/longer_side
        while step <= longer_side:
            shorter_side_increse = round(step*slope)
            x_increse = 0
            y_increse = 0

            if x_diff_is_larger:
                x_increse = step
                y_increse = shorter_side_increse
            else:
                y_increse = step
                x_increse = shorter_side_increse
            
            x_pos = start_pos[0] + (x_increse*x_modifier)
            y_pos = start_pos[1] + (y_increse*y_modifier)

            list_of_positions.append((x_pos,y_pos))
            step += 1
        return list_of_positions

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

    def __init__(self, grid:Grid, position, size, color) -> None:
        self.x = position[0]
        self.y = position[1]
        self.surface = pygame.Surface((size,size))
        self.rect = self.surface.get_rect(topleft=(self.x,self.y))
        self.rect.topleft = (self.x,self.y)
        self.color = color
        self.grid = grid
        self.surface.fill(self.color)
        Cell.list_of_cells.append(self)

    def update_all():
        for cell in reversed(Cell.list_of_cells):
            cell.update()
    
    def draw_all():
        for cell in Cell.list_of_cells:
            cell.draw()

    def update(self):
        pass
    
    def draw(self):
        screen.blit(self.surface,self.rect)

    def is_type(self, object, class_type) -> bool:
        return issubclass(type(object),class_type)
    
    def free(self):
        Cell.list_of_cells.remove(self)
        del(self)

class Static_Cell(Cell):
    def __init__(self, grid: Grid, position, size, color) -> None:
        super().__init__(grid, position, size, color)

class Fluid(Cell):
    def __init__(self, grid: Grid, position, size, color, velocity, life_time) -> None:
        super().__init__(grid, position, size, color)
        self.velocity = velocity
        self.life_time = life_time

class Sand(Cell):
    def __init__(self, grid: Grid, position, size, color=(250,250,0), velocity=1) -> None:
        super().__init__(grid, position, size, color)
        self.velocity = velocity

    def update(self):
        self.rect.topleft = (self.x,self.y)
        current_pos = self.grid.get_grid_position((self.x,self.y)) 

        bottom = (current_pos[0],current_pos[1]+1)
        bottom_left = (current_pos[0]-1,current_pos[1]+1)
        bottom_right = (current_pos[0]+1,current_pos[1]+1)

        if self.grid.grid[current_pos[0]][current_pos[1]+1] == None:  # TODO FIX THE CRASH AND CELLS GOING DIAGNAL IF THERE IS A BLOCK NEXT TO THEM
            self.grid.swap_grid_cells(current_pos,bottom)
            self.x = current_pos[0]*self.grid.cell_size
            self.y = (current_pos[1]+1)*self.grid.cell_size
            return

        elif self.is_type(self.grid.grid[current_pos[0]][current_pos[1]+1], Water):
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
            elif self.is_type(self.grid.grid[current_pos[0]-1][current_pos[1]+1], Water):
                self.grid.grid[current_pos[0]][current_pos[1]] = self.grid.grid[current_pos[0]-1][current_pos[1]+1]
                self.grid.grid[current_pos[0]-1][current_pos[1]+1].x = self.x = current_pos[0]*self.grid.cell_size
                self.grid.grid[current_pos[0]-1][current_pos[1]+1].y = (current_pos[1])*self.grid.cell_size
                self.grid.grid[current_pos[0]-1][current_pos[1]+1] = self
                self.x = (current_pos[0]-1)*self.grid.cell_size
                self.y = (current_pos[1]+1)*self.grid.cell_size
                return

        if self.grid.grid[current_pos[0]-1][current_pos[1]] != None and self.grid.grid[current_pos[0]-1][current_pos[1]+1] != None:
            if self.is_type(self.grid.grid[current_pos[0]-1][current_pos[1]+1], Water):
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
            if self.is_type(self.grid.grid[current_pos[0]+1][current_pos[1]+1], Water):
                self.grid.grid[current_pos[0]][current_pos[1]] = self.grid.grid[current_pos[0]+1][current_pos[1]+1]
                self.grid.grid[current_pos[0]+1][current_pos[1]+1].x = self.x = current_pos[0]*self.grid.cell_size
                self.grid.grid[current_pos[0]+1][current_pos[1]+1].y = (current_pos[1])*self.grid.cell_size
                self.grid.grid[current_pos[0]+1][current_pos[1]+1] = self
                self.x = (current_pos[0]+1)*self.grid.cell_size
                self.y = (current_pos[1]+1)*self.grid.cell_size
                return
        
        if self.grid.grid[current_pos[0]+1][current_pos[1]] != None and self.grid.grid[current_pos[0]+1][current_pos[1]+1] != None:
            if self.is_type(self.grid.grid[current_pos[0]+1][current_pos[1]+1],Water):
                self.grid.grid[current_pos[0]][current_pos[1]] = self.grid.grid[current_pos[0]+1][current_pos[1]+1]
                self.grid.grid[current_pos[0]+1][current_pos[1]+1].x = self.x = current_pos[0]*self.grid.cell_size
                self.grid.grid[current_pos[0]+1][current_pos[1]+1].y = (current_pos[1])*self.grid.cell_size
                self.grid.grid[current_pos[0]+1][current_pos[1]+1] = self
                self.x = (current_pos[0]+1)*self.grid.cell_size
                self.y = (current_pos[1]+1)*self.grid.cell_size
                return

class Water(Fluid):
    def __init__(self, grid: Grid, position, size, color=(0,0,170), velocity=2, life_time=-1) -> None:
        super().__init__(grid, position, size, color, velocity, life_time)
        self.velocity = velocity
        self.life_time = life_time

    def update(self):
        self.rect.topleft = (self.x,self.y)
        current_pos = self.grid.get_grid_position((self.x,self.y))

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

class Wood(Static_Cell):
    def __init__(self, grid: Grid, position, size, color=(102, 58, 13)) -> None:
        super().__init__(grid, position, size, color)

class Border(Cell):
    def __init__(self, grid: Grid, position, size, color=(20,20,20)) -> None:
        super().__init__(grid, position, size, color)

def main():
    Clock = pygame.time.Clock()

    sand_button = cu.Button((WIDTH-60,50),(40,40),(250,250,0),"Sand",(0,0,0),20,border=2)
    water_button = cu.Button((WIDTH-60,100),(40,40),(0,0,170),"water",(0,0,0),20,border=2)
    wood_button = cu.Button((WIDTH-60,150),(40,40),(102, 58, 13),"wood",(0,0,0),20,border=2)

    fps_button = cu.Button((10,10),(40,10),text=60,border=0,text_color=(0,0,0))

    brush_size = 5  # TODO ADD DRAWING MORE CELLS WITH A BRUSH SIZE
    current_type = Sand

    grid = Grid(WIDTH,HEIGHT,10)
    grid.generate_grid()
    grid.generate_borders(2)

    previous_mouse_pos = None

    show_grid_lines = True
    is_paused = False
    is_running = True
    while is_running:
        previous_mouse_pos = grid.get_grid_position(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_paused = not is_paused
                if event.key == pygame.K_q:
                    show_grid_lines = not show_grid_lines
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    cu.events.append(cu.MOUSE_LEFT)
            if event.type == pygame.MOUSEWHEEL:
                brush_size += event.y
                if brush_size < 1: brush_size = 1
                if brush_size > 50: brush_size = 50
                
        screen.fill((50,50,50))
        delta = Clock.tick(60)/1000

        if pygame.key.get_pressed()[pygame.K_1] or sand_button.is_pressed:
            current_type = Sand
        if pygame.key.get_pressed()[pygame.K_2] or water_button.is_pressed:
            current_type = Water
        if pygame.key.get_pressed()[pygame.K_3] or wood_button.is_pressed:
            current_type = Wood
        
        mouse = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0] and not cu.UI.is_over_ui:
            pos = grid.get_grid_position(mouse)
            for x in range(brush_size):
                for y in range(brush_size):
                    grid_cell = (pos[0]+x-floor(brush_size/2),pos[1]+y-floor(brush_size/2))
                    if grid_cell[0] < 0 or grid_cell[0] > len(grid.grid)-1 or grid_cell[1] < 0 or grid_cell[1] > len(grid.grid[0])-1: continue
                    positions = Grid.traverse_matrix((previous_mouse_pos[0]+x-floor(brush_size/2),previous_mouse_pos[1]+y-floor(brush_size/2)),grid_cell)
                    if positions == None: positions = [grid_cell]
                    for position in positions:
                        if position[0] < 0 or position[0] > len(grid.grid)-1 or position[1] < 0 or position[1] > len(grid.grid[0])-1: continue
                        if grid.grid[position[0]][position[1]] == None :
                            cel = current_type(grid,(position[0]*grid.cell_size,position[1]*grid.cell_size),grid.cell_size)
                            grid.grid[position[0]][position[1]] = cel

        if pygame.mouse.get_pressed()[2] and not cu.UI.is_over_ui:
            pos = grid.get_grid_position(mouse)
            for x in range(brush_size):
                for y in range(brush_size):
                    grid_cell = (pos[0]+x-floor(brush_size/2),pos[1]+y-floor(brush_size/2))
                    if grid_cell[0] < 0 or grid_cell[0] > len(grid.grid)-1 or grid_cell[1] < 0 or grid_cell[1] > len(grid.grid[0])-1: continue
                    positions = Grid.traverse_matrix((previous_mouse_pos[0]+x-floor(brush_size/2),previous_mouse_pos[1]+y-floor(brush_size/2)),grid_cell)
                    if positions == None: positions = [grid_cell]
                    for position in positions:
                        if position[0] < 0 or position[0] > len(grid.grid)-1 or position[1] < 0 or position[1] > len(grid.grid[0])-1: continue
                        if grid.grid[position[0]][position[1]] != None and type((grid.grid[position[0]][position[1]])) != Border:
                            grid.grid[position[0]][position[1]].free()
                            grid.grid[position[0]][position[1]] = None


        cu.update()
        if not is_paused:
            Cell.update_all()
        Cell.draw_all() 
        # draw placement preview
        preview_offset = grid.get_grid_position(((brush_size/2)*grid.cell_size,(brush_size/2)*grid.cell_size))
        placement_preview_grid = grid.get_grid_position((mouse[0],mouse[1]))
        placement_preview_position = (placement_preview_grid[0]-preview_offset[0],placement_preview_grid[1]-preview_offset[1])
        pygame.draw.rect(screen,(255,0,0),(placement_preview_position[0]*grid.cell_size,placement_preview_position[1]*grid.cell_size,brush_size*grid.cell_size,brush_size*grid.cell_size),3)

        if show_grid_lines:
            grid.draw_grid_lines()
        cu.draw(screen)
        pygame.display.flip()
        print(f'game loop-{round(delta*1000, 3)} ms    ammount of cells-{len(Cell.list_of_cells)}')
        fps_button.text = round(1000/(delta*1000))
    pygame.quit()


if __name__ == '__main__':
    main()