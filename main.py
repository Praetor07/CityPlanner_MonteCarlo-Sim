from Emergency import Emergency
from CityConfiguration import City


def allocate_emergency_units(self, emergency_units: dict):
    """
    Determine optimal available emergency units to be allocated to resolve the emergency.
    :param emergency_units:
    :return:
    """


if __name__ == '__main__':
    pop_densities = [2.4, 3.5, 0.9, 4.5]
    test = City(2, 2, pop_densities)
    for i in range(25):
        e = Emergency(test)
    # Take input of city zone configuration -
    # For loop for one day- each iteration represents 1 unit of time (ex: 1 minute)
        # Within one day - time parameter between edges is updated by changing traffic penalty parameter
        # (which is a function of time and population density) - graph edges are updates 4 times a day