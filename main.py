import math
import random
import re

from Emergency import Emergency
from CityConfiguration import City
from EmergencyUnit import EmergencyUnit
from threading import Thread
import numpy as np
import pandas as pd
from tqdm import tqdm

def poisson_probability(rates: np.array) -> np.array:
    """

    :param rates:
    :return:
    >>> res = poisson_probability(np.asarray([0.0256, 0.349, 0.00127]))
    >>> [round(prob, 5) for prob in res]
    [0.02495, 0.24618, 0.00127]
    """
    if rates.dtype == np.float64:
        return rates * np.exp(-1*rates)
    else:
        raise ValueError("Rates cannot be converted to poisson probabilities ")

def configure_city_file():
    city_init = 0
    with open('./config/configuration.txt', 'r') as f:
        present_line = f.readline()
        while present_line:
            if re.search('dimension', present_line,re.IGNORECASE):
                counter = 0
                city_init += 1
                while counter < 2:
                    temp_string = f.readline()
                    if re.search('height', temp_string, re.IGNORECASE):
                        height = int(temp_string.split(' ')[-1])
                        if height <= 0:
                            raise ValueError
                    if re.search('width', temp_string, re.IGNORECASE):
                        width = int(temp_string.split(' ')[-1])
                        if width <= 0:
                            raise ValueError
                    counter += 1
            if re.search('population', present_line, re.IGNORECASE):
                city_init += 1
                populations_list = np.empty(width * height)
                counter = 0
                while counter < height*width:
                    population = int(f.readline().split()[0])
                    populations_list[counter] = population
                    counter += 1
            if re.search('intensity', present_line, re.IGNORECASE):
                city_init += 1
                intensity = f.readline()
                intensity_distributions = [float(i) for i in intensity.split(' ')]
            if city_init == 3:
                city_configured = City(width, height, populations_list, intensity_distributions)
            if re.search('small building', present_line, re.IGNORECASE):
                count_of_small_buildings = int(f.readline().split()[0])
                counter = 0
                while counter < count_of_small_buildings:
                    coordinate = f.readline().split(',')
                    if not city_configured.check_coordinates(int(coordinate[0]), int(coordinate[1])):
                        print("Please enter valid coordinates according to the city configured.")
                    else:
                        EmergencyUnit("small", (int(coordinate[0]), int(coordinate[1])))
                    counter += 1
            if re.search('medium building', present_line, re.IGNORECASE):
                count_of_medium_buildings = int(f.readline().split()[0])
                counter = 0
                while counter < count_of_medium_buildings:
                    coordinate = f.readline().split(',')
                    if not city_configured.check_coordinates(int(coordinate[0]), int(coordinate[1])):
                        print("Please enter valid coordinates according to the city configured.")
                    else:
                        EmergencyUnit("medium", (int(coordinate[0]), int(coordinate[1])))
                    counter += 1
            if re.search('large building', present_line, re.IGNORECASE):
                count_of_large_buildings = int(f.readline().split()[0])
                counter = 0
                while counter < count_of_large_buildings:
                    coordinate = f.readline().split(',')
                    if not city_configured.check_coordinates(int(coordinate[0]), int(coordinate[1])):
                        print("Please enter valid coordinates according to the city configured.")
                    else:
                        EmergencyUnit("large", (int(coordinate[0]), int(coordinate[1])))
                    counter += 1
            present_line = f.readline()
    return city_configured

def configure_city():
    try:
        EmergencyUnit.clear_emergency_buildings()
        Emergency.clear_emergencies()
        print("Welcome to the Emergency Response Monte-Carlo Simulation. You will have to configure the city\n"
              "in terms of its dimensions, populations, probability of each intensity type occurring in the 5-point emergency\n"
              "intensity scale (depending on the nature of the city you are designing), and the locations of the emergency\n"
              "unit buildings within the city")
        print("First, you will need to configure the city width and height in terms of the zone unit, where each zone\n"
              "represents a 3X3 square consisting of 9 coordinates")
        width = int(input("Enter the width of the city in terms of number of zones: "))
        if width <= 0:
            raise ValueError()
        height = int(input("Enter the height of the city in terms of number of zones: "))
        if height <= 0:
            raise ValueError()
        print("Now, configure the population of each zone column-wise, assuming that the population is uniformly\n"
              "distributed within each zone.")
        populations = np.empty(width*height)
        for z in range(width*height):
            populations[z] = int(input("Enter the population of zone {}: ".format(z)))
        print("Now, configure the probability of each intensity type of, given that an emergency has occurred -\n"
              "with intensities measured on a scale of 1 to 5 where 1 is the lowest and 5 is the highest\n"
              "For example, if every intensity type is equally likely, then the probabilities for each intensity\n"
              "type would be 0.2. Ensure that the provided probabilities add up to exactly 1.")
        intensity_distributions = np.empty(5)
        while True:
            for intensity in range(1, 6):
                intensity_distributions[intensity-1] = float(input("Enter the probability of the emergency being of intensity {}, given that an emergency has occurred: ".format(intensity)))
            if np.sum(intensity_distributions) != 1.0:
                print("Please ensure that the probabilities add up to exactly 1.")
            else:
                break
        city_configured = City(width, height, populations, intensity_distributions)
        print("Now, configure the types and locations of the emergency unit buildings within the city.\n"
              "There are three types of emergency unit buildings - small buildings each housing 1 emergency response team,\n"
              "medium buildings each housing 3 emergency response teams, and large buildings each housing 5 emergency response teams.")
        while True:
            small_count = int(input("Enter the number of small emergency unit buildings: "))
            medium_count = int(input("Enter the number of medium emergency unit buildings: "))
            large_count = int(input("Enter the number of large emergency unit buildings: "))
            if small_count + medium_count + large_count == 0:
                print("Please ensure that there is atleast one emergency unit building")
            else:
                break
        for size in range(3):
            if size == 0:
                limit = small_count
                building_type = 'small'
            elif size == 1:
                limit = medium_count
                building_type = 'medium'
            else:
                limit = large_count
                building_type = 'large'
            for unit in range(1, limit+1):
                while True:
                    x = int(input("Enter the x-coordinate of {} building {}: ".format(building_type, unit)))
                    y = int(input("Enter the y-coordinate of {} building {}: ".format(building_type, unit)))
                    if not city_configured.check_coordinates(x, y):
                        print("Please enter valid coordinates according to the city configured.")
                    else:
                        EmergencyUnit(building_type, (x, y))
                        break
        return city_configured
    except ValueError:
        print("Please enter only numeric values.")


def simulate(city):
    thread_list = []
    # populations = [2400, 3500, 900, 4500]
    # intensity_distributions = [0.2, 0.2, 0.2, 0.2, 0.2]
    # test = City(2, 2, populations, intensity_distributions)
    # test.build_city_graph()
    # print(test.city_graph.nodes)
    # nx.draw(test.city_graph, with_labels=True)
    # e1 = EmergencyUnit(3, (1, 1))
    # e2 = EmergencyUnit(3, (1, 4))
    # e3 = EmergencyUnit(3, (4, 1))
    # e4 = EmergencyUnit(3, (4, 4))
    test = city
    seconds_in_a_day = 86400
    base_rate_for_emergency = 0.219
    base_population = 200000
    base_rate_per_person = base_rate_for_emergency/base_population
    zone_probabilities = poisson_probability(base_rate_per_person * np.asarray(test.zone_populations))
    aggregate_resp_times = []
    aggregate_perc_successful = []
    # Obtained code for displaying progress bar in for loop from: https://stackoverflow.com/questions/3160699/python-progress-bar
    for run in tqdm(range(1, 101)):
        for i in range(seconds_in_a_day):
            if i in [21599, 43119, 64799]:
                test.update_graph_edges(math.floor((i+1)/21600))
            for zone in range(len(zone_probabilities)):
                prob = zone_probabilities[zone]*1000000
                if random.randint(1, 1000000) <= prob:
                    e = Emergency(test, zone)
                    th = Thread(target=e.resolve_emergency(), daemon=False)
                    th.start()
                    thread_list.append(th)
        for th in thread_list:
            th.join()
        thread_list = []
        resp_times = list()
        successful_response_emergencies = 0
        for emergency in Emergency.emergencies:
            if emergency.time_to_respond <= Emergency.resolution_time_threshold:
                successful_response_emergencies += 1
            resp_times.append(emergency.time_to_respond)
        # print("{}".format(run))
        avg_resp_time = np.mean(np.asarray(resp_times))
        perc_successful = (successful_response_emergencies/len(resp_times))*100
        if run == 1:
            aggregate_resp_times.append(avg_resp_time)
            aggregate_perc_successful.append(perc_successful)
        else:
            resp_time_sum_until_now = aggregate_resp_times[-1] * len(aggregate_resp_times)
            avg_resp_time = (resp_time_sum_until_now + avg_resp_time)/run
            aggregate_resp_times.append(avg_resp_time)
            perc_sum_until_now = aggregate_perc_successful[-1] * len(aggregate_perc_successful)
            avg_perc_successful = (perc_sum_until_now + perc_successful)/run
            aggregate_perc_successful.append(avg_perc_successful)
        Emergency.clear_emergencies()
    EmergencyUnit.clear_emergency_buildings()
    return aggregate_resp_times, aggregate_perc_successful

# if __name__ == '__main__':
#     city = configure_city_file()
#     simulate(city)
