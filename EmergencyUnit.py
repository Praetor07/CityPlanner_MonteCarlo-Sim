import networkx as nx
from Emergency import Emergency
from collections import defaultdict, OrderedDict
from CityConfiguration import City

class EmergencyUnit:
    # Class variable - List of all emergency units (all objects of class)
    response_buildings = []
    def __init__(self, size: int, location: str = None):
        """
        Initialize size and location of the emergency unit, along with number of teams currently available
        :param size:
        :param location:
        """
        self.location = location
        self.available_capacity = size
        EmergencyUnit.response_buildings.append(self)

    def relieve_response_teams(self, relieved_units):
        self.available_capacity += relieved_units

    def dispatch_teams(self, required_units):
        self.available_capacity -= required_units

    def check_team_availability(self, team_requirement: int):
        """

        :param team_requirement: attribute of the Emergency class determining the personnel needed to address the emergency
        :return:
        """
        if self.available_capacity <= 0:
            return team_requirement, False, 0
        if self.available_capacity <= team_requirement:
            return team_requirement - self.available_capacity, True, self.available_capacity
        else:
            return 0, True, team_requirement

    @staticmethod
    def allocate_teams_to_emergency(graph: nx.DiGraph, emergency: Emergency):
        """
        Update current location to unit to location of emergency and store time after which unit becomes available.
        :return:
        """
        emergency_requirement = emergency.requirement
        node_to_emergency_details = defaultdict(dict)
        response_time = 0 #seconds
        number_of_units = 0
        winner_nodes = defaultdict(dict)
        for unit in EmergencyUnit.response_buildings:
            if unit.available_capacity > 0:
                node_to_emergency_details[unit]['capacity'] = unit.available_capacity
                node_to_emergency_details[unit]['time'] = 1 if unit.location == emergency.location \
                    else nx.algorithms.shortest_path_length(
                    graph, unit.location, emergency.location, weight='adjusted_time', method='dijkstra')
        sorted_node_to_emergency_details = {k: v for k, v in sorted(node_to_emergency_details.items(), key=lambda item: (item[1]['time'],-item[1]['capacity']))}
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
        avg_resp = response_time/number_of_units
        # winner_criteria = 1 if avg_resp >= 15 else 0
        return winner_nodes, avg_resp




