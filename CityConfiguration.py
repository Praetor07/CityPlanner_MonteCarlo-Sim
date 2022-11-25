import networkx as nx

class City:
    # Class variable - represents size of each zone in terms of coordinates
    # Class variable - represents constant time between two adjacent nodes with no traffic between them
    def __init__(self, width: int, height: int, population_densities: list):
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
        self.population_densities = population_densities
        self.coordinate_pop_densities = []
        for p in population_densities:
            for _ in range(9): # number of nodes per zone?
                self.coordinate_pop_densities.append(p)
        self.cumulative_sum_densities = []
        for i in range(len(self.coordinate_pop_densities)):
            if i == 0:
                self.cumulative_sum_densities.append(self.coordinate_pop_densities[i])
            else:
                self.cumulative_sum_densities.append(self.coordinate_pop_densities[i] +
                                                     self.cumulative_sum_densities[i - 1])

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