import networkx as nx
import numpy as np


# Function for mod_pert_random has been picked from Mr Weible's example
# from https://github.com/iSchool-597PR/2022_Fall_examples/blob/main/unit_07/Probability_Distributions.ipynb
def mod_pert_random(low, likely, high, confidence=4, samples=10000):
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
        self.city_graph = None
        self.width = width
        self.height = height
        self.zone_populations = zone_populations
        self.coordinate_populations = []
        self.intensity_distribution = intensity_distribution
        for i in range(len(zone_populations)):
            for _ in range(9):  # number of nodes per zone?
                self.coordinate_populations.append(zone_populations[i] / 9)
        self.cumulative_sum_populations = []
        for i in range(len(self.coordinate_populations)):
            if i == 0:
                self.cumulative_sum_populations.append(self.coordinate_populations[i])
            else:
                self.cumulative_sum_populations.append(self.coordinate_populations[i] +
                                                       self.cumulative_sum_populations[i - 1])

        self.city_graph = nx.DiGraph()
        self.build_city_graph()
        # 0,0   0,1   0,2   0,3   0,4   0,5
        # 1,0   1,1   1,2   1,3   1,4   1,5
        # 2,0   2,1   2,2   2,3   2,4   2,5
        # 3,0   3,1   3,2   3,3   3,4   3,5
        # 4,0   4,1   4,2   4,3   4,4   4,5
        # 5,0   5,1   5,2   5,3   5,4   5,5

    def get_commute_time(self, time_of_day:int, zone_pop:int, city_pop:int):
        """
        Calculates the commute time based on time of day and the zone population
        :param time_of_day: Time of day during the simulation
        :param zone_pop: Average population of the zones involved in the commute
        :param city_pop:
        :return:
        """
        likely_val = zone_pop / city_pop
        traffic_time = mod_pert_random(low=0, likely=likely_val, high=1, samples=1)
        traffic_time *= time_of_day
        commute_time = 10 + traffic_time
        return commute_time

    def build_city_graph(self):
        # Modeling each zone using 9 nodes as a 3 x 3 set of nodes

        ## Adding Nodes
        zone_num = -1
        for i in range(3 * self.height):
            for j in range(3 * self.width):
                if (j == 0) or (j % 3 == 0):
                    zone_num += 1
                # print(zone_num)
                self.city_graph.add_nodes_from([((i, j), {'Zone_Number': zone_num,
                                                          'Zone_Population': self.zone_populations[zone_num],
                                                          'Coord_Population': self.zone_populations[zone_num] / 9})])
            if (i == 0) or (i % 3 != 0):
                zone_num -= self.width

        ## Adding Edges
        nodes = list(self.city_graph.nodes)
        for (i, j) in nodes:
            if self.city_graph.has_node((i, j + 1)):
                self.city_graph.add_edge((i, j), (i, j + 1), adjusted_time=10)
            if self.city_graph.has_node((i + 1, j)):
                self.city_graph.add_edge((i, j), (i + 1, j), adjusted_time=10)


    def update_graph_edges(self, time_of_day: int, zone_pop: int, city_pop: int):
        """
        Update graph edges which is constant + traffic parameter
        :param time_of_day:
        :return:
        """
        for (i, j) in self.city_graph.nodes:
            travel_time = self.get_commute_time(time_of_day, zone_pop, city_pop)
            if self.city_graph.has_node((i, j + 1)):
                self.city_graph[(i, j)][(i, j+1)]['adjusted_time'] = travel_time
            if self.city_graph.has_node((i + 1, j)):
                self.city_graph[(i, j)][(i + 1, j)]['adjusted_time'] = travel_time

