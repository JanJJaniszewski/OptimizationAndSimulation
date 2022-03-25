from copy import deepcopy as dc
import config as cf
import random

class VehicleGenerator():
    def __init__(self):
        pass

    def generate_vehicle(self):
        vehicle_type = random.choices(['car', 'van', 'bus'], weights=[0.7, 0.2, 0.1], k=1)[0]
        max_speed = 1


class Simulation():
    def __init__(self):
        self.clock = 0

    def initiate(self):
        self.traffic_light = Lights(cf.traffic_light_episode_duration)
        self.roads =

    def create_road(self, start, end):
        road = Road(start, end)
        self.roads.append(road)
        return road

    def create_roads(self, road_list):
        for road in road_list:
            self.create_road(*road)

    def check_if_vehicle_arrives(self):
        vehicle_arrives = random.choice([0,0,0,0,0,1])
        if vehicle_arrives:
            vehicle = self.vehicle_generator.generate_vehicle()

        return vehicle


    def update(self):
        self.clock += 1
        self.traffic_light.update()


class Car():
    def __init__(self, vehicle_type):
        self.vehicle_type = vehicle_type
        self.speed = 1
        self.coming_from = random.choices(dc(cf.directions), weights=[0.25, 0.25, 0.25, 0.25], k=1)[0]

        possibilities = dc(cf.directions)
        possibilities.remove(self.coming_from)
        self.going_to = random.choices(possibilities, weights=[0.25, 0.25, 0.25], k=1)[0]

    def cross(self):
        pass

    def stop(self):
        self.stopped = True

    def unstop(self):
        self.stopped = False

    def slow_down(self, v):
        self.v = 1

    def speed_up(self):
        self.v = 0.5

class Lights():
    def __init__(self, duration_sec):
        self.light_series = [
            {'s': 'stop', 'w': 'go', 'n': 'stop', 'e': 'stop'},
            {'s': 'go', 'w': 'stop', 'n': 'stop', 'e': 'stop'},
            {'s': 'stop', 'w': 'stop', 'n': 'go', 'e': 'stop'},
            {'s': 'stop', 'w': 'stop', 'n': 'stop', 'e': 'go'}
        ]
        self.episode_duration = duration_sec
        self.active_episode = self.light_series[0]
        self.ticks_left = self.episode_duration

    def change_episode(self):
        active_episode_index = self.light_series.index(self.active_episode)
        active_episode_index += 1
        self.active_episode = self.light_series[active_episode_index]

    def lower_counter(self, ticks_passed):
        self.ticks_left -= ticks_passed

    def renew_counter(self):
        self.ticks_left = self.episode_duration

    def update(self, ticks_passed):
        self.lower_counter(ticks_passed)
        if self.ticks_left == 0:
            self.change_episode()
            self.renew_counter()

class Road():
    def __init__(self, coming_from, going_to):
        self.direction = coming_from
        self.going_to = going_to
        self.direction = coming_from + going_to
        self.length = 10
        self.queue = []

    def car_arrives(self, car):
        self.queue += [car]

    def car_crosses(self):
        self.queue[0].cross()
        self.queue.pop(0)