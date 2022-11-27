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
        # self.cumulative_sum_populations = []
        # for i in range(len(self.coordinate_populations)):
        #     if i == 0:
        #         self.cumulative_sum_populations.append(self.coordinate_populations[i])
        #     else:
        #         self.cumulative_sum_populations.append(self.coordinate_populations[i] +
        #                                                self.cumulative_sum_populations[i - 1])

    def build_city_graph(self):
        # Modeling each zone using 9 nodes as a 3 x 3 set of nodes

        ## Adding Nodes
        self.city_graph = nx.DiGraph()
        zone_num = -1
        for i in range(3*self.height):
            for j in range(3*self.width):
                if (j == 0) or (j % 3 == 0):
                    zone_num += 1
                # print(zone_num)
                self.city_graph.add_nodes_from([((i,j), {'Zone_Number': zone_num, 'Zone_Population':self.zone_populations[zone_num], 'Coord_Population':self.zone_populations[zone_num]/9})])
            if (i == 0) or (i % 3 != 0):
                zone_num -= self.width

        ## Adding Edges
        for (i,j) in self.city_graph.nodes:
            self.city_graph.add_edge((i,j), (i,j+1))
            self.city_graph.add_edge((i, j), (i+1, j))

        return self.city_graph

    def update_graph_edges(self, time_of_day: int):
        """
        Update graph edges which is constant + traffic parameter
        :param time_of_day:
        :return:
        """
        self.city_graph = nx.DiGraph()
        # 0,0   0,1   0,2   0,3   0,4   0,5
        # 1,0   1,1   1,2   1,3   1,4   1,5
        # 2,0   2,1   2,2   2,3   2,4   2,5
        # 3,0   3,1   3,2   3,3   3,4   3,5
        # 4,0   4,1   4,2   4,3   4,4   4,5
        # 5,0   5,1   5,2   5,3   5,4   5,5