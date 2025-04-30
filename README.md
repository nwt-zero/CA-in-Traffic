# What the Code Does
**Together**, these 3 files produce a Cellular Automata that can simulate one of 2 different patterns of traffic flow at intersections:

- Traffic Light Signalling System
- 4-Way Stop (Right-of-way signalling)

The execution of the code results in the output of a **matplotlib plot graph** and, if enabled, a **gif animation file**.

# How to Run the Code
The code can be run by running the main.py file. Main.py also contains many customizable parameters near the top of the file that can be changed freely to view differing circumstances. The customizable parameters are described within the code, but there's also a description of them below.

You may need to install Pillow (`pip install pillow`) in order to run the code. Other than that, the libraries involved are most likely already installed.

# Customizable Parameters
### Simulation Parameters

- steps_per_epoch: Number of steps per epoch
- num_epochs: Number of epochs, end of each epoch records congestion value once
- traffic_system: Chooses the traffic system implementation (0: Traffic Light, 1: 4-Way Stop)


### Grid Parameters

- n: Forms an n x n grid of intersections
- road_length: Number of cells before, after, and between each intersection
- car_join_interval: Number of steps before a car tries to join the grid
- right_turn_probability: Probability of a car turning right, as opposed to going straight


### Animation Parameters

- create_animation: Enables creation of an animation (takes significantly longer), otherwise just measures and plots congestion values
- delayed_start: Number of epochs to update normally before starting the animation
- fps: Frames per second speed of the animation file
- animation_name: animation saved as [animation_name].gif


### Traffic Light Parameter

- light_timer: time spent before changing lights, in steps