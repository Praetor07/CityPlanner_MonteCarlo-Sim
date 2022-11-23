import random
import math
import CityConfiguration


class Emergency:
    # Class variable - Dictionary mapping different intensities to number of emergency teams and total time taken to
    # resolve once team reaches location of emergency
    # Class variable - Threshold of time for emergency resolution for it to be considered successfully resolved.
    # Class variable - List containing time taken for resolution of each emergency
    def __init__(self, city: CityConfiguration.City):
        """
        Initialize location and intensity of emergency using probability distributions.
        If location of emergency is same as that of emergency response unit, we assume a small time as
        coordinates represent approximate locations
        """
        total = int(sum(city.coordinate_pop_densities))
        n = random.randint(0, total)
        for i in range(len(city.cumulative_sum_densities)):
            if n <= city.cumulative_sum_densities[i]:
                loc = i
                break
        # loc=33
        zone = math.floor(loc/9)
        # print(loc)
        # print(zone)
        zone_row = zone % city.height
        zone_col = math.floor(zone/city.height)
        # print(zone_row)
        # print(zone_col)
        if zone != 0:
            pos = loc % (zone*9)
        else:
            pos = loc
        self.location = ((zone_row*3) + math.floor(pos/3), (zone_col*3) + (pos % 3))
        print(self.location)

    def resolve_emergency(self):
        """
        Resolve emergency.
        :return:
        """

    def resolve_emergency(self):
        """
        Determine if emergency was resolved successfully and time taken to resolve emergency.
        :return:
        """