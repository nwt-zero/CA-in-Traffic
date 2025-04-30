class Cell():
    def __init__(self, state:int):
        self.state=state            # State of the cell: 0 is empty, 1 is car, 2 is barrier
        
        
class Road(Cell):
    def __init__(self, state:int):
        if state not in [0, 1]:
            print("Invalid Road state")
            
        self.state=state            # State 0 is empty spot, 1 is car-filled spot
        self.car_stuck=False        # Car is counted as congestion if True
        self.location=()            # coordinate of Road cell

class Intersection(Cell):
    def __init__(self, state:int, turnable:bool=False):
        if state not in [0, 1]:
            print("Invalid Intersection state")
            
        self.state=state            # State 0 is empty spot, 1 is car-filled spot
        self.car_stuck=False        # Car is counted as congestion if True
        self.location=()            # coordinate of Intersection cell
        self.turnable=turnable      # If the car can "turn right" from this cell
        self.intersection_id=id     # the id of the IntersectionBlock the cell belongs to
        
class Barrier(Cell):
    def __init__(self, cell):
        self.state=2
        self.prev_cell=cell
        self.blocking=True
        

#Conatins a set of Intersection cells and the 4 barriers
class IntersectionBlock():
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
            
        return False