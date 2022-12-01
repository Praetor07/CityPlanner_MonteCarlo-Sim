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
    traffic_time_weights = {0:0, 1:2, 2:2, 3:1}
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
        self.build_city_graph()
        # 0,0   0,1   0,2   0,3   0,4   0,5
        # 1,0   1,1   1,2   1,3   1,4   1,5
        # 2,0   2,1   2,2   2,3   2,4   2,5
        # 3,0   3,1   3,2   3,3   3,4   3,5
        # 4,0   4,1   4,2   4,3   4,4   4,5
        # 5,0   5,1   5,2   5,3   5,4   5,5

    def get_commute_time(self, source_node: tuple, dest_node: tuple, time_weight: int):
        """
        Calculates the commute time based on time of day and the zone population
        :param time_of_day: Time of day during the simulation
        :return:
        """
        likely = 0.5 * (self.likely_vals[self.city_graph.nodes[source_node]['Zone_Number']] + self.likely_vals[self.city_graph.nodes[dest_node]['Zone_Number']])
        traffic_time = mod_pert_random(low=0, likely=likely, high=1, samples=1)
        traffic_time *= time_weight
        commute_time = City.default_commute_time + City.default_commute_time * traffic_time
        return commute_time

    def build_city_graph(self):
        # Modeling each zone using 9 nodes as a 3 x 3 set of nodes

        ## Adding Nodes
        zone_num = -1
        for i in range(City.zone_dimension * self.height):
            for j in range(City.zone_dimension * self.width):
                if (j == 0) or (j % City.zone_dimension == 0):
                    zone_num += 1
                # print(zone_num)
                self.city_graph.add_nodes_from([((i, j), {'Zone_Number': zone_num,
                                                          'Zone_Population': self.zone_populations[zone_num],
                                                          'Coord_Population': self.zone_populations[
                                                                                  zone_num] / City.zone_dimension ** 2})])
            if (i == 0) or (i % City.zone_dimension != 0):
                zone_num -= self.width

        ## Adding Edges
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
        if x < self.width*3 and y < self.height*3:
            return True
        else:
            return False
