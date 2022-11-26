**Emergency Response Monte-Carlo Simulation for City Planning**


**Background:**
This project is a Monte-Carlo simulation of a city with random emergency situations that need to be attended to. We have defined the cities to have three types of emergency response unit buildings: Large with 5 emergency response teams, Medium with 3 emergency response teams and Small with 1 emergency response team. Given a configuration with locations of the emergency response unit buildings, a simulation is run randomizing the time, location, and intensity of each emergency, along with possible traffic along the route. The solution finds the average emergency response time and success rate of resolving the emergencies for the given configuration, and can be run over multiple configurations to determine which one produces the minimum response time and maximum success rate for the emergencies. This type of simulation can be useful for city planning.


**Configurable Parameters of Simulation:**
1) Zone Count and Arrangement: Each city is divided into a specified number of equal-sized zones. The number of zones in the city must be specified along with the width and height of the city in terms of the number of zones.
2) Head Count of Each Zone: The number of people residing in each zone must be specified. Each zone can have a different head count.
3) Total Number of Large Emergency Response Unit Buildings: The number of emergency response unit buildings (each having 5 emergency response teams) that can be constructed in the city.
4) Total Number of Medium Emergency Response Unit Buildings: The number of emergency response unit buildings (each having 3 emergency response teams) that can be constructed in the city.
5) Total Number of Small Emergency Response Unit Buildings: The number of emergency response unit buildings (each having 1 emergency response team) that can be constructed in the city.
6) Locations of the Emergency Unit Buildings: The coordinate locations of the emergency unit buildings of each type.


**Randomized Variables:**
1) Time of Emergency: Randomizing the occurrence of emergencies with respect to time - probability distribution of one emergency occurring at current time in each zone is obtained using the poisson distribution modeled using a real dataset.
2) Location of Emergency: Randomizing the location coordinates of the emergency within a zone using uniform distribution
3) Intensity of Emergency: Each emergency can have an intensity which is measured on a scale of 1 to 5, with 1 being the lowest intensity and 5 being the highest intensity. The number of emergency teams and the total time taken to resolve the emergency will be a function of the intensity of the emergency. The intensity of the emergency will be randomized on the discrete scale mentioned above. Probabilities of each intensity will be user input, and as baseline input, a uniform distribution is considered.
4) Traffic: Randomizing the traffic present along the different paths in the city as a probability distribution of the time and population density of the zone.  


**Output Aggregate Statistics After Each Simulation Run:**
1) The percentage of emergencies successfully responded to: We will define a maximum response time for an emergency response to be called successful and estimate the location of emergency response unit buildings to maximize the percentage of emergencies that were successfully responded to
2) The average response time for all successfully responded emergencies


**Assumptions:**
1) Each zone has a defined size that remains constant within a simulation and across all simulations.
2) Within each zone, the population density is uniformly distributed.
3) The coordinate system is used for specifying locations of the entities
4) Euclidean distance or shortest path distance is used to calculate the distance between the emergency occurring and the nearest emergency unit building with teams available. We will add a randomized penalty component to this which will represent the time added due to traffic
5) Each run of the simulation will represent a span of one day
6) An emergency response team located in one zone can respond to emergencies in any zone
7) The emergency is said to be successfully responded to if the emergency response team can respond to the emergency within a certain threshold of time.
8) The base rate (lambda) of emergency occurrence has been calculated using data from Montgomery County on the number of 911 calls - the dataset contains 663522 occurrences recorded in a span of 5 weeks, for the population of approximately 200000 in Montgomery County. This produces an emergency occurrence rate of 0.219 emergencies/second. The program assumes that the emergency occurrence rate is linearly proportional to the population - the base rate of 0.219 for a population of 200000 is used to calculate the rate of emergency occurrence for each zone in the city based on its population, which is used in a poisson distribution to calculate the probability of an emergency occurring in each zone in the next second.