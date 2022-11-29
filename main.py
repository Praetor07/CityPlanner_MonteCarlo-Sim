import math
import random
from Emergency import Emergency
from CityConfiguration import City
from EmergencyUnit import EmergencyUnit
from threading import Thread
import numpy as np
import networkx as nx

def allocate_emergency_units(self, emergency_units: dict):
    """
    Determine optimal available emergency units to be allocated to resolve the emergency.
    :param emergency_units:
    :return:
    """
#population of each zones
#emergency rate
#scale of emergency
#


def poisson_probability(rates: np.array) -> np.array:
    return rates * np.exp(-1*rates)


if __name__ == '__main__':
    thread_list = []
    populations = [2400, 3500, 900, 4500]
    intensity_distributions = [0.2, 0.2, 0.2, 0.2, 0.2]
    test = City(2, 2, populations, intensity_distributions)
    city = test.build_city_graph()
    print(test.city_graph.nodes)
    # nx.draw(test.city_graph, with_labels=True)
    e1 = EmergencyUnit(3, (1, 1))
    e2 = EmergencyUnit(3, (1, 4))
    e3 = EmergencyUnit(3, (4, 1))
    e4 = EmergencyUnit(3, (4, 4))
    # print(city.nodes)
    # print(city.nodes[(0,0)]['Coord_Population'])
    # print(city.edges)

    # for i in range(25):
    #     e = Emergency(test, 3, [0.1, 0.1, 0.1, 0.1, 0.6])
    seconds_in_a_day = 86400
    base_rate_for_emergency = 0.219
    base_population = 200000
    base_rate_per_person = base_rate_for_emergency/base_population
    zone_probabilities = poisson_probability(base_rate_per_person * np.asarray(populations))
    # print(zone_probabilities)
    # exit()
    avg_resp_times = []
    for run in range(1, 101):
        for i in range(seconds_in_a_day):
            if i in [21599, 43119, 64799]:
                test.update_graph_edges(math.floor((i+1)/21600))
            for zone in range(zone_probabilities.shape[0]):
                prob = zone_probabilities[zone]*1000000
                if random.randint(1, 1000000) <= prob:
                    e = Emergency(test, zone)
                    th = Thread(target=e.resolve_emergency(), daemon=False)
                    th.start()
                    thread_list.append(th)
        for th in thread_list:
            th.join()
        resp_times = []
        for emergency in Emergency.emergencies:
            resp_times.append(emergency.resolution_time)
        avg = np.mean(np.asarray(resp_times))
        if run == 1:
            avg_resp_times.append(avg)
        else:
            sum_until_now = avg_resp_times[-1] * len(avg_resp_times)
            avg = (sum_until_now+avg)/run
            avg_resp_times.append(avg)
        Emergency.clear_emergencies()
    for avg in avg_resp_times:
        print(avg)
        # e = Emergency(test)
        #List of all the population densities
        #Scaling the emergency rate
        #feed all values into the poisson distribution to get the probabilities
        #based on the probabilities decide if emergency occurs [0/1 array]
        #randomize location in that zone for the emergency
        #run algo further
    # Take input of city zone configuration -
    # For loop for one day- each iteration represents 1 unit of time (ex: 1 minute)
        # Within one day - time parameter between edges is updated by changing traffic penalty parameter
        # (which is a function of time and population density) - graph edges are updates 4 times a day