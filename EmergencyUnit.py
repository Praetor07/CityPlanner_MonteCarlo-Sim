import networkx as nx
# from Emergency import Emergency
from collections import defaultdict, OrderedDict
from CityConfiguration import City

class EmergencyUnit:
    # Class variable - List of all emergency units (all objects of class)
    response_buildings = []
    type_to_capacity_mapping = {'small': 1, 'medium': 2, 'large': 3}
    def __init__(self, size: str, location: tuple):
        """
        Initialize size and location of the emergency unit, along with number of teams currently available
        :param size:
        :param location:
        """
        self.location = location
        self.available_capacity = EmergencyUnit.type_to_capacity_mapping[size]
        if self.check_emergency_building_coordinates():
            EmergencyUnit.response_buildings.append(self)
        else:
            raise ValueError("Coordinates are duplicate for EmergencyResponse unit buildings..")

    def relieve_response_teams(self, relieved_units):
        """
        Function to relive response teams once a emergency is resolved

        :param relieved_units: number of units to be relived
        :return: None

        >>> e= EmergencyUnit('medium', (1,3))
        >>> e.relieve_response_teams(1)
        >>> e.available_capacity
        3
        """
        self.available_capacity += relieved_units

    def dispatch_teams(self, required_units):
        """
        Function to reduce units capacity after dispatching teams for emergency

        :param required_units: number of units required by emergency
        :return: None

        >>> e= EmergencyUnit('medium', (1,2))
        >>> e.dispatch_teams(1)
        >>> e.available_capacity
        1
        """
        self.available_capacity -= required_units

    def check_team_availability(self, team_requirement: int):
        """

        :param team_requirement: attribute of the Emergency class determining the personnel needed to address the emergency
        :return: further requirement, <if building can source all teams>, dispatched teams from unit

        >>> e= EmergencyUnit('medium', (1,1))
        >>> e.check_team_availability(2)
        (0, True, 2)
        >>> e.check_team_availability(3)
        (1, True, 2)
        """
        if self.available_capacity <= 0:
            return team_requirement, False, 0
        if self.available_capacity <= team_requirement:
            return team_requirement - self.available_capacity, True, self.available_capacity
        else:
            return 0, True, team_requirement

    def check_emergency_building_coordinates(self):
        """
        Function to ensure no duplicate unit building coordinates are passed
        :return: flag, True if no other unit in same coordinate

        >>> e= EmergencyUnit('medium', (2,2))
        >>> e1= EmergencyUnit('medium', (2,2)) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: Coordinates are duplicate for EmergencyResponse unit buildings..
        """
        flag = True
        for unit in EmergencyUnit.response_buildings:
            if unit.location == self.location:
                flag = False
                break
        return flag





