from copy import deepcopy as dc
import random

directions = ['n', 'e', 's', 'w']

class Car(vehtype):
    def __init__(self):
        self.car_type = random.choices(['car', 'van', 'bus'], weights=[0.7, 0.2, 0.1], k=1)[0]
        self.speed = 1
        self.coming_from = random.choices(dc(directions), weights=[0.25, 0.25, 0.25, 0.25], k=1)[0]

        possibilities = dc(directions)
        possibilities.remove(self.coming_from)
        self.going_to = random.choices(possibilities, weights=[0.25, 0.25, 0.25], k=1)[0]

    def cross(self):
        pass

class Lights(duration_sec):
    def __init__(self):
        self.light_series = [
            {'s': 'stop', 'w': 'go', 'n': 'stop', 'e': 'stop'},
            {'s': 'go', 'w': 'stop', 'n': 'stop', 'e': 'stop'},
            {'s': 'stop', 'w': 'stop', 'n': 'go', 'e': 'stop'},
            {'s': 'stop', 'w': 'stop', 'n': 'stop', 'e': 'go'}
        ]
        self.episode_duration = 20
        self.active_episode = self.light_series[0]

    def change_episode(self):
        active_episode_index = self.light_series.index(self.active_episode)
        active_episode_index += 1
        self.active_episode = self.light_series[active_episode_index]

class Street(coming_from, going_to):
    def __init__(self):
        self.direction = coming_from
        self.going_to = going_to
        self.direction = coming_from + going_to
        self.queue = []

    def car_arrives(self, car):
        self.queue += [car]

    def car_crosses(self):
        self.queue[0].cross()
        self.queue.pop(0)