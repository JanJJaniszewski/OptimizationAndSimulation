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
        self.traffic_light = Lights()
        self.vehicle_generator = VehicleGenerator()
        self.counters = {
            'lights': next(self.traffic_light.durations),
            'arrivals': next(self.vehicle_generator.arrival_time_cycle),
            'service0': 2.4,
            'service1': 2.5,
            'service2': 2.6,
            'service3': 2.7,
            'service4': 2.8,
            'service5': 2.9
        }
        self.roads = self.create_roads(cf.paths)
        self.results = pd.DataFrame()
        self.ticks_green = 0
        self.services = ['service0', 'service1', 'service2', 'service3', 'service4', 'service5']
        self.ticks = 0
        self.waiting_times = pd.DataFrame()

    def create_roads(self, road_list):
        roads = dict()
        for path in road_list:
            new_road = Road(path)
            roads[path] = new_road

        return roads

    def tiktok(self):
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
            self.counters['service3'] -= self.ticks
            self.counters['service4'] -= self.ticks
            self.counters['service5'] -= self.ticks

    def update(self):
        logger.debug('UPDATE -----------------------------------------')
        #logger.info(self.counters)
        #logger.info([(a, len(r.queue)) for a, r in self.roads.items()])

        if not self.traffic_light.served_roads:
            lowest_counter = list(self.counters.keys())[list(self.counters.values()).index(min(self.counters['lights'], self.counters['arrivals']))]
        else:
            lowest_counter = min(self.counters, key=self.counters.get)
        self.ticks = self.counters[lowest_counter]

        self.tiktok()
        if lowest_counter == 'lights':
            self.counters['lights'] = self.traffic_light.update()
        elif lowest_counter == 'arrivals':
            vehicle, self.counters['arrivals'] = self.vehicle_generator.vehicles_arrive(clock=self.clock)
            self.roads[vehicle.path].queue.append(vehicle)
        elif (lowest_counter in self.services):
            road_num = int(lowest_counter[-1])
            try:
                path = self.traffic_light.served_roads[road_num]
            except IndexError as e:
                logger.warning(f'{e}: That means that we assumed there are more green lights than there are. Nothing to worry about though.')
            else:
                queuelength = len(self.roads[path].queue)
                if queuelength == 0:
                    self.counters[lowest_counter] = 0.1 + self.counters['arrivals']
                else:
                    self.counters[lowest_counter], vehicle_waiting_time = self.roads[path].vehicles_leave(self.ticks_green, clock = self.clock)
                    self.save_waiting_times(vehicle_waiting_time, path, queuelength)

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

    def save_waiting_times(self, vehicle_waiting_time, path, queuelength):
        self.waiting_times = pd.concat([self.waiting_times, pd.DataFrame({'clock': [self.clock],
                                                              'road': [path],
                                                                    'waiting_time': vehicle_waiting_time,
                                                         'queue': [queuelength]})], ignore_index=True)

class Car():
    # The client
    def __str__(self):
        return (self.vehicle_type)

    def __repr__(self):
        return (self.vehicle_type)

    def __init__(self, vehicle_type, service_time, startclock):
        self.vehicle_type = vehicle_type
        self.service_time = service_time
        self.path = next(cf.path_choice_cycle)
        self.startclock = startclock



class Lights():
    # The server
    def __init__(self):
        logger.debug('Initiating traffic lights (server)')
        self.active_episodes = cf.traffic_light_series
        self.active_episode = next(self.active_episodes)
        self.traffic_light_all_stop = cf.traffic_light_all_stop
        self.durations = cf.traffic_light_episode_durations
        self.served_roads = []
        self.episode_type = cf.episode_type

    def block_crossing(self):
        logger.debug(f'Blocking intersection for all incoming traffic')
        counter = cf.traffic_light_crossing_block_in_ticks
        self.active_episode = self.traffic_light_all_stop

        return counter

    def change_episode(self):
        logger.debug('Freeing server for new requests (deblocking intersection) and renewing counter')
        self.active_episode = next(self.active_episodes)
        counter = next(self.durations)

        return counter

    def update(self):
        episode_type = next(self.episode_type)
        if episode_type == 'block':
            #queue_exploding = min([len(road.queue) for road in roads if road.path in self.served_roads]) > 0
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
        self.arrival_time_cycle = cf.arrival_time_cycle

    def vehicles_arrive(self, clock):
        vehicle_type = next(cf.vehicle_type_cycle)
        vehicle_service_time = next(cf.service_time_cycles[vehicle_type])
        vehicle = Car(vehicle_type=vehicle_type, service_time=vehicle_service_time, startclock=clock)
        counter = next(self.arrival_time_cycle)
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

    def vehicles_leave(self, ticks_green, clock):
        if len(self.queue) > 0:
            vehicle = dc(self.queue[0])
            vehicle_waiting_time = clock - vehicle.startclock

            self.queue.pop(0)
            #logger.info(f'-------------------------VEHICLE LEFT: {self.path}')

            # slowdown_cycles: all cars slow down when in front of traffic light
            # service_time: Time of acceleration
            # ticks green: How long is traffic light on 'GO'/'GREEN' already
            # service_time = 1s + (1s / (1+'GO'(s))
            counter = next(cf.slowdown_cycles) + (vehicle.service_time / (ticks_green+1))
        else:
            counter = 0
            vehicle_waiting_time = -999

        return counter, vehicle_waiting_time




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
        ft.write_feather(sim.waiting_times, f'data/waitingtimes_testrun.feather')
    else:
        ft.write_feather(sim.results, f"data/results_{datetime.datetime}.feather")
        ft.write_feather(sim.results, f"data/waitingtimes_{datetime.datetime}.feather")
