import random
import math
import threading
import networkx as nx
from CityConfiguration import City
from collections import defaultdict
from EmergencyUnit import EmergencyUnit


class Emergency:
    lock = threading.Lock()
    # Class variable - Dictionary mapping different intensities to number of emergency teams and total time taken to
    # resolve once team reaches location of emergency
    intensity_mapping = {1: {'teams': 3, 'time': 5}, 2: {'teams': 4, 'time': 10}, 3: {'teams': 5, 'time': 15},
                         4: {'teams': 6, 'time': 20}, 5: {'teams': 7, 'time': 25}}
    # Class variable - Threshold of time for emergency resolution for it to be considered successfully resolved.
    resolution_time_threshold = 10
    # Class variable - List containing time taken for resolution of each emergency
    emergencies = []

    def __init__(self, city: City, zone: int):
        """
        Initialize location and intensity of emergency using probability distributions.
        >>> populations = [2000, 3500, 900, 4500, 700, 9000, 870, 4500, 2000, 400, 2400, 3000]
        >>> intensity_distributions = [0.2, 0.2, 0.2, 0.2, 0.2]
        >>> test1 = City(4, 3, populations, intensity_distributions)
        >>> e1 = EmergencyUnit('large', (1, 7))
        >>> e2 = EmergencyUnit('large', (3, 2))
        >>> e3 = EmergencyUnit('large', (5, 0))
        >>> e4 = EmergencyUnit('large', (7, 10))
        >>> e1=Emergency(test1, 8)
        >>> 6 <= e1.location[0] <= 8
        True
        >>> 0 <= e1.location[1] <= 2
        True
        >>> e2=Emergency(test1, 2)
        >>> 0 <= e2.location[0] <= 2
        True
        >>> 6 <= e2.location[1] <= 8
        True
        >>> 1 <= e2.intensity <= 5
        True
        >>> e3=Emergency(test1, 7)
        >>> 3 <= e3.location[0] <= 5
        True
        >>> 9 <= e3.location[1] <= 11
        True
        >>> e4=Emergency(test1, 15)
        Unable to create an emergency as zone does not exist in the city.
        """
        if zone >= city.width*city.height:
            print('Unable to create an emergency as zone does not exist in the city.')
            return
        self.time_to_respond = None
        zone_col = zone % city.width
        zone_row = math.floor(zone/city.width)
        self.response_unit = None
        loc = random.randint(0, (City.zone_dimension ** 2) - 1)
        r = math.floor(loc/City.zone_dimension)
        c = loc % City.zone_dimension
        self.location = ((zone_row*City.zone_dimension) + r, (zone_col*City.zone_dimension) + c)
        rand = random.randint(1, 100)
        for i in range(len(city.intensity_cumulative)):
            if rand <= city.intensity_cumulative[i]:
                self.intensity = i + 1
                break
        self.city_of_emergency = city
        self.requirement = Emergency.intensity_mapping[self.intensity]['teams']
        Emergency.emergencies.append(self)
        self.resolve_emergency()


    def resolve_emergency(self):
        """
        :return:
        >>> populations = [2500, 2500]
        >>> intensity_distributions = [1, 0, 0, 0, 0]
        >>> test = City(2, 1, populations, intensity_distributions)
        >>> EmergencyUnit.clear_emergency_buildings()
        >>> Emergency.clear_emergencies()
        >>> e1 = EmergencyUnit('small', (1, 1))
        >>> e2 = EmergencyUnit('small', (1, 2))
        >>> e3 = EmergencyUnit('small', (1, 3))
        >>> e4 = EmergencyUnit('small', (1, 4))
        >>> e5 = EmergencyUnit('small', (1, 5))
        >>> e6 = EmergencyUnit('small', (0, 1))
        >>> e7 = EmergencyUnit('small', (0, 2))
        >>> e8 = EmergencyUnit('small', (0, 3))
        >>> e9 = EmergencyUnit('small', (0, 4))
        >>> e10 = EmergencyUnit('small', (0, 5))
        >>> e11 = EmergencyUnit('small', (2, 0))
        >>> e12 = EmergencyUnit('small', (2, 1))
        >>> e13 = EmergencyUnit('small', (2, 2))
        >>> e14 = EmergencyUnit('small', (2, 3))
        >>> e15 = EmergencyUnit('small', (2, 4))
        >>> e16 = EmergencyUnit('small', (2, 5))
        >>> e17 = EmergencyUnit('small', (1, 0))
        >>> e18 = EmergencyUnit('small', (0, 0))
        >>> e = Emergency(test, 0)
        >>> e.resolve_emergency()
        >>> e.time_to_respond == 1.0
        True
        """
        emergency_units, time_taken_to_reach, waiting_time = self.allocate_teams_to_emergency()
        time_to_resolve = time_taken_to_reach + Emergency.intensity_mapping[self.intensity]['time'] + time_taken_to_reach + waiting_time
        self.time_to_respond = float(time_taken_to_reach) + waiting_time
        self.response_unit = emergency_units
        for _ in range(int(time_to_resolve)):
            for __ in self.city_of_emergency.zone_populations:
                random.randint(1, 1000000)
        for emergency_unit, num_teams in emergency_units.items():
            emergency_unit.relieve_response_teams(num_teams)


    def allocate_teams_to_emergency(self):
        """
        Optimally allocate the required number of teams to resolve the emergency by finding the nearest available teams
        - calculating the time required to respond to the emergency and updating number of available teams in the
        emergency units from which teams are being dispatched.
        :return:
        >>> populations = [2500, 2500]
        >>> intensity_distributions = [0, 1, 0, 0, 0]
        >>> test = City(2, 1, populations, intensity_distributions)
        >>> EmergencyUnit.clear_emergency_buildings()
        >>> Emergency.clear_emergencies()
        >>> e1 = EmergencyUnit('small', (1, 1))
        >>> e2 = EmergencyUnit('small', (1, 2))
        >>> e3 = EmergencyUnit('small', (1, 3))
        >>> e4 = EmergencyUnit('small', (1, 4))
        >>> e5 = EmergencyUnit('small', (1, 5))
        >>> e6 = EmergencyUnit('small', (0, 1))
        >>> e7 = EmergencyUnit('small', (0, 2))
        >>> e8 = EmergencyUnit('small', (0, 3))
        >>> e9 = EmergencyUnit('small', (0, 4))
        >>> e10 = EmergencyUnit('small', (0, 5))
        >>> e11 = EmergencyUnit('small', (2, 0))
        >>> e12 = EmergencyUnit('small', (2, 1))
        >>> e13 = EmergencyUnit('small', (2, 2))
        >>> e14 = EmergencyUnit('small', (2, 3))
        >>> e15 = EmergencyUnit('small', (2, 4))
        >>> e16 = EmergencyUnit('small', (2, 5))
        >>> e17 = EmergencyUnit('small', (1, 0))
        >>> e18 = EmergencyUnit('small', (0, 0))
        >>> e = Emergency(test, 0)
        >>> unit_loc, avg_time, wait_time = e.allocate_teams_to_emergency()
        >>> avg_time > 1
        True
        >>> list(unit_loc.values())[0] > 1
        True
        >>> 0 <= list(unit_loc.keys())[0].location[0] <= 2
        True
        >>> 0 <= list(unit_loc.keys())[0].location[1] <= 5
        True
        """
        # Locking mechanism used for the thread to acquire a lock at the beginning of the method and release it at the
        # end to prevent race conditions
        # Locking code obtained from https://coderslegacy.com/python/lock-in-with-statement/
        waiting_time = 0
        with Emergency.lock:
            graph = self.city_of_emergency.city_graph
            emergency_requirement = self.requirement
            response_time = 0  # seconds
            winner_nodes = defaultdict(dict)
            while emergency_requirement != 0:
                node_to_emergency_details = defaultdict(dict)
                for unit in EmergencyUnit.response_buildings:
                    if unit.available_capacity > 0:
                        node_to_emergency_details[unit]['capacity'] = unit.available_capacity
                        node_to_emergency_details[unit]['time'] = 1 if unit.location == self.location \
                            else nx.algorithms.shortest_path_length(
                            graph, unit.location, self.location, weight='adjusted_time', method='dijkstra')
                sorted_node_to_emergency_details = {k: v for k, v in sorted(node_to_emergency_details.items(),
                                                                            key=lambda item: (
                                                                            item[1]['time'], -item[1]['capacity']))}
                for response_unit in sorted_node_to_emergency_details:
                    emergency_requirement, available, teams_dispatched = response_unit.check_team_availability(
                        emergency_requirement)
                    if available:
                        response_time += sorted_node_to_emergency_details[response_unit]['time']
                        response_unit.dispatch_teams(teams_dispatched)
                        winner_nodes[response_unit] = teams_dispatched
                    if emergency_requirement == 0:
                        break
                if emergency_requirement != 0:
                    EmergencyUnit.wait_for_teams_to_be_available = True
                    while EmergencyUnit.wait_for_teams_to_be_available:
                        for __ in self.city_of_emergency.zone_populations:
                            random.randint(1, 1000000)
                        waiting_time += 1
                else:
                    avg_resp = response_time / len(winner_nodes)
            # winner_criteria = 1 if avg_resp >= 15 else 0
            return winner_nodes, avg_resp, waiting_time

    @staticmethod
    def clear_emergencies():
        """
        :return:
        >>> populations = [2000, 3500, 900, 4500, 700, 9000, 870, 4500, 2000, 400, 2400, 3000]
        >>> intensity_distributions = [0.2, 0.2, 0.2, 0.2, 0.2]
        >>> test2 = City(4, 3, populations, intensity_distributions)
        >>> Emergency.clear_emergencies()
        >>> e1=Emergency(test2, 2)
        >>> len(Emergency.emergencies)
        1
        >>> Emergency.clear_emergencies()
        >>> len(Emergency.emergencies)
        0
        """
        Emergency.emergencies = []