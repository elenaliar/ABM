from mesa import Model
from household import Household
from grid import Grid
from mesa.time import RandomActivation  # Or another scheduler
from mesa.datacollection import DataCollector
import random
from random import choice
random.seed(42)  # For reproducibility

class CityModel(Model):
    def __init__(self, width, height, num_agents, subsidy=0, subsidy_timestep=0):
        self.num_agents = num_agents
        self.grid = Grid(width, height)
        self.schedule = RandomActivation(self)
        self.subsidy = subsidy  # Subsidy flag, 0 if government does not provide subsidy, 1 if it does
        self.running = True
        self.subsidy_timestep = subsidy_timestep # Timestep when subsidy is applied

        # Number of household per income level and apartment type
        self.incomes = {
            1: {"count": 0, "houses": 0, "apartments": 0},
            2: {"count": 0, "houses": 0, "apartments": 0},
            3: {"count": 0, "houses": 0, "apartments": 0}
        }

        self.datacollector = DataCollector(
        model_reporters={
        "Low Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 1 and a.solar_panels == 1 and a.type == 1),
        "Low Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 1 and a.solar_panels == 1 and a.type == 2),
        "Mid Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 2 and a.solar_panels == 1 and a.type == 1),
        "Mid Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 2 and a.solar_panels == 1 and a.type == 2),
        "High Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 3 and a.solar_panels == 1 and a.type == 1),
        "High Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 3 and a.solar_panels == 1 and a.type == 2),
        }
        )

        # Define 9 rectangular neighborhoods (can be uneven)
        neighborhoods = [
            {"x_range": (0, 84), "y_range": (0, 64), "income_dist": [1, 2, 3], "weights": [0.85, 0.15, 0.0]},     # 57x38
            {"x_range": (84, 120), "y_range": (66, 120), "income_dist": [1, 2, 3], "weights": [0.6, 0.39, 0.01]},     # 36x54
            {"x_range": (0, 39), "y_range": (38, 64), "income_dist": [1, 2, 3], "weights": [0.75, 0.25, 0.0]},    # 39x26
            {"x_range": (39, 51), "y_range": (46, 64), "income_dist": [2, 3, 1], "weights": [0.7, 0.2, 0.1]},     # 12x18
            {"x_range": (39, 51), "y_range": (38, 46), "income_dist": [2, 1, 3], "weights": [0.7, 0.2, 0.1]},     # 12x8
            {"x_range": (51, 57), "y_range": (38, 42), "income_dist": [2, 3, 1], "weights": [0.7, 0.2, 0.1]},     # 6x4
            {"x_range": (51, 94), "y_range": (42, 64), "income_dist": [3, 2, 1], "weights": [0.7, 0.3, 0.0]},     # 33x22
            {"x_range": (94, 120), "y_range": (42, 66), "income_dist": [2, 1, 3], "weights": [0.7, 0.1, 0.2]},     # 36x24
            {"x_range": (57, 120), "y_range": (0, 42), "income_dist": [3, 2, 1], "weights": [0.7, 0.3, 0.0]},     # 63x42
            {"x_range": (0, 84), "y_range": (64, 66), "income_dist": [3, 2, 1], "weights": [0.7, 0.3, 0.0]}, 
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

            agent = Household(next_id, self)
            income = random.choices(neighborhood["income_dist"], weights=neighborhood["weights"])[0]
            agent.set_income(income)


            agent.set_environmental_consciousness(random.uniform(0, 1))
            agent.set_stubborness_factor(random.uniform(0, 1))

            if income == 1:
                agent.set_subsidy(0)  # low income households get subsidy if available
                education_level = random.choices([1, 2, 3], weights=[0.1, 0.6, 0.3])[0]  # 10% low education, 60% high school, 30% university
                agent.set_education_level(education_level)
                self.incomes[1]["count"] += 1
                    
                agent_type = random.choices([1, 2], weights=[0.2, 0.8])[0] # 20% chance of house, 80% chance of apartment
                if agent_type == 1:
                    self.incomes[1]["houses"] += 1
                else:
                    self.incomes[1]["apartments"] += 1

                if agent_type == 1 and not self.grid.is_cell_empty((x, y)):
                    # if the cell x,y is an agent with agent type = 2, put the agent as apartment
                    x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                    while not self.grid.is_cell_empty((x, y)):
                        x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                    agent.set_type(agent_type)

                elif agent_type == 2 and not self.grid.is_cell_empty((x, y)):
                    if self.grid.get_cell_list_contents((x, y))[0].type == 1:
                        x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                        while (not self.grid.is_cell_empty((x, y)) and 
                            (self.grid.get_cell_list_contents((x, y))[0].type == 2)):
                            x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                        agent.set_type(agent_type)
                    elif self.grid.get_cell_list_contents((x, y))[0].type == 2:
                        agent.set_type(agent_type)

        
            elif income == 2:
                agent.set_subsidy(0) # set subsidy with probability 50%
                education_level = random.choices([1, 2, 3], weights=[0.05, 0.2, 0.75])[0]  # 5% low education, 20% high school, 75% university
                agent.set_education_level(education_level)
                self.incomes[2]["count"] += 1

                agent_type = random.choices([1, 2], weights=[0.5, 0.5])[0] # 50% chance of house, 50% chance of apartment
                if agent_type == 1:
                    self.incomes[2]["houses"] += 1
                else:
                    self.incomes[2]["apartments"] += 1

                if agent_type == 1 and not self.grid.is_cell_empty((x, y)):
                    x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                    while not self.grid.is_cell_empty((x, y)):
                        x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                    agent.set_type(agent_type)

                elif agent_type == 2 and not self.grid.is_cell_empty((x, y)):
                    if self.grid.get_cell_list_contents((x, y))[0].type == 1:
                        x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                        while (not self.grid.is_cell_empty((x, y)) and 
                            self.grid.get_cell_list_contents((x, y))[0].type == 2):
                            x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                        agent.set_type(agent_type)
                    elif self.grid.get_cell_list_contents((x, y))[0].type == 2:
                        agent.set_type(agent_type)
            
            else:
                agent.set_subsidy(0)
                education_level = random.choices([1, 2, 3], weights=[0.01, 0.1, 0.89])[0]
                agent.set_education_level(education_level)
                self.incomes[3]["count"] += 1

                agent_type = random.choices([1, 2], weights=[0.8, 0.2])[0] # 80% chance of house, 20% chance of apartment
                if agent_type == 1:
                    self.incomes[3]["houses"] += 1
                else:
                    self.incomes[3]["apartments"] += 1

                if agent_type == 1 and not self.grid.is_cell_empty((x, y)):
                    x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                    while not self.grid.is_cell_empty((x, y)):
                        x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                    agent.set_type(agent_type)

                elif agent_type == 2 and not self.grid.is_cell_empty((x, y)):
                    if self.grid.get_cell_list_contents((x, y))[0].type == 1:
                        x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                        while (not self.grid.is_cell_empty((x, y)) and 
                            self.grid.get_cell_list_contents((x, y))[0].type == 2):
                            x, y = self.random.randrange(x_min, x_max), self.random.randrange(y_min, y_max)
                        agent.set_type(agent_type)
                    elif self.grid.get_cell_list_contents((x, y))[0].type == 2:
                        agent.set_type(agent_type)
            
            self.grid.place_agent(agent, (x, y))
            self.schedule.add(agent)
            next_id += 1
    

    def step(self):
        """Advance the model by one step."""
        if self.schedule.time == 0:
            self.datacollector.collect(self)
        if self.schedule.time == self.subsidy_timestep and self.subsidy == 1:
            for agent in self.schedule.agents:
                if agent.income == 1:
                    agent.set_subsidy(1)
                elif agent.income == 2:
                    agent.set_subsidy(1 if random.random() < 0.4 else 0)
                else:
                    agent.set_subsidy(0)

        agents = self.schedule._agents
        agent_keys = list(agents.keys())
        for key in agent_keys:
            if key in agents:
                agents[key].step(self.grid, self)
        self.datacollector.collect(self)
        self.schedule.time += 1
    
    def run_model(self, steps=100):
        """Run the model for a specified number of steps."""
        for i in range(steps):
            self.step()
            if not self.running:
                break


        

