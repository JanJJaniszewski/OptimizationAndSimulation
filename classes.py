from copy import deepcopy as dc
from time import sleep

import config as cf
import random
import logging

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)




class Simulation():
    # Simulation
    def __init__(self):
        logger.info('Initiating everything')
        self.clock = 0
        self.traffic_light = Lights(cf.traffic_light_episode_duration)
        self.roads = self.create_roads(cf.road_paths)

    def create_roads(self, road_list):
        roads = dict()
        for path in road_list:
            new_road = Road(path[0], path[1])
            roads[path] = new_road

        return roads

    def update(self, ticks_passed = 1):
        logger.info('-' * 50)
        logger.info('UPDATE INFO')

        # Update t
        input('Press whatever you feel to progress to the next tick')
        self.clock += ticks_passed

        # Update server state
        self.traffic_light.update(ticks_passed = ticks_passed)

        for path, road in self.roads.items():
            road.allow_for_new_vehicles_to_arrive()

            # Serve clients
            if (self.traffic_light.active_episode[path] == 'go') and not \
                    self.traffic_light.blocked and \
                (len(road.queue) > 0):
                vehicle = road.vehicle_leaves()

                self.traffic_light.block_crossing(vehicle.crossing_duration)

            logger.info(f'Road: {path}, Cars waiting: {len(road.queue)}')

        logger.info(f'Lights blocked: {self.traffic_light.blocked} for {self.traffic_light.ticks_blocked} turns.')
        logger.info('Changing traffic light (server) episode to GO/green for')
        logger.info([x for x, y in self.traffic_light.active_episode.items() if y == 'go'])


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
        logger.debug('Defining how long it takes the vehicle to cross the street')
        if self.vehicle_type == 'car':
            self.crossing_duration = 5
        else:
            self.crossing_duration = 10
        return self.crossing_duration

class Lights():
    # The server
    def __init__(self, duration_sec):
        logger.info('Initiating traffic lights (server)')
        self.light_series = cf.traffic_light_series
        self.episode_duration = duration_sec
        self.active_episode = self.light_series[0]
        self.ticks_left = self.episode_duration
        self.ticks_blocked = 0
        self.blocked = False

    def block_crossing(self, how_long):
        logger.debug(f'Serving current traffic for {i} for ticks (blocking intersection)')
        if how_long > self.ticks_blocked:
            self.ticks_blocked = how_long
        self.blocked = True

        return self.blocked

    def free_crossing(self):
        logger.info('Freeing server for new requests (deblocking intersection)')
        self.blocked = False

        return self.blocked

    def change_episode(self):
        active_episode_index = self.light_series.index(self.active_episode)
        active_episode_index += 1
        if active_episode_index >= len(self.light_series):
            active_episode_index = 0
        self.active_episode = self.light_series[active_episode_index]

    def lower_counter(self, ticks_passed):
        logger.info(f'Lowering counter')
        self.ticks_left -= ticks_passed
        self.ticks_blocked -= ticks_passed

    def renew_counter(self):
        logger.info('Renewing counter')
        self.ticks_left = self.episode_duration

    def update(self, ticks_passed):
        logger.info('Updating traffic lights')
        self.lower_counter(ticks_passed)
        if self.ticks_left == 0:
            self.change_episode()
            self.renew_counter()
        if self.ticks_blocked == 0:
            self.free_crossing()

class VehicleGenerator():
    # The client generation function
    def __init__(self):
        logger.info('Initiating Vehicle Generator')
        self.vehicle_types = ['car', 'van', 'bus']
        self.distribution = [0.7, 0.2, 0.1]

    def check_if_vehicle_arrives(self):
        logger.debug('Checking if vehicle will arrive')
        vehicle_will_arrive = random.choice([1, 0])
        if vehicle_will_arrive:
            logger.debug('Vehicle arriving')
            vehicle = self.generate_vehicle()
        else:
            vehicle = False

        return vehicle

    def generate_vehicle(self):
        logger.debug('Generating vehicle')
        vehicle_type = random.choices(self.vehicle_types, weights=self.distribution, k=1)[0]
        vehicle = Car(vehicle_type=vehicle_type)
        return vehicle

class Road():
    # The queue
    def __init__(self, coming_from, going_to):
        logger.info('Initiating queue (road)')
        self.coming_from = coming_from
        self.going_to = going_to
        self.path = coming_from + going_to
        self.length = 10
        self.queue = []
        self.vehicle_generator = VehicleGenerator()

    def allow_for_new_vehicles_to_arrive(self):
        vehicle = self.vehicle_generator.check_if_vehicle_arrives()
        if vehicle:
            logger.debug(f'Vehicle arrived and joined queue in {self.path} path')
            self.queue.append(vehicle)  # Add car to queue of waiting cars (if any wait)

        return self.queue

    def vehicle_leaves(self):
        logger.debug('Vehicle (client) left the queue')
        vehicle = dc(self.queue[0])
        self.queue.pop(0)

        return (vehicle)

if __name__ == '__main__':
    sim = Simulation()
    for i in range(0, 100):
        sim.update()