import random
import math
import networkx as nx
from CityConfiguration import City
from collections import defaultdict
from EmergencyUnit import EmergencyUnit

class Emergency:
    # Class variable - Dictionary mapping different intensities to number of emergency teams and total time taken to
    # resolve once team reaches location of emergency
    intensity_mapping = {1: {'teams': 1, 'time': 5}, 2: {'teams': 4, 'time': 10}, 3: {'teams': 5, 'time': 15},
                         4: {'teams': 6, 'time': 20}, 5: {'teams': 7, 'time': 25}}
    # Class variable - Threshold of time for emergency resolution for it to be considered successfully resolved.
    resolution_time_threshold = 25
    # Class variable - List containing time taken for resolution of each emergency
    emergencies = []
    def __init__(self, city: City, zone: int):
        """
        Initialize location and intensity of emergency using probability distributions.
        If location of emergency is same as that of emergency response unit, we assume a small time as
        coordinates represent approximate locations
        """
        self.time_to_respond = None
        zone_row = zone % city.height
        zone_col = math.floor(zone/city.height)
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


    def resolve_emergency(self):
        """

        :return:
        >>> populations = [2500, 2500]
        >>> intensity_distributions = [1, 0, 0, 0, 0]
        >>> test = City(2, 1, populations, intensity_distributions)
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
        >>> e.time_to_respond
        1.0
        """
        emergency_units, time_taken_to_reach = self.allocate_teams_to_emergency()
        time_to_resolve = time_taken_to_reach + Emergency.intensity_mapping[self.intensity]['time'] + time_taken_to_reach
        self.time_to_respond = float(time_taken_to_reach)
        for _ in range(int(time_to_resolve)*60):
            pass
        for emergency_unit, num_teams in emergency_units.items():
            emergency_unit.relieve_response_teams(num_teams)


    def allocate_teams_to_emergency(self):
        """
        Update current location to unit to location of emergency and store time after which unit becomes available.
        :return:
        """
        if True:
            graph = self.city_of_emergency.city_graph
            emergency_requirement = self.requirement
            node_to_emergency_details = defaultdict(dict)
            response_time = 0  # seconds
            number_of_units = 0
            winner_nodes = defaultdict(dict)
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
                    number_of_units += 1
                    response_unit.dispatch_teams(teams_dispatched)
                    winner_nodes[response_unit] = teams_dispatched
                if emergency_requirement == 0:
                    break
            avg_resp = response_time / number_of_units
            # winner_criteria = 1 if avg_resp >= 15 else 0
            return winner_nodes, avg_resp

    @staticmethod
    def clear_emergencies():
        Emergency.emergencies = []
