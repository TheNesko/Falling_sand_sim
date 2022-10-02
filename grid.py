import math, pygame
import numpy as np


class Grid():
    def __init__(self,width:int,height:int,cell_size:int=1) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = round(self.width/self.cell_size)+1
        self.grid_height = round(self.height/self.cell_size)+1
        self.grid = np.full((self.grid_width,self.grid_height),None)

    def draw_grid_lines(self,screen):
        for x in range(self.width+1):
            pygame.draw.line(screen,(40,40,40),(x*self.cell_size,0),(x*self.cell_size,self.height*self.cell_size))
        for y in range(self.height+1):
            pygame.draw.line(screen,(40,40,40),(0,y*self.cell_size),(self.width*self.cell_size,y*self.cell_size))

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

    # traverse matrix is heavy on performance but smoothes the drawing of cells
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

    def get_cell(self, pos):
        if self.is_in_grid_bounds(pos):
            return self.grid[pos[0]][pos[1]]

    def get_grid_position(self,position):
        return math.floor(position[0]/self.cell_size), math.floor(position[1]/self.cell_size)

    def get_world_position(self,position):
        return math.floor(position[0]*self.cell_size), math.floor(position[1]*self.cell_size)
    
    def get_in_grid_space(self,number):
        return math.floor(number/self.cell_size)
    
    def get_in_world_space(self,number):
        return math.floor(number*self.cell_size)
    
    def is_in_grid_bounds(self,pos):
        if pos[0] >= 0 and pos[0] < (self.grid_width-1) and pos[1] >= 0 and pos[1] < (self.grid_height-1):
            return True
        return False


