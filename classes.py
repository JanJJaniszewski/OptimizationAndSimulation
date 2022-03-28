from copy import deepcopy as dc
from time import sleep

import config as cf
import random
import logging

class VehicleGenerator():
    # The client generation function
    def __init__(self):
        self.vehicle_types = ['car', 'van', 'bus']
        self.distribution = [0.7, 0.2, 0.1]

    def generate_vehicle(self):
        vehicle_type = random.choices(self.vehicle_types, weights=self.distribution, k=1)[0]
        max_speed = 1
        return car

class Simulation():
    # Simulation
    def __init__(self):
        self.clock = 0
        self.traffic_light = Lights(cf.traffic_light_episode_duration)
        self.roads = self.create_roads(cf.road_paths)
        self.vehicle_generator = VehicleGenerator()
        self.intersection = Intersection(size = 10)

    def create_road(self, path):
        start = path[0]
        end = path[1]
        road = Road(start, end)
        return road

    def create_roads(self, road_list):
        roads = dict()
        for road in road_list:
            new_road = self.create_road(road)
            roads[road] = new_road

        return roads

    def check_if_vehicle_arrives(self):
        vehicle_arrives = random.choice([0,0,0,0,1,1])
        if vehicle_arrives:
            vehicle = self.vehicle_generator.generate_vehicle()
            logging.info(f'New vehicle arrives in path {vehicle.path}')
            to_return = vehicle
        else:
            to_return = False

        return to_return

    def update(self, ticks_passed = 1):
        # Update t
        sleep(1)
        self.clock += ticks_passed

        # Update server state
        self.traffic_light.update(ticks_passed = ticks_passed)

        # Client arrival
        vehicle = self.check_if_vehicle_arrives()
        if vehicle:
            self.roads[vehicle.path].queue.append(vehicle) # Add car to queue of waiting cars (if any wait)

        for path, road in self.roads:
            # Serve clients
            if (self.traffic_light.active_episode[path] == 'go') and not self.traffic_light.blocked:
                vehicle = dc(road.queue[0])
                road.queue.pop(0)
                self.traffic_light.block_crossing(vehicle.crossing_duration)

class Car():
    # The client
    def __init__(self, vehicle_type):
        self.vehicle_type = vehicle_type
        self.speed = 1
        self.coming_from = random.choices(dc(cf.directions), weights=cf.coming_from_weights, k=1)[0]

        possibilities = dc(cf.directions)
        possibilities.remove(self.coming_from)
        self.going_to = random.choices(possibilities, weights=cf.going_to_weights, k=1)[0]
        self.path = self.coming_from + self.going_to
        self.crossing_duration = self.define_crossing_duration()

    def define_crossing_duration(self):
        self.crossing_duration = 5
        return self.crossing_duration

class Lights():
    # The server
    def __init__(self, duration_sec):
        self.light_series = cf.traffic_light_series
        self.episode_duration = duration_sec
        self.active_episode = self.light_series[0]
        self.ticks_left = self.episode_duration
        self.ticks_blocked = 0

    def block_crossing(self, how_long):
        logging.info(f'Serving current traffic for {i} for ticks')
        if how_long > self.ticks_blocked:
            self.ticks_blocked = how_long
        self.blocked = True

    def free_crossing(self):
        logging.info('Freeing server')
        self.blocked = False

    def change_episode(self):
        active_episode_index = self.light_series.index(self.active_episode)
        active_episode_index += 1
        if active_episode_index >= len(self.light_series):
            active_episode_index = 0
        self.active_episode = self.light_series[active_episode_index]
        logging.info('Changing traffic light episode to go for')
        logging.info([x for x, y in self.active_episode if y == 'go'])

    def lower_counter(self, ticks_passed):
        logging.info(f'Lowering counter')
        self.ticks_left -= ticks_passed
        self.ticks_blocked -= ticks_passed

    def renew_counter(self):
        logging.info('Renewing counter')
        self.ticks_left = self.episode_duration

    def update(self, ticks_passed):
        logging.info('Updating traffic lights')
        self.lower_counter(ticks_passed)
        if self.ticks_left == 0:
            self.change_episode()
            self.renew_counter()
        if self.ticks_blocked == 0:
            self.free_crossing()

class Road():
    # The queue
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

if __name__ == '__main__':
    sim = Simulation()
    for i in range(0, 100):
        sim.update()