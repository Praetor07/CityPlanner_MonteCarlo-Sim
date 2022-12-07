import numpy as np
import networkx as nx

# Function for mod_pert_random has been picked from Mr Weible's example
# from https://github.com/iSchool-597PR/2022_Fall_examples/blob/main/unit_07/Probability_Distributions.ipynb
def mod_pert_random(low, likely, high, confidence=4, samples=1):
    """Produce random numbers according to the 'Modified PERT' distribution.
    :param low: The lowest value expected as possible.
    :param likely: The 'most likely' value, statistically, the mode.
    :param high: The highest value expected as possible.
    :param confidence: This is typically called 'lambda' in literature
                        about the Modified PERT distribution. The value
                        4 here matches the standard PERT curve. Higher
                        values indicate higher confidence in the mode.
                        Currently allows values 1-18
    Formulas to convert beta to PERT are adapted from a whitepaper
    "Modified Pert Simulation" by Paulo Buchsbaum.
    """
    # Check for reasonable confidence levels to allow:
    if confidence < 1 or confidence > 18:
        raise ValueError('confidence value must be in range 1-18.')

    mean = (low + confidence * likely + high) / (confidence + 2)

    a = (mean - low) / (high - low) * (confidence + 2)
    b = ((confidence + 1) * high - low - confidence * likely) / (high - low)

    beta = np.random.beta(a, b, samples)
    beta = beta * (high - low) + low
    return beta


class City:
    zone_dimension = 3
    traffic_time_weights = {0: 0, 1: 2, 2: 2, 3: 1}
    default_commute_time = 3
    # Class variable - represents size of each zone in terms of coordinates
    # Class variable - represents constant time between two adjacent nodes with no traffic between them

    def __init__(self, width: int, height: int, zone_populations: list, intensity_distribution: list):
        """
        Initialize a networkx graph where each node is a coordinate in the city, with its properties being zone number,
        population density of zone. Add edges between every pair or coordinates with the time property equal
        to sum of the distance between the two coordinates and a penalty parameter which is randomized as a
        probability distribution of the population densities of the two nodes.
        Also initialize a mapping of zone numbers to their population densities and top-left corner coordinates
        (this will be used to randomize zone of an emergency as a distribution of the population
        density and then determine a random coordinate within the zone)
        """
        self.width = width
        self.height = height
        self.zone_populations = np.asarray(zone_populations)
        self.coordinate_populations = []
        self.intensity_distribution = intensity_distribution
        self.intensity_cumulative = np.cumsum(np.rint(np.asarray(self.intensity_distribution)*100))
        for i in range(len(zone_populations)):
            for _ in range(City.zone_dimension ** 2):  # number of nodes per zone?
                self.coordinate_populations.append(zone_populations[i] / (City.zone_dimension ** 2))

        self.city_graph = nx.Graph()
        self.build_city_graph()
        self.likely_vals = self.zone_populations / np.sum(self.zone_populations)
        self.update_graph_edges(0)
        # 0,0   0,1   0,2   0,3   0,4   0,5     0,6     0,7     0,8     0,9     0,10    0,11
        # 1,0   1,1   1,2   1,3   1,4   1,5     1,6     1,7     1,8     1,9     1,10    1,11
        # 2,0   2,1   2,2   2,3   2,4   2,5     2,6     2,7     2,8     2,9     2,10    2,11
        # 3,0   3,1   3,2   3,3   3,4   3,5     3,6     3,7     3,8     3,9     3,10    3,11
        # 4,0   4,1   4,2   4,3   4,4   4,5     4,6     4,7     4,8     4,9     4,10    4,11
        # 5,0   5,1   5,2   5,3   5,4   5,5     5,6     5,7     5,8     5,9     5,10    5,11
        # 6,0   6,1   6,2   6,3   6,4   6,5     6,6     6,7     6,8     6,9     6,10    6,11
        # 7,0   7,1   7,2   7,3   7,4   7,5     7,6     7,7     7,8     7,9     7,10    7,11
        # 8,0   8,1   8,2   8,3   8,4   8,5     8,6     8,7     8,8     8,9     8,10    8,11
        # 9,0   9,1   9,2   9,3   9,4   9,5     9,6     9,7     9,8     9,9     9,10    9,11
        # 10,0   10,1   8,2   8,3   8,4   8,5     8,6     8,7     8,8     0,9     0,10    8,11
        # 11,0   11,1   11,2   11,3   11,4   11,5     11,6     11,7     1,8     0,9     0,10    8,11


    def get_commute_time(self, source_node: tuple, dest_node: tuple, time_weight: int):
        """
        Calculates the commute time based on time of day and the zone population. Source and Destination
        node must have a direct edge between them
        :param source_node: Node from which commute starts
        :param dest_node: Node at which commute ends
        :param time_weight: Time of day during the simulation
        :return: Float value which gives the new commute time between source to destination node

        >>> city =  City(2, 2, [100, 400, 800, 1400], [0.4, 0.2, 0.2, 0.1, 0.1])
        >>> City.default_commute_time < city.get_commute_time((3,4), (3,5), 2) <=  City.default_commute_time * (1 + 2)
        True
        >>> time = city.get_commute_time((3,4), (2,1), 3) # doctest: +ELLIPSIS
        Commute time cannot be changed as there is no direct path between source and destination...
        >>> time == City.default_commute_time
        True
        >>> time = city.get_commute_time((6,6), (2,1), 3) # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        Exception: Invalid Source or Destination Node.
        """
        if self.city_graph.has_edge(source_node, dest_node):
            likely = 0.5 * (self.likely_vals[self.city_graph.nodes[source_node]['Zone_Number']] + self.likely_vals[self.city_graph.nodes[dest_node]['Zone_Number']])
            traffic_time = mod_pert_random(low=0, likely=likely, high=1, samples=1)
            traffic_time *= time_weight
            commute_time = City.default_commute_time + City.default_commute_time * traffic_time
            return float(commute_time)
        elif self.city_graph.has_node(source_node) & self.city_graph.has_node(dest_node):
            print(f"Commute time cannot be changed as there is no direct path between source and "
                  f"destination. Returning default time: {City.default_commute_time}")
            return float(City.default_commute_time)
        else:
            raise Exception("Invalid Source or Destination Node.")

    def build_city_graph(self):
        """
        Builds a graph with an n*n grid of coordinates representing every zone, with n being the
        class variable zone_dimension. A node is a tuple of coordinates governed by the specified
        height, width and zone_dimension. Total nodes in a row is given by width of the object * n,
        and total nodes in a column is given by height of the object * n. There is an edge between
        every vertically and horizontally adjacent node, and no diagonal edges. The time taken to
        go traverse between adjacent node has been set to the default value specified as class variable.
        :return: None. Modifies graph object in place

        >>> city =  City(2, 1, [400, 800], [0.4, 0.2, 0.2, 0.1, 0.1])
        >>> city.build_city_graph()
        >>> truth = True
        >>> for (r, c) in list(city.city_graph.nodes):
        ...     val = city.check_coordinates(r, c)
        ...     truth *= val
        >>> truth
        1
        >>> ((0, 0), (1, 1)) in list(city.city_graph.edges)
        False
        >>> ((1, 2), (1, 3)) in list(city.city_graph.edges)
        True
        >>> ((1, 2), (1, 4)) in list(city.city_graph.edges)
        False
        >>> zone_dict = {}
        >>> for (r, c) in list(city.city_graph.nodes):
        ...     zone = city.city_graph.nodes[(r, c)]['Zone_Number']
        ...     if zone in zone_dict:
        ...         zone_dict[zone] += 1
        ...     else:
        ...         zone_dict[zone] = 1
        >>> set(zone_dict.values()) == {City.zone_dimension**2}
        True
        """

        # Adding Nodes
        zone_num = -1
        for i in range(City.zone_dimension * self.height):
            for j in range(City.zone_dimension * self.width):
                if (j == 0) or (j % City.zone_dimension == 0):
                    zone_num += 1
                self.city_graph.add_nodes_from([((i, j), {'Zone_Number': zone_num,
                                                          'Zone_Population': self.zone_populations[zone_num],
                                                          'Coord_Population': self.zone_populations[
                                                                                  zone_num] / City.zone_dimension ** 2})])
            if (i == 0) or (i % City.zone_dimension != 0):
                zone_num -= self.width

        # Adding Edges
        nodes = list(self.city_graph.nodes)
        for (i, j) in nodes:
            if self.city_graph.has_node((i, j + 1)):
                self.city_graph.add_edge((i, j), (i, j + 1), adjusted_time=City.default_commute_time)
            if self.city_graph.has_node((i + 1, j)):
                self.city_graph.add_edge((i, j), (i + 1, j), adjusted_time=City.default_commute_time)


    def update_graph_edges(self, time_of_day: int):
        """
        Update graph edges which is constant + traffic parameter
        :param time_of_day:
        :return:
        """
        for (i, j) in self.city_graph.nodes:
            if self.city_graph.has_node((i, j + 1)):
                commute_time = self.get_commute_time((i, j), (i, j+1), City.traffic_time_weights[time_of_day])
                self.city_graph[(i, j)][(i, j + 1)]['adjusted_time'] = commute_time
            if self.city_graph.has_node((i + 1, j)):
                commute_time = self.get_commute_time((i, j), (i+1, j), City.traffic_time_weights[time_of_day])
                self.city_graph[(i, j)][(i + 1, j)]['adjusted_time'] = commute_time

    def check_coordinates(self, x, y):
        if y < self.width*City.zone_dimension and x < self.height*City.zone_dimension:
            return True
        else:
            return False
