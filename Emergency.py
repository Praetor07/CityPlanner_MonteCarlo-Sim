import random
import math
import threading
import networkx as nx
from CityConfiguration import City
from collections import defaultdict
from EmergencyUnit import EmergencyUnit


class Emergency:
    """
    Emergency entity which represents the emergencies occurring throughout the city.
    """
    lock = threading.Lock()
    # Dictionary mapping different intensities to number of emergency teams and total time taken to
    # resolve each intensity type of emergency, once team reaches the location of the emergency.
    intensity_mapping = {1: {'teams': 3, 'time': 5}, 2: {'teams': 4, 'time': 10}, 3: {'teams': 5, 'time': 15},
                         4: {'teams': 6, 'time': 20}, 5: {'teams': 7, 'time': 25}}
    # Threshold of time, in minutes, for emergency resolution in order for it to be considered as successfully resolved.
    resolution_time_threshold = 10
    # List containing all the Emergency objects over one simulation run
    emergencies = []

    def __init__(self, city: City, zone: int):
        """
        Randomize the location of emergency within the specified zone, using a uniform distribution, and
        randomize the intensity of the emergency using the user provided probabilites. The number
        of teams required to resolve the emergency is also initialized using the pre-defined dictionary mapping,
        and the emergency is attempted to be resolved.
        :param city: City configured where the emergency is taking place
        :param zone: Zone number of the city, counted from 0 row-wise, where the emergency occurs
        :return: None
        >>> populations = [2000, 3500, 900, 4500, 700, 9000, 870, 4500, 2000, 400, 2400, 3000]
        >>> intensity_distributions = [0.2, 0.2, 0.2, 0.2, 0.2]
        >>> test1 = City(4, 3, populations, intensity_distributions)
        >>> eu1 = EmergencyUnit('large', (1, 7))
        >>> eu2 = EmergencyUnit('large', (3, 2))
        >>> eu3 = EmergencyUnit('large', (5, 0))
        >>> eu4 = EmergencyUnit('large', (7, 10))
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
        # One of 9 coordinates (0 to 8) chosen to position emergency
        loc = random.randint(0, (City.zone_dimension ** 2) - 1)
        r = math.floor(loc/City.zone_dimension)
        c = loc % City.zone_dimension
        # Location of the emergency calculated with respect to the city coordinate grid
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
        Invokes the core logic of the simulation to allocate the required number of available teams from optimal
        locations of the emergency units, in order to resolve the emergency. Once the optimal allocation of teams
        from one or more emergency units is calculated, the simulation performs the computation representing
        the passage of time, which represents the teams being busy and unavailable to respond to other emergencies.
        Once the specified amount of time required for the teams to commute to the location of the emergency, resolve
        the emergency and commute back to their original location(s) has elapsed, the teams are released and are
        free to respond to subsequent emergencies.
        :return: None
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
        # Total time taken to resolve emergency
        time_to_resolve = time_taken_to_reach + Emergency.intensity_mapping[self.intensity]['time'] + \
            time_taken_to_reach + waiting_time
        # Time taken to respond to the emergency (commute time to location of emergency)
        self.time_to_respond = float(time_taken_to_reach) + waiting_time
        self.response_unit = emergency_units
        # Waiting for passage of time equivalent to the total time that teams are busy (to-commute time, time to resolve
        # emergency, fro-commute time and any waiting time), by simulating each minute as program equivalent of passage
        # of a minute as what occurs in the simulate() function, where each iteration and the computation within each
        # iteration until a random number is chosen is considered to be 1 minute in program/simulation time
        for _ in range(int(time_to_resolve)):
            for __ in self.city_of_emergency.zone_populations:
                random.randint(1, 1000000)
        # Relieve emergency teams after keeping them busy for the required duration of time as described above
        for emergency_unit, num_teams in emergency_units.items():
            emergency_unit.relieve_response_teams(num_teams)

    def allocate_teams_to_emergency(self):
        """
        Optimally allocate the required number of teams to resolve the emergency by finding the available teams
        from one or more emergency units. Calculate the time required to respond to the emergency as the average of
        the time required for each of the teams to commute to the location of the emergency using the Dijkstra's
        shortest path algorithm. Update the number of available teams in the emergency units from which teams are being
        dispatched.
        In the scenario that no emergency units have teams available, then the emergency waits for the
        required number of teams to become available, and the waiting time is also recorded.
        Since each emergency is created on a separate thread, a locking mechanism is added to the logic in this method
        in order to prevent race conditions, and ensure that the optimal allocation of teams calculation is performed
        for only one thread (emergency) at one point in time.
        :return: Dictionary containing mapping of emergency unit objects to the time required for teams from each
        of the allocated emergency units to reach the location of the emergency (respond to the emergency), the
        response time in minutes for the particular emergency, waiting time (if any) in minutes that was involved
        in waiting for required number of teams to become available.
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
            # Response time measured in minutes
            response_time = 0
            winner_nodes = defaultdict(dict)
            while emergency_requirement != 0:
                node_to_emergency_details = defaultdict(dict)
                # For units where teams are available, sort the units by time required for a team from unit
                # to reach location of emergency (ascending order), and use number of
                # available teams (descending order) to resolve ties while sorting. If an emergency occurs
                # at the same location as an emergency unit, minimal default time of 1 minute is considered
                # as the time taken to respond to the emergency.
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
                # If there aren't sufficient teams available to resolve the emergency, wait until a team becomes
                # available (appropriate flag is set by thread in EmergencyUnit class when relieving teams).
                # Record the waiting time in minutes, by simulating each minute as program equivalent of passage
                # of a minute as what occurs in the simulate() function, where each iteration and the computation
                # within each iteration until a random number is chosen is considered to be 1 minute in
                # program/simulation time
                if emergency_requirement != 0:
                    EmergencyUnit.wait_for_teams_to_be_available = True
                    while EmergencyUnit.wait_for_teams_to_be_available:
                        for __ in self.city_of_emergency.zone_populations:
                            random.randint(1, 1000000)
                        waiting_time += 1
                else:
                    avg_resp = response_time / len(winner_nodes)
            return winner_nodes, avg_resp, waiting_time

    @staticmethod
    def clear_emergencies():
        """
        Clears the list of emergencies stored for each simulation run, at the end of each simulation run.
        :return: None
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
