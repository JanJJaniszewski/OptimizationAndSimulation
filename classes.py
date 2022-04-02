import datetime
from copy import deepcopy as dc
from itertools import cycle
import numpy as np
import pyarrow.feather as ft
import pandas as pd
import multiprocessing

import config as cf
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
        #logger.info('Initiating everything')
        self.clock = 0
        self.counters = {
            'lights': next(cf.traffic_light_episode_durations),
            'arrivals': next(cf.arrival_time_cycle),
            'service0': 2.4,
            'service1': 2.5,
            'service2': 2.6,
        }
        self.traffic_light = Lights()
        self.roads = self.create_roads(cf.paths)
        self.results = pd.DataFrame()
        self.ticks_green = 0
        self.services = ['service0', 'service1', 'service2']
        self.vehicle_generator = VehicleGenerator()
        self.ticks = 0

    def create_roads(self, road_list):
        roads = dict()
        for path in road_list:
            new_road = Road(path)
            roads[path] = new_road

        return roads

    def tiktok(self, event_type):
        self.clock += self.ticks
        self.ticks_green += self.ticks
        self.counters['lights'] -= self.ticks
        self.counters['arrivals'] -= self.ticks

        if self.traffic_light.served_roads == []:
            self.ticks_green = 0
        else:
            self.counters['service0'] -= self.ticks
            self.counters['service1'] -= self.ticks
            self.counters['service2'] -= self.ticks

    def update(self):
        logger.debug('UPDATE -----------------------------------------')
        #logger.info(self.counters)
        #logger.info([(a, len(r.queue)) for a, r in self.roads.items()])

        if not self.traffic_light.served_roads:
            lowest_counter = list(self.counters.keys())[list(self.counters.values()).index(min(self.counters['lights'], self.counters['arrivals']))]
        else:
            lowest_counter = min(self.counters, key=self.counters.get)
        self.ticks = self.counters[lowest_counter]

        if lowest_counter == 'lights':
            self.tiktok('lights')
            self.counters['lights'] = self.traffic_light.update()
        elif lowest_counter == 'arrivals':
            self.tiktok('arrivals')
            vehicle, self.counters['arrivals'] = self.vehicle_generator.vehicles_arrive()
            self.roads[vehicle.path].queue.append(vehicle)
        elif (lowest_counter in self.services):
            self.tiktok('services')
            road_num = int(lowest_counter[-1])
            path = self.traffic_light.served_roads[road_num]
            if len(self.roads[path].queue) == 0:
                self.counters[lowest_counter] = 0.1 + self.counters['arrivals']
            else:
                self.counters[lowest_counter] = self.roads[path].vehicles_leave(self.ticks_green)

        self.save_results()

    def save_results(self):
        assert self.traffic_light.active_episode.keys() == self.roads.keys()

        num_served_roads = len(self.roads)
        clocks = [self.clock] * num_served_roads
        indicators = self.traffic_light.active_episode.values()
        paths = self.traffic_light.active_episode.keys()
        queues = [len(r.queue) for r in self.roads.values()]

        self.results = pd.concat([self.results, pd.DataFrame({'clock': clocks,
                                                              'road': paths,
                                                         'indicator': indicators,
                                                         'queue': queues})], ignore_index=True)

class Car():
    # The client
    def __str__(self):
        return (self.vehicle_type)

    def __repr__(self):
        return (self.vehicle_type)

    def __init__(self, vehicle_type, service_time):
        self.vehicle_type = vehicle_type
        self.service_time = service_time
        self.path = next(cf.path_choice_cycle)



class Lights():
    # The server
    def __init__(self):
        logger.debug('Initiating traffic lights (server)')
        self.active_episode = next(cf.traffic_light_series)
        self.served_roads = []

    def block_crossing(self):
        logger.debug(f'Blocking intersection for all incoming traffic')
        counter = cf.traffic_light_crossing_block_in_ticks
        self.active_episode = cf.traffic_light_all_stop

        return counter

    def change_episode(self):
        logger.debug('Freeing server for new requests (deblocking intersection) and renewing counter')
        self.active_episode = next(cf.traffic_light_series)
        counter = next(cf.traffic_light_episode_durations)

        return counter

    def update(self):
        episode_type = next(cf.episode_type)
        if episode_type == 'block':
            counter = self.block_crossing()
            self.served_roads = []
        elif episode_type == 'go':
            counter = self.change_episode()
            self.served_roads = [path for path, active in self.active_episode.items() if active == 'go']
        else:
            Exception('What the heck happened?')
        #logger.info(f'-------------------------LIGHT CHANGED: {[x for x, y in self.active_episode.items() if y == "go"]}')

        return counter


class VehicleGenerator():
    # The client generation function
    def __init__(self):
        pass

    def vehicles_arrive(self):
        vehicle_type = next(cf.vehicle_type_cycle)
        vehicle_service_time = next(cf.service_time_cycles[vehicle_type])
        vehicle = Car(vehicle_type=vehicle_type, service_time=vehicle_service_time)
        counter = next(cf.arrival_time_cycle)
        #logger.debug(f'-------------------------VEHICLE ARRIVED: {vehicle.path}')
        return vehicle, counter


class Road():
    # The queue
    def __init__(self, path):
        logger.debug('Initiating queue (road)')
        self.path = path
        self.queue = []

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.path

    def vehicles_leave(self, ticks_green):
        if len(self.queue) > 0:
            vehicle = dc(self.queue[0])
            self.queue.pop(0)
            #logger.info(f'-------------------------VEHICLE LEFT: {self.path}')

            # slowdown_cycles: all cars slow down when in front of traffic light
            # service_time: Time of acceleration
            # ticks green: How long is traffic light on 'GO'/'GREEN' already
            # service_time = 1s + (1s / (1+'GO'(s))
            counter = next(cf.slowdown_cycles) + (vehicle.service_time / (ticks_green+1))
        else:
            counter = 0

        return counter




def run_updates(sim):
    for i in range(1, cf.ticks + 1):
        sim.update()
    #ft.write_feather(sim.results, f"results_{version}.feather")
    return sim

if __name__ == '__main__':
    sim = Simulation()
    for i in range(1, cf.ticks + 1):
        sim.update()
    is_testrun = True
    if is_testrun:
        ft.write_feather(sim.results, f"data/results_testrun.feather")
    else:
        ft.write_feather(sim.results, f"data/results_{datetime.datetime}.feather")

