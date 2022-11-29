import networkx as nx
# from Emergency import Emergency
from collections import defaultdict, OrderedDict
from CityConfiguration import City

class EmergencyUnit:
    # Class variable - List of all emergency units (all objects of class)
    response_buildings = []
    def __init__(self, size: int, location: tuple):
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




