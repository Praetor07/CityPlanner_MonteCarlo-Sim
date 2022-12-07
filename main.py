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
    pass

def poisson_probability(rates: np.array) -> np.array:
    """
    :param rates:
    :return:
    >>> res = poisson_probability(np.asarray([0.0256, 0.349, 0.00127]))
    >>> [round(p, 5) for p in res]
    [0.02495, 0.24618, 0.00127]
    """
    if rates.dtype == np.float64:
        return 1 - np.exp(-1*rates)
    else:
        raise ValueError("Rates cannot be converted to poisson probabilities ")

def configure_city_file(configuration_file: str):
    """
    Function to read the configuration file and construct the city
    :return:
    """
    city_init = 0
    try:
        with open(f"./config/{configuration_file}", 'r') as f:
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
                                    raise ValidationError("Kindly check values again. Number is less than 0")
                            if re.search('width', temp_string, re.IGNORECASE):
                                width = int(temp_string.split(' ')[-1])
                                if width <= 0:
                                    raise ValidationError("Kindly check values again. Number is less than 0")
                            counter += 1
                    if re.search('population', present_line, re.IGNORECASE):
                        city_init += 1
                        populations_list = np.empty(width * height)
                        counter = 0
                        while counter < height*width:
                            population = int(f.readline().split()[0])
                            if population <= 0:
                                raise Exception("Population should be greater than 0")
                            populations_list[counter] = population
                            counter += 1
                    if re.search('intensity', present_line, re.IGNORECASE):
                        city_init += 1
                        intensity = f.readline()
                        intensity_distributions = np.asarray([float(i) for i in intensity.split(' ')])
                        if intensity_distributions.sum() != 1:
                            raise Exception("Intensity distributions should sum to 1")
                    if city_init == 3:
                        city_configured = City(width, height, populations_list, intensity_distributions)
                    if re.search('small building', present_line, re.IGNORECASE):
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
                        count_of_large_buildings = int(f.readline().strip().split()[0])
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
    except ValueError:
        print("\n###Please only enter numeric values in the configuration file###")
    except ValidationError as v:
        print(v)

def simulate(test_city):
    thread_list = []
    if test_city is None:
        raise ValidationError("Please check the configuration file...")
    seconds_in_a_day = 1440
    base_rate_for_emergency = 13.165119
    base_population = 200000
    number_of_emergencies = 0
    base_rate_per_person = base_rate_for_emergency/base_population
    zone_probabilities = poisson_probability(base_rate_per_person * np.asarray(test_city.zone_populations))
    aggregate_resp_times = []
    aggregate_perc_successful = []
    plotting_emergency_dict = {}
    # Obtained code for displaying progress bar in for loop from: https://stackoverflow.com/questions/3160699/python-progress-bar
    for run in tqdm(range(1, 101)):
        for i in range(seconds_in_a_day):
            if i in [359, 719, 1079]:
                test_city.update_graph_edges(math.floor((i+1)/360))
            for zone in range(len(zone_probabilities)):
                prob = zone_probabilities[zone]*1000000
                if random.randint(1, 1000000) <= prob:
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
        avg_resp_time = np.mean(np.asarray(resp_times))
        perc_successful = (successful_response_emergencies/len(resp_times))*100
        if run == 1:
            for emergency in Emergency.emergencies[:5]:
                plotting_emergency_dict[emergency.location] = [tuple(key.location) for key in emergency.response_unit]
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


"""if __name__ == '__main__':
     city = configure_city_file('inner_medium_ps.txt')
     resp_times, perc_successfull, emergencies = simulate(city)
     print(f"Total number of emergencies occured: {emergencies}")
     print(f"Average response time: {resp_times[-1]}")
     print(f"Success ratio : {perc_successfull[-1]}")"""
