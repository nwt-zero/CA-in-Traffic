from cell import Road, Intersection, Barrier, IntersectionBlock
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from functools import partial
import random


class Grid():
    def __init__(self, num_of_roads:int=1, road_length:int=20, right_turn_prob:float=0.33):
        directions={"north", "south", "east", "west"}   # The 4 directions of roads
        
        # Initializing various important attributes
        self.right_turn_prob=right_turn_prob
        self.num_of_roads=num_of_roads
        self.road_length=road_length
        self.L = (road_length + 2) * num_of_roads + road_length # side length of the grid when plotted
        self.map=[[-1] * self.L for _ in range(self.L)]         # static background used for matplotlib visual of CA
        
        self.intersections:list[IntersectionBlock]=[]
        for i in range(num_of_roads**2):
            self.intersections.append(IntersectionBlock(i))
        
        self.road_dict=dict()
        for direction in directions:
            for i in range(num_of_roads):
                road=f"{direction}_road_{i}"
                self.road_dict.update({road: []})
        
        for key in self.road_dict.keys():
            for _ in range(num_of_roads):
                #Insert straight road
                self.road_dict[key].extend([Road(0) for _ in range(road_length-1)])
                cell=Road(0)
                self.road_dict[key].append(cell)
                #Insert barrier
                self.road_dict[key].append(Barrier(cell))
                #Insert Intersection cells
                self.road_dict[key].append(Intersection(0, turnable=True))
                self.road_dict[key].append(Intersection(0))
            
            #Insert straight road
            self.road_dict[key].extend([Road(0) for _ in range(road_length)])
            
        
        # Adds location coordinates to each Road and Intersection object
        # Also adds Intersection objects into the right IntersectionBlock
        segment_length=self.road_length+2
        for segment_index in range(self.num_of_roads):
            row_col_index = segment_index*segment_length + self.road_length
            
            east_road=[cell for cell in reversed(self.road_dict[f'east_road_{segment_index}']) if cell.state!=2]
            for i, cell in enumerate(east_road):
                cell.location=(row_col_index, i)
                if isinstance(cell, Intersection):
                    self.intersections[num_of_roads*segment_index+(i//segment_length)].cells.append(cell)
                    cell.intersection_id=num_of_roads*segment_index+(i//segment_length)
                
            west_road=[cell for cell in self.road_dict[f'west_road_{segment_index}'] if cell.state!=2]
            for i, cell in enumerate(west_road):
                cell.location=(row_col_index+1, i)
                if isinstance(cell, Intersection):
                    self.intersections[num_of_roads*segment_index+(i//segment_length)].cells.append(cell)
                    cell.intersection_id=num_of_roads*segment_index+(i//segment_length)
                
            north_road=[cell for cell in self.road_dict[f'north_road_{segment_index}'] if cell.state!=2]
            for i, cell in enumerate(north_road):
                cell.location=(i, row_col_index)
                if isinstance(cell, Intersection):
                    self.intersections[num_of_roads*(i//segment_length)+segment_index].cells.append(cell)
                    cell.intersection_id=num_of_roads*(i//segment_length)+segment_index
                
            south_road=[cell for cell in reversed(self.road_dict[f'south_road_{segment_index}']) if cell.state!=2]
            for i, cell in enumerate(south_road):
                cell.location=(i, row_col_index+1)
                if isinstance(cell, Intersection):
                    self.intersections[num_of_roads*(i//segment_length)+segment_index].cells.append(cell)
                    cell.intersection_id=num_of_roads*(i//segment_length)+segment_index
                
            # Adding the barriers into each IntersectionBlock
            east_barriers=[cell for cell in reversed(self.road_dict[f'east_road_{segment_index}']) if cell.state==2]
            west_barriers=[cell for cell in self.road_dict[f'west_road_{segment_index}'] if cell.state==2]
            north_barriers=[cell for cell in self.road_dict[f'north_road_{segment_index}'] if cell.state==2]
            south_barriers=[cell for cell in reversed(self.road_dict[f'south_road_{segment_index}']) if cell.state==2]
            for i in range(num_of_roads):
                self.intersections[num_of_roads*segment_index+i].east_barrier=east_barriers[i]
                self.intersections[num_of_roads*segment_index+i].west_barrier=west_barriers[i]
                self.intersections[num_of_roads*i+segment_index].north_barrier=north_barriers[i]
                self.intersections[num_of_roads*i+segment_index].south_barrier=south_barriers[i]
            
            # self.map will be a static image of the grid with empty roads
            # setting all road cell spots to empty roads below
            self.map[row_col_index] = [0 for _ in range(self.L)]
            self.map[row_col_index+1] = [0 for _ in range(self.L)]
            
            for i in range(self.L):
                self.map[i][row_col_index+1] = 0
                self.map[i][row_col_index] = 0

            
        self.fig_init()
        self.results=[self.measure_congestion()]
    
    def fig_init(self):
        color_map={-1:partial(Rectangle, width=1, height=1, color='white'),
                    0: partial(Rectangle, width=1, height=1, color='gray')}
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.L)
        ax.set_ylim(0, self.L)
        ax.invert_yaxis()
        ax.set_aspect('equal')
        for i in range(self.L):
            for j in range(self.L):
                ax.add_patch(color_map[self.map[i][j]](xy=(i, j)))

        max_num = self.L * 4 * self.num_of_roads
        self.squares = [Rectangle((0, 0), 1, 1, color='red', visible=False) for _ in range(max_num)]
        for square in self.squares:
            ax.add_patch(square)

        self.fig, self.ax = fig, ax

    def get_car_locations(self):
        car_locations=[]
        for key in self.road_dict.keys():
            for cell in self.road_dict[key]:
                if cell.state==1:
                    car_locations.append(cell.location)
        return car_locations


    def try_inserting_car(self, key:str):
        cell=self.road_dict[key][0]
        if cell.state==0:
            cell.state=1
            return True # Successfully added car
        return False # Cell not empty, failed to add car
    
    # Move a car forward by one spot, if possible
    def move_next(self, key, i):
        cell=self.road_dict[key][i]
        
        # if cell is at end of road
        if i==(self.L+self.num_of_roads - 1):
            # remove car
            cell.state=0
            return None
        
        
        next_cell=self.road_dict[key][i+1]
        
        # If on a right-turn cell
        if isinstance(cell, Intersection) and cell.turnable==True:
            # Chance to turn right
            if random.random() < self.right_turn_prob:
                # Calculating coordinates of new next_cell
                prev_cell=self.road_dict[key][i-2]
                x, y = tuple(a - b for a, b in zip(cell.location, prev_cell.location))
                if x==0:
                    next_cell_location=list(cell.location)
                    next_cell_location[0]+=y
                    next_cell_location=tuple(next_cell_location)
                else:
                    next_cell_location=list(cell.location)
                    next_cell_location[1]-=x
                    next_cell_location=tuple(next_cell_location)
                
                # Reassigning cell to other Intersection cell at same location and next_cell to corresponding cell
                cell=self.turn_right(cell)
                next_cell=[cell for cell in self.road_dict[self.turn_right_road(key, next_cell_location)] if not isinstance(cell, Barrier) and cell.location==next_cell_location][0]
        
        # If next cell is a non-blocking barrier
        if next_cell.state==2 and not next_cell.blocking:
            next_cell=self.road_dict[key][i+2]
        
        # If next cell is empty
        if next_cell.state==0:
            cell.state=0
            cell.car_stuck=False
            next_cell.state=1
        
        # If next cell is a car      
        elif next_cell.state==1:
            cell.car_stuck=True
        
        # If next cell is a blocking barrier
        elif next_cell.state==2 and next_cell.blocking:
            cell.car_stuck=True
            
            
    def turn_right(self, cell:Intersection):
        matching_cells = [cell2 for cell2 in self.intersections[cell.intersection_id].cells if cell.location==cell2.location]
        if matching_cells[0].turnable==False:
            cell2=matching_cells[0]
        else:
            cell2=matching_cells[1]
        
        cell2.state=1
        cell.state=0
        return cell2
    
    def turn_right_road(self, road_name:str, location:tuple):
        road_name = road_name.split("_")
        row_col_indexes=list(range(self.road_length, self.L, (self.road_length+2))) + list(range((self.road_length+1), self.L, (self.road_length+2)))

        if road_name[0]=="east":
            road_name[0]="south"
        elif road_name[0]=="south":
            road_name[0]="west"
        elif road_name[0]=="west":
            road_name[0]="north"
        elif road_name[0]=="north":
            road_name[0]="east"
        
        segment_index = [x//(self.road_length+2) for x in location if x in row_col_indexes]
        road_name[2]=str(segment_index[0])
        
        return "_".join(road_name)
    
    # Scans each road in road_dict and counts total number of stuck cars
    def measure_congestion(self):
        congestion=0
        for key in self.road_dict.keys():
            for cell in self.road_dict[key]:
                if cell.state==1 and cell.car_stuck==True:
                    congestion += 1
        return congestion

class TrafficLightGrid(Grid):
    def __init__(self, num_of_roads:int, road_length:int, right_turn_prob:float):
        super().__init__(num_of_roads=num_of_roads, road_length=road_length, right_turn_prob=right_turn_prob)
        self.waiting_for_insertion=[False] * (4*num_of_roads)
        self.changed_lights=[False] * (num_of_roads**2)
        
    def update_traffic_system(self, total_step, light_timer):
        light_cycle = (total_step//light_timer) % 2
        if light_cycle==1:
            goal_lights=[True, False, True, False]  # blocking states for the north, west, south, and east barriers
        else:
            goal_lights=[False, True, False, True]  # North and South are unblocked, East and West are blocked
        
        for i, intersection in enumerate(self.intersections):
            # For unchanged lights (that need to be changed) and an empty intersection
            if not self.changed_lights[i] and not intersection.car_in_intersection():
                intersection.north_barrier.blocking, intersection.west_barrier.blocking, intersection.south_barrier.blocking, intersection.east_barrier.blocking = goal_lights
                self.changed_lights[i] = True
            # For unchanged lights with a non-empty intersection
            elif not self.changed_lights[i]:
                intersection.north_barrier.blocking, intersection.west_barrier.blocking, intersection.south_barrier.blocking, intersection.east_barrier.blocking = [True] * 4
                
        


class FourWayStop(Grid):
    def __init__(self, num_of_roads:int, road_length:int, right_turn_prob:float):
        super().__init__(num_of_roads=num_of_roads, road_length=road_length, right_turn_prob=right_turn_prob)
        self.waiting_for_insertion=[False] * (4*num_of_roads)
        self.in_order=[False] * (num_of_roads**2)
        self.next_barrier=[None] * (num_of_roads**2)
        
    def update_traffic_system(self):
        for i, intersection in enumerate(self.intersections):
            if not intersection.car_in_intersection():
                cars_waiting=[intersection.east_barrier.prev_cell.state, intersection.south_barrier.prev_cell.state, intersection.west_barrier.prev_cell.state, intersection.north_barrier.prev_cell.state]
                if sum(cars_waiting)==0:
                    continue
                
                elif sum(cars_waiting)>=1:
                    self.car_barrier_open(cars_waiting, i)
                    
            else:
                intersection.east_barrier.blocking, intersection.south_barrier.blocking, intersection.west_barrier.blocking, intersection.north_barrier.blocking = [True] * 4
    
    def car_barrier_open(self, cars_waiting, i):
        if sum(cars_waiting)==1:
            self.open_first_barrier(cars_waiting, i, 0)
            self.in_order[i]=False
            
        elif sum(cars_waiting)>=2:
            if self.in_order[i]:
                self.next_barrier[i] = self.open_first_barrier(cars_waiting, i, self.next_barrier[i])
            else:
                 self.next_barrier[i] = self.open_first_barrier(cars_waiting, i, 0)
            
            self.in_order[i] = True
            
    def open_first_barrier(self, cars_waiting:list[int], i:int, cur_barrier:int):
        # Look for first barrier with a waiting car, starting from cur_barrier
        barriers=[0, 1, 2, 3]
        barriers=barriers[cur_barrier:] + barriers[:cur_barrier]
        for j in barriers:
            if cars_waiting[j]==1:
                break
        
        barrier_dict={0:self.intersections[i].east_barrier,
                      1:self.intersections[i].south_barrier,
                      2:self.intersections[i].west_barrier,
                      3:self.intersections[i].north_barrier}
        
        barrier_dict[j].blocking=False
        next_barrier = (j+1) % 4
        return next_barrier