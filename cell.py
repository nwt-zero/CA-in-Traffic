'''This file defines many classes: 
- Cell and its derived classes
    - Road - A forward-only road cell
    - Intersection - A road cell with the option to enable right turns as well
    - Barrier - A blocking cell that restricts cars from moving forward
- IntersectionBlock - A 4-way intersection containing Intersection cells and 4 Barriers'''

class Cell():
    '''The Cell class is a Base Class representing a single square cell on a Grid.
    
    **Attributes**
    - state - A number describing the state of the cell'''
    def __init__(self, state:int):
        self.state=state            # State of the cell: 0 is empty, 1 is car, 2 is barrier


class Road(Cell):
    '''A forward-only road cell
    
    **Attributes**
    - state - An integer describing the state of the cell
    - car_stuck - A Boolean describing if the car is stopped from moving
    - location - A tuple describing the coordinates of the cell on the grid'''
    def __init__(self, state:int):
        if state not in [0, 1]:
            raise ValueError("Invalid Road state")

        super().__init__(state)
        self.car_stuck=False        # Car is counted as congestion if True
        self.location=()            # coordinate of Road cell

class Intersection(Cell):
    '''A road cell with the option to enable right turns as well
    
    **Attributes**
    - state - An integer describing the state of the cell
    - car_stuck - A Boolean describing if the car is stopped from moving
    - location - A tuple describing the coordinates of the cell on the grid
    - turnable - A Boolean describing if turning is allowed in this cell
    - intersection_id - An integer representing this cell'''
    def __init__(self, state:int, turnable:bool=False):
        if state not in [0, 1]:
            raise ValueError("Invalid Intersection state")

        super().__init__(state)
        self.car_stuck=False        # Car is counted as congestion if True
        self.location=()            # coordinate of Intersection cell
        self.turnable=turnable      # If the car can "turn right" from this cell
        self.intersection_id=id     # the id of the IntersectionBlock the cell belongs to

class Barrier(Cell):
    '''A road cell with the option to enable right turns as well
    
    **Attributes**
    - state - An integer describing the state of the cell
    - prev_cell - A reference to the previous cell from the POV of a forward-only road
    - blocking - A Boolean describing if the Barrier is enabled'''
    def __init__(self, cell):
        self.state=2
        self.prev_cell=cell
        self.blocking=True


#Conatins a set of Intersection cells and 4 barriers that control intersection access
class IntersectionBlock():
    '''A 4-way intersection, containing Intersection cells and 4 Barriers
    
    **Attributes**
    - id - An integer representing this collection
    - cells - A list holding references to multiple Intersection cells
    - north/south/east/west_barrier - References to the 4 Barriers associated with the IntersectionBlock'''
    def __init__(self, id):
        self.id=id
        self.cells=[]
        self.north_barrier:Barrier
        self.south_barrier:Barrier
        self.east_barrier:Barrier
        self.west_barrier:Barrier

    def car_in_intersection(self):
        for cell in self.cells:
            if cell.state==1:
                return True
        #else
        return False
