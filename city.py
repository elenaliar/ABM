from mesa import Model
from household import Household
from grid import Grid
from mesa.time import RandomActivation  # Or another scheduler
import random
from random import choice
random.seed(42)  # For reproducibility

class CityModel(Model):
    def __init__(self, width, height, num_agents):
        self.num_agents = num_agents
        self.grid = Grid(width, height)
        self.schedule = RandomActivation(self)

        # Divide the grid into quadrants for neighborhoods
        mid_x = width // 2
        mid_y = height // 2

        # Define 9 rectangular neighborhoods (can be uneven)
        neighborhoods = [
            {"x_range": (0, 84), "y_range": (0, 64), "income_dist": [1, 2, 3], "weights": [0.8, 0.15, 0.05]},     # 57x38
            {"x_range": (84, 120), "y_range": (66, 120), "income_dist": [1, 2, 3], "weights": [0.6, 0.3, 0.1]},     # 36x54
            {"x_range": (0, 39), "y_range": (38, 64), "income_dist": [1, 2, 3], "weights": [0.75, 0.2, 0.05]},    # 39x26
            {"x_range": (39, 51), "y_range": (46, 64), "income_dist": [2, 3, 1], "weights": [0.7, 0.2, 0.1]},     # 12x18
            {"x_range": (39, 51), "y_range": (38, 46), "income_dist": [2, 1, 3], "weights": [0.7, 0.2, 0.1]},     # 12x8
            {"x_range": (51, 57), "y_range": (38, 42), "income_dist": [2, 3, 1], "weights": [0.7, 0.2, 0.1]},     # 6x4
            {"x_range": (51, 94), "y_range": (42, 64), "income_dist": [3, 2, 1], "weights": [0.7, 0.2, 0.1]},     # 33x22
            {"x_range": (94, 120), "y_range": (42, 66), "income_dist": [2, 1, 3], "weights": [0.7, 0.2, 0.1]},     # 36x24
            {"x_range": (57, 120), "y_range": (0, 42), "income_dist": [3, 2, 1], "weights": [0.7, 0.2, 0.1]},     # 63x42
            {"x_range": (0, 84), "y_range": (64, 66), "income_dist": [3, 2, 1], "weights": [0.7, 0.2, 0.1]}, 
            {"x_range": (0, 84), "y_range": (64, 120), "income_dist": [2, 3, 1], "weights": [0.7, 0.2, 0.1]}         #84x56
        ]


        # Precompute area-based weights for neighborhood selection
        for n in neighborhoods:
            x_min, x_max = n["x_range"]
            y_min, y_max = n["y_range"]
            n["area"] = (x_max - x_min) * (y_max - y_min)

        total_area = sum(n["area"] for n in neighborhoods)
        area_weights = [n["area"] / total_area for n in neighborhoods]


        next_id = 0  # track agent IDs

        while next_id < self.num_agents:
            neighborhood = random.choices(neighborhoods, weights=area_weights, k=1)[0]
            x_min, x_max = neighborhood["x_range"]
            y_min, y_max = neighborhood["y_range"]

            x = self.random.randrange(x_min, x_max)
            y = self.random.randrange(y_min, y_max)

            agent_type = random.choices([1, 2], weights=[0.6, 0.4])[0]#house or apartment

            if agent_type == 1 and not self.grid.is_cell_empty((x, y)):
                continue  # skip if house but spot is taken

            agent = Household(next_id, self)
            income = random.choices(neighborhood["income_dist"], weights=neighborhood["weights"])[0]
            agent.set_income(income)
            agent.set_type(agent_type)
            #randomly assign environmental consciousness from uniform distribution
            agent.set_environmental_consciousness(random.uniform(0, 1))
            #same for stubbornness factor
            agent.set_stubborness_factor(random.uniform(0, 1))


            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
            next_id += 1
