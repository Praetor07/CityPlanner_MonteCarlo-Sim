import networkx as nx
from Emergency import Emergency

class EmergencyUnit:
    # Class variable - List of all emergency units (all objects of class)
    response_buildings = []
    def __init__(self, size: int, location: str, name: str = None):
        """
        Initialize size and location of the emergency unit, along with number of teams currently available
        :param size:
        :param location:
        """
        self.name = name
        self.capacity = size
        self.available_capacity = size
        self.location = location
        EmergencyUnit.response_buildings.append(self)

    def relieve_response_unit(self):
        self.available_capacity = self.capacity


    def check_team_availability(self, team_requirement: int):
        """

        :param team_requirement: attribute of the Emergency class determining the personnel needed to address the emergency
        :return:
        """
        if self.available_capacity <= team_requirement:
            return 0
        else:
            return team_requirement - self.available_capacity

    def allocate_teams_to_emergency(self, graph: nx.DiGraph, emergency: Emergency):
        """
        Update current location to unit to location of emergency and store time after which unit becomes available.
        :return:
        """
        min_time = float('inf')
        winner_node = ''
        winnner_criteria = 15
        for unit in EmergencyUnit.response_buildings:
            if unit.name == emergency.coordinate:
                return 1 #default value if emergency at same coordinate as emergency
            else:
                time = nx.algorithms.shortest_path_length(graph, unit.name, emergency.coordinate, weight='adjusted_time', method='dijkstra')
                if time < min_time:
                    team_availability = unit.check_team_availability(emergency.scale)
                    if unit.check_team_availability(emergency.scale):
                    winner_node = unit.name


