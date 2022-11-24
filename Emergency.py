import random
import math
import CityConfiguration
from main import allocate_emergency_units

class Emergency:
    zone_dimension = 3
    # Class variable - Dictionary mapping different intensities to number of emergency teams and total time taken to
    # resolve once team reaches location of emergency
    intensity_mapping = {1: {'teams': 3, 'time': 5}, 2: {'teams': 4, 'time': 10}, 3: {'teams': 5, 'time': 15},
                         4: {'teams': 6, 'time': 20}, 5: {'teams': 7, 'time': 25}}
    # Class variable - Threshold of time for emergency resolution for it to be considered successfully resolved.
    resolution_time_threshold = 25
    # Class variable - List containing time taken for resolution of each emergency
    emergencies = []
    def __init__(self, city: CityConfiguration.City, zone: int, intensity_distribution: list):
        """
        Initialize location and intensity of emergency using probability distributions.
        If location of emergency is same as that of emergency response unit, we assume a small time as
        coordinates represent approximate locations
        """
        # total = int(sum(city.coordinate_pop_densities))
        # n = random.randint(0, total)
        # for i in range(len(city.cumulative_sum_densities)):
        #     if n <= city.cumulative_sum_densities[i]:
        #         loc = i
        #         break
        # # loc=33
        # zone = math.floor(loc/9)
        # print(loc)
        # print(zone)
        self.resolution_time = None
        zone_row = zone % city.height
        zone_col = math.floor(zone/city.height)
        # print(zone_row)
        # print(zone_col)
        loc = random.randint(0, (Emergency.zone_dimension ** 2) - 1)
        r = math.floor(loc/Emergency.zone_dimension)
        c = loc % Emergency.zone_dimension
        self.location = ((zone_row*Emergency.zone_dimension) + r, (zone_col*Emergency.zone_dimension) + c)
        # print(self.location)
        self.intensity_distribution = [int(intensity*100) for intensity in intensity_distribution]
        self.intensity_cumulative = []
        for i in range(len(self.intensity_distribution)):
            if i == 0:
                self.intensity_cumulative.append(self.intensity_distribution[i])
            else:
                self.intensity_cumulative.append(self.intensity_cumulative[-1] + self.intensity_distribution[i])
        rand = random.randint(1, self.intensity_cumulative[-1])
        for i in range(len(self.intensity_cumulative)):
            if rand <= self.intensity_cumulative[i]:
                self.intensity = i + 1
                break
        print(self.intensity)
        self.emergencies.append(self)
        self.city_of_emergency = city
        self.resolve_emergency()

    def resolve_emergency(self):
        emergency_units, time_taken_to_reach = allocate_emergency_units(self.intensity_mapping[self.intensity]['teams'])
        time_to_resolve = time_taken_to_reach + self.intensity_mapping[self.intensity]['time']
        self.resolution_time = time_to_resolve
        total_time = time_to_resolve + time_taken_to_reach
        for _ in range(total_time):
            pass
        for emergency_unit, num_teams in emergency_units:
            emergency_unit.release_teams(num_teams)

