#class for household agent
from mesa import Agent
import numpy as np
from scipy.stats import norm



class Household(Agent):
    """A household agent with unique id and position in the grid"""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.income = 0 # 1: low income, 2: mid income, 3: high income
        self.stubborness_factor = 0
        self.environmental_consciousness = 0
        self.education_level = 0 # 1: low education, 2: high school, 3: university
        self.type = 0 # 1: house, 2:apartment
        self.solar_panels = 0 # 0: no solar panels, 1: solar panels installed
        self.subsidy = 0 # 0: no subsidy, 1: subsidy received

    def set_income(self, income):
        """Set the income of the household"""
        self.income = income
    def set_stubborness_factor(self, factor):
        """Set the stubbornness factor of the household"""
        self.stubborness_factor = factor
    def set_environmental_consciousness(self, consciousness):
        """Set the environmental consciousness of the household"""
        self.environmental_consciousness = consciousness
    def set_type(self, apt_type):
        """Set the type of the household"""
        self.type = apt_type
    def set_future_awareness(self, awareness):
        """Set the future awareness of the household"""
        self.future_awareness = awareness
    def set_education_level(self, level):
        """Set the education level of the household"""
        self.education_level = level
    def set_solar_panels(self, solar_panels):
        """Set the solar panels of the household"""
        self.solar_panels = solar_panels
    def set_subsidy(self, subsidy):
        """Set the subsidy of the household"""
        self.subsidy = subsidy
    def get_neighbours(self, grid):
        """Get the neighbors of the household in the grid"""
        if self.type == 2:
            include_center = True
        else:
            include_center = False
        return grid.get_neighbors(self.pos, include_center)
    
    def utility(self, grid, citymodel, beta1, beta2, beta3, beta4, beta5, beta6, beta7):
        """Calculate the utility of the household based on income, environmental consciousness, and stubbornness factor"""
        # Utility function can be defined here
        neighbours = self.get_neighbours(grid)
        solar_neighbors = [n for n in neighbours if n.solar_panels == 1]
        fraction_with_solar = len(solar_neighbors) / len(neighbours) if neighbours else 0

        noise = np.random.normal(0, 0.5) # Creating noise from a normal distribution

        utility = beta1 * (self.income / 3) + beta2 * self.environmental_consciousness  + beta3 * fraction_with_solar - beta4 * self.stubborness_factor + beta5 * (self.education_level/3) + beta6 * self.subsidy * citymodel.subsidy + beta7 * (1 - self.type) + noise
        return utility
    
    def step(self, grid, citymodel, beta1, beta2, beta3, beta4, beta5, beta6, beta7):
        """Define the step function for the household agent"""
        # get neighbors with solar panels
        if self.solar_panels == 1:
            return
        utility = self.utility(grid, citymodel, beta1, beta2, beta3, beta4, beta5, beta6, beta7)
        # Input utility into a standard normal distribution to get probability of installation
        prob_installation = norm.cdf(utility)
        #print(f"Household {self.unique_id} utility: {utility}, probability of installation: {prob_installation}")
        if 0.98 < prob_installation:
            self.solar_panels = 1


