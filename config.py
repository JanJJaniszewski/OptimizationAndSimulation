import logging
from copy import deepcopy as dc
import numpy as np
import random
from itertools import cycle

# Basics
ticks = 3600
paths = ['ne', 'ns', 'nw', 'en', 'es', 'ew', 'sn', 'se', 'sw', 'wn', 'we', 'ws']

# Logging

# Simulation

# Vehicle Generator
generator_length = ticks*len(paths)
vehicle_type_cycle = cycle(random.choices(['car', 'van'], weights=[8101, 828], k=generator_length))
service_time_cycles = {
    # CAN BE CHANGED
    'car': cycle(np.random.exponential(4, size=generator_length)), # looked up by Fengtao
    'van': cycle(np.random.exponential(6, size=generator_length)) # 1.5 * car
    ################
}
# CAN BE CHANGED
arrival_time_cycle = cycle(np.random.exponential(scale=1, size=generator_length)) # Experiment for max for steady state
slowdown_cycles = cycle(np.random.exponential(1, size=generator_length))
################

# Car
# WE: Main
# NS: Side
# CAN BE CHANGED
path_distribution = {
    'ne': 0.25,
    'nw': 0.25,
    'ns': 0.1,
    'ew': 0.75,
    'en': 0.5,
    'es': 0.5,
    'sw': 0.25,
    'se': 0.25,
    'sn': 0.1,
    'we': 0.5,
    'wn': 0.25,
    'ws': 0.25}
################

path_choice_cycle = cycle(random.choices(list(path_distribution.keys()), weights=list(path_distribution.values()), k=generator_length))

# Traffic Light
traffic_light_all_stop = {x: ('stop' if x not in ['ws', 'nw', 'se', 'en'] else 'go') for x in paths}
# CAN BE CHANGED
traffic_light_crossing_block_in_ticks = 10
traffic_light_episode_durations = cycle([20, 30, 20, 30]) # Experiment
number_of_traffic_light_episodes = 4
################
traffic_light_series = [dc(traffic_light_all_stop) for x in range(0, number_of_traffic_light_episodes)]
episode_type = cycle(['go', 'block'])

# Experiment with this (also randomize the order?)
# CAN BE CHANGED
traffic_light_series[0].update({'ne':'go', 'ns':'go', 'nw':'go'})
traffic_light_series[1].update({'we':'go', 'ws':'go', 'wn':'go'})
traffic_light_series[2].update({'se':'go', 'sn':'go', 'sw':'go'})
traffic_light_series[3].update({'en':'go', 'es':'go', 'ew':'go'})
################

traffic_light_series = cycle(traffic_light_series)
