"""
Driver program containing functions that control the input and execution of the Monte-Carlo Simulation.
"""
import math
import random
import re
from Emergency import Emergency
from CityConfiguration import City
from EmergencyUnit import EmergencyUnit
from threading import Thread
import numpy as np
from tqdm import tqdm


class ValidationError(Exception):
    """
    Custom Error class for handling user configuration input exceptions.
    """
    def __init__(self, x: int, flag: str):
        self.x = x
        self.flag = flag

    def __str__(self):
        if self.flag == "rate":
            return f"Didn't receive either rate or base population. Running the simulation using " \
                   f" default values of rate and population"
        return f"Kindly check {self.flag}, its passed as {self.x}. This isn't correct. It should be greater than 0"


def poisson_probability(rates: np.array) -> np.array:
    """
    Given an input numpy array of the per-minute rates of emergency for each zone in the city, calculates and returns
    the probability of an emergency occuring within the next minute in each zone of the city. The probability is
    calculated using the poisson distribution, by finding:  1 - Probability(no emergency occuring within next minute)
    :param rates: Numpy array representing the rates of emergency for each zone in the city
    :return: Numpy array of the probabilities of emergency occurring in the next 1 minute, in each zone of the city
    >>> res = poisson_probability(np.asarray([0.0256, 0.349, 0.00127]))
    >>> [round(p, 5) for p in res]
    [0.02528, 0.29461, 0.00127]
    >>> poisson_probability(np.asarray(['hello', 0.349, 0.00127]))
    Traceback (most recent call last):
    ValueError: Rates cannot be converted to poisson probabilities
    """
    if rates.dtype == np.float64:
        return 1 - np.exp(-1*rates)
    else:
        raise ValueError("Rates cannot be converted to poisson probabilities")


def configure_city_file(configuration_file: str):
    """
    Function to read the configuration file and construct the city
    List of validations being conducted:
    Height/width > 0
    No two Emergency response units should share the same unit
    Only numeric values should be passed
    Population should be greater than 0
    Intensity distributions should sum up to 1
    Unit coordinates should be the same as initial number passed
    If no rate/base population passed, run with default config
    :return:

    >>> configure_city_file("test_config_1.txt") # doctest: +ELLIPSIS
    Kindly check width...
    >>> configure_city_file("test_config_2.txt") # doctest: +ELLIPSIS
    ###Kindly check the configuration file...
    >>> configure_city_file("test_config_3.txt") # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    Exception: Intensity distributions should sum to 1
    >>> configure_city_file("test_config_4.txt") # doctest: +ELLIPSIS
    Coordinates are duplicate...
    >>> c = configure_city_file("test_config_5.txt")
    Didn't receive either rate or base population. Running the simulation using  default values of rate and population
    >>> c[0].coordinate_populations # doctest: +ELLIPSIS
    [500.0, 500.0, 500.0...400.0]
    """
    city_init = 0
    building_flag = ''
    try:
        with open(f"./config/{configuration_file}", 'r') as f:
            present_line = f.readline()
            while present_line:
                if re.search('dimension', present_line, re.IGNORECASE):
                    building_flag = ''
                    counter = 0
                    city_init += 1
                    while counter < 2:
                        temp_string = f.readline()
                        if re.search('height', temp_string, re.IGNORECASE):
                            height = int(temp_string.split(' ')[-1])
                            if height <= 0:
                                raise ValidationError(height, "height")
                        if re.search('width', temp_string, re.IGNORECASE):
                            width = int(temp_string.split(' ')[-1])
                            if width <= 0:
                                raise ValidationError(width, "width")
                        counter += 1
                if re.search('population distribution', present_line, re.IGNORECASE):
                    building_flag = ''
                    city_init += 1
                    populations_list = np.empty(width * height)
                    counter = 0
                    while counter < height*width:
                        population = int(f.readline().split()[0])
                        if population <= 0:
                            raise ValidationError(population, "population")
                        populations_list[counter] = population
                        counter += 1
                if re.search('intensity', present_line, re.IGNORECASE):
                    building_flag = ''
                    city_init += 1
                    intensity = f.readline()
                    intensity_distributions = np.asarray([float(i) for i in intensity.split(' ')])
                    if intensity_distributions.sum() != 1:
                        raise Exception("Intensity distributions should sum to 1")
                if city_init == 3:
                    city_configured = City(width, height, populations_list, intensity_distributions)
                if re.search('small building', present_line, re.IGNORECASE):
                    building_flag = "small"
                    count_of_small_buildings = int(f.readline().split()[0])
                    counter = 0
                    while counter < count_of_small_buildings:
                        coordinate = f.readline().strip().split(',')
                        if not city_configured.check_coordinates(int(coordinate[0]), int(coordinate[1])):
                            print("Please enter valid coordinates according to the city configured.")
                        else:
                            EmergencyUnit("small", (int(coordinate[0]), int(coordinate[1])))
                        counter += 1
                if re.search('medium building', present_line, re.IGNORECASE):
                    building_flag = "medium"
                    count_of_medium_buildings = int(f.readline().strip().split()[0])
                    counter = 0
                    while counter < count_of_medium_buildings:
                        coordinate = f.readline().split(',')
                        if not city_configured.check_coordinates(int(coordinate[0]), int(coordinate[1])):
                            print("Please enter valid coordinates according to the city configured.")
                        else:
                            EmergencyUnit("medium", (int(coordinate[0]), int(coordinate[1])))
                        counter += 1
                if re.search('large building', present_line, re.IGNORECASE):
                    building_flag = "large"
                    count_of_large_buildings = int(f.readline().strip().split()[0])
                    counter = 0
                    while counter < count_of_large_buildings:
                        coordinate = f.readline().split(',')
                        if not city_configured.check_coordinates(int(coordinate[0]), int(coordinate[1])):
                            print("Please enter valid coordinates according to the city configured.")
                        else:
                            EmergencyUnit("large", (int(coordinate[0]), int(coordinate[1])))
                        counter += 1
                if re.search('emergency rate', present_line, re.IGNORECASE):
                    building_flag = ''
                    temp_list = f.readline().split(' ')
                    if len(temp_list) == 1:
                        raise ValidationError(0, "rate")
                    configured_base_emergency_rate = temp_list[0]
                    configured_population = temp_list[1]
                present_line = f.readline()
            return city_configured, float(configured_base_emergency_rate), int(configured_population)
    except (ValueError, UnboundLocalError, IndexError) as v:
        if re.search("int|float", v.__str__()):
            if building_flag in ["small", "medium", "large"]:
                print(f"{building_flag} buildings has an issue.Possibly number of buildings != number of coordinates "
                      f"entered")
            print("###Kindly check the configuration file###")
        else:
            print(v)
    except ValidationError as v:
        print(v)
        if re.search("rate", v.__str__(), re.IGNORECASE):
            return city_configured, None, None
    return None, None, None


def simulate(test_city, base_rate_for_emergency: float, base_population: int):
    """
    Performs a Monte-Carlo simulation with 100 runs and each run representing a span of 1 day, of emergencies occurring
    at randomized time and locations within the city, with randomly chosen intensities in the scale of 1 to 5.
    The traffic present across the different paths in the city is randomized and updated 4 times in a day, over the
    span of every 6 hours. The emergencies occurring are responded to by the emergency units configured in specific
    locations across the city, and the statistics of average response time and percentage of successfully responded
    emergencies are calculated for each run of the simulation, and are aggregated over all the 100 runs.

    :param test_city: The CityConfiguration object representing the city configured in the simulation - with a
    defined width, height, population of each zone, and emergency units at specific locations.
    :param base_rate_for_emergency: Emergency rate per unit minute as configured in the input file. If no input is given in
    the input file then the default value is considered as calculated from the Montgomery PA data
    :param base_population: Base population as given in the configuration file, if the value isnt given then the default
    value is considered as calculated from the Montgomery PA data
    :return: List of average responses times aggregated after each simulation run, list of percentage of successfully
    responded emergencies aggregated after each simulation run, total number of emergencies that occurred in the
    entire duration of the simulations, dictionary of details of first 3 emergencies used for visualizations.
    >>> populations = [2500, 2500]
    >>> intensity_distributions = [1, 0, 0, 0, 0]
    >>> test = City(2, 1, populations, intensity_distributions)
    >>> EmergencyUnit.clear_emergency_buildings()
    >>> Emergency.clear_emergencies()
    >>> e1 = EmergencyUnit('small', (1, 1))
    >>> e2 = EmergencyUnit('small', (1, 3))
    >>> e3 = EmergencyUnit('small', (1, 5))
    >>> e4 = EmergencyUnit('small', (0, 2))
    >>> e5 = EmergencyUnit('small', (0, 4))
    >>> e6 = EmergencyUnit('small', (2, 0))
    >>> e7 = EmergencyUnit('small', (2, 2))
    >>> e8 = EmergencyUnit('small', (2, 4))
    >>> e9 = EmergencyUnit('small', (0, 0))
    >>> resp_time, perc, num_emer, emer_dict = simulate(test, None, None)
    >>> 1.0 <= resp_time[-1] <= 3.0
    True
    >>> 90 <= perc[-1]
    True
    """
    # Setting rate of the number of emergencies per minute and the population reference for which the rate was
    # specified to default values, if user input was not provided.
    base_rate_for_emergency = 13.165119 if base_rate_for_emergency is None else base_rate_for_emergency
    base_population = 200000 if base_population is None else base_population
    thread_list = []
    minutes_in_a_day = 1440
    number_of_emergencies = 0
    aggregate_resp_times = []
    aggregate_perc_successful = []
    plotting_emergency_dict = {}
    try:
        if test_city is None:
            raise ValueError("Kindly rerun after checking the file...")
        base_rate_per_person = base_rate_for_emergency/base_population
        zone_probabilities = poisson_probability(base_rate_per_person * np.asarray(test_city.zone_populations))
        # Obtained code for displaying progress bar in for loop from:
        # https://stackoverflow.com/questions/3160699/python-progress-bar
        # Executing 100 simulation runs
        for run in tqdm(range(1, 101)):
            # Each iteration and the corresponding computation in each iteration represents one minute of program/
            # simulation time
            for i in range(minutes_in_a_day):
                # Traffic across the paths in the city are updated 4 times in a day (every 6 hours of real-time)
                if i in [0, 359, 719, 1079]:
                    test_city.update_graph_edges(math.floor((i+1)/360))
                # Using the probability of an emergency occurring in each zone, randomizing if an emergency occurs
                for zone in range(len(zone_probabilities)):
                    prob = zone_probabilities[zone]*1000000
                    if random.randint(1, 1000000) <= prob:
                        # New thread is spawned for every emergency creation and resolution
                        th = Thread(target=Emergency, args=[test_city, zone], daemon=False)
                        th.start()
                        thread_list.append(th)
            for th in thread_list:
                th.join()
            thread_list = []
            resp_times = list()
            successful_response_emergencies = 0
            for emergency in Emergency.emergencies:
                number_of_emergencies += 1
                if emergency.time_to_respond <= Emergency.resolution_time_threshold:
                    successful_response_emergencies += 1
                resp_times.append(emergency.time_to_respond)
            # Calculating average of response time across all emergencies that occurred in 1 day (1 simulation run)
            avg_resp_time = np.mean(np.asarray(resp_times))
            # Calculating percentage of emergencies that were successfully responded to in 1 day (1 simulation run)
            perc_successful = (successful_response_emergencies/len(resp_times))*100
            # Aggregating the average response time and percentage of successfully responded emergencies over
            # all simulation runs
            if run == 1:
                for emergency in Emergency.emergencies[:5]:
                    plotting_emergency_dict[emergency.location] = [tuple(key.location) for key in
                                                                   emergency.response_unit]
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
        return aggregate_resp_times, aggregate_perc_successful, number_of_emergencies, plotting_emergency_dict
    except ValueError as v:
        print(v)
    return [0], [0], [], {}
