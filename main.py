from grid import TrafficLightGrid, FourWayStop
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from functools import partial

# Cellular Automata in Traffic
# Group: Nikhil Thimmadasaiah, Nem Mehta, Shonn Vinchurkar
# 
# There are a series of customizable parameters below, with comments to describe their functions

# **BEGIN CUSTOMIZABLE PARAMETERS**

# Simulation Parameters
steps_per_epoch=100         # Number of steps per epoch
num_epochs=1              # Number of epochs, each epoch records congestion value once at the end
traffic_system=1            # Chooses the traffic system implementation (0: Traffic Light, 1: 4-Way Stop)

# Grid Parameters
n=3                         # Forms an n x n grid of intersections
road_length=20              # Number of cells before, after, and between each intersection
car_join_interval=10        # Number of steps before a car tries to join the grid
right_turn_probability=0.33 # Probability of a car turning right, as opposed to going straight

# Animation Parameters
create_animation=True      # Takes significantly longer, otherwise just measures and plots congestion values
delayed_start=0             # Number of epochs to update normally before starting the animation
fps=30                      # Frames per second speed of the animation
animation_name='4WayStop_animation'  # animation saved as [animation_name].gif

# Traffic Light Parameter
light_timer=50              # time spent before changing lights, in steps


# **END CUSTOMIZABLE PARAMETERS**

if create_animation and delayed_start>=num_epochs:
    raise ValueError("delayed_start must be lower than epochs")

if traffic_system==0:
    grid=TrafficLightGrid(num_of_roads=n, road_length=road_length, right_turn_prob=right_turn_probability)
else:
    grid=FourWayStop(num_of_roads=n, road_length=road_length, right_turn_prob=right_turn_probability)


def update(total_step:int, last_step:bool):
    # Adding cars at Grid edges
    for i, key in enumerate(grid.road_dict.keys()):
        if grid.waiting_for_insertion[i]:
            grid.waiting_for_insertion[i]=not(grid.try_inserting_car(key))
    
    if total_step%car_join_interval==0:
        for i, key in enumerate(grid.road_dict.keys()):
            if not grid.waiting_for_insertion[i]:
                grid.waiting_for_insertion[i]=not(grid.try_inserting_car(key))
                
    # Enabling and disabling the apropriate barriers
    if traffic_system==0:   # Traffic Lights
        if total_step%light_timer==0:
            grid.changed_lights=[False] * (n**2)
        if (False in grid.changed_lights):
            grid.update_traffic_system(total_step, light_timer)
    else:                   # Four Way Stop
        grid.update_traffic_system()
    
    # Update car positions
    for key in grid.road_dict.keys():
        for i in range((grid.L+n-1), -1, -1):
            if grid.road_dict[key][i].state==1:
                grid.move_next(key, i)
    
    if last_step:
        grid.results.append(grid.measure_congestion())


def animate(frame, steps_per_epoch):
    last_step = (frame%steps_per_epoch)==(steps_per_epoch-1)
    update(frame, last_step)
    car_locations=grid.get_car_locations()
    for i, sq in enumerate(grid.squares):
        if i < len(car_locations):
            y, x = car_locations[i]     # reversed x and y to match matplotlib convention
            sq.set_xy((x, y))
            sq.set_visible(True)
        else:
            sq.set_visible(False)
    return grid.squares

def init():
    for square in grid.squares:
        square.set_xy((0, 0))
    return grid.squares

if create_animation:
    for frame in range(delayed_start*steps_per_epoch):
        last_step = (frame%steps_per_epoch)==(steps_per_epoch-1)
        update(frame, last_step)
    ani = animation.FuncAnimation(grid.fig, partial(animate, steps_per_epoch=steps_per_epoch), frames=range(delayed_start*steps_per_epoch, num_epochs*steps_per_epoch), init_func=init, blit=True, repeat=False)
    ani.save(f'{animation_name}.gif', writer='pillow', fps=fps)
else:
    for frame in range(num_epochs*steps_per_epoch):
        last_step = (frame%steps_per_epoch)==(steps_per_epoch-1)
        update(frame, last_step)

plt.figure()

# Plotting results
print(grid.results)

epochs = range(num_epochs+1)
plt.plot(epochs, grid.results)
labels={0:"Traffic Light System",
        1:"4-Way Stop System"}
plt.title(labels[traffic_system])
plt.xlabel("Epoch")
plt.ylabel("Congestion (Number of stuck cars)")

    
plt.show()