import logging
import copy

# Basics
directions = ['n', 'e', 's', 'w']
paths = ['ne', 'ns', 'nw', 'en', 'es', 'ew', 'sn', 'se', 'sw', 'wn', 'we', 'ws']

# Logging
logging.basicConfig(level=logging.INFO)

# Simulation

# Car
coming_from_weights = [0.25, 0.25, 0.25, 0.25]
going_to_weights = [0.25, 0.25, 0.25]

# Traffic Light
traffic_light_episode_duration = 20
traffic_light_series = [
    {'ne': 'stop',
    'ns': 'stop',
    'nw': 'stop',
    'en': 'stop',
    'es': 'stop',
    'ew': 'stop',
    'sn': 'stop',
    'se': 'stop',
    'sw': 'stop',
    'wn': 'stop',
    'we': 'stop',
    'ws': 'stop'} for x in range(0, 4)
        ]

traffic_light_series[0].update({'ne':'go', 'ns':'go', 'nw':'go'})
traffic_light_series[1].update({'we':'go', 'ws':'go', 'wn':'go'})
traffic_light_series[2].update({'se':'go', 'sn':'go', 'sw':'go'})
traffic_light_series[3].update({'en':'go', 'es':'go', 'ew':'go'})


# Road
road_paths = paths
