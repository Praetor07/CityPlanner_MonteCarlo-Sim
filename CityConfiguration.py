import networkx as nx
import numpy as np

class City:
    zone_dimension = 3
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
        self.intensity_cumulative = np.cumsum(np.rint(np.asarray(self.intensity_distribution)))
        for i in range(len(zone_populations)):
            for _ in range(City.zone_dimension ** 2):# number of nodes per zone?
                self.coordinate_populations.append(zone_populations[i]/(City.zone_dimension ** 2))

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
                                                          'Coord_Population': self.zone_populations[zone_num] / 9})])
            if (i == 0) or (i % City.zone_dimension != 0):
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

