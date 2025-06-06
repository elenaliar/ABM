#class for household agent
from mesa import Agent


class Household(Agent):
    """A household agent with unique id and position in the grid"""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.income = 0 # 1: low income, 2: mid income, 3: high income
        self.stubborness_factor = 0
        self.environmental_consciousness = 0
        self.type = 0 # 1: house, 2:apartment
        self.future_awareness = 0
        self.solar_panels = 0 # 0: no solar panels, 1: solar panels installed

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
    def set_solar_panels(self, solar_panels):
        """Set the solar panels of the household"""
        self.solar_panels = solar_panels

