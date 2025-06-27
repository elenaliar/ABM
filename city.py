from mesa import Model
from household import Household
from grid import Grid
from mesa.time import RandomActivation 
from mesa.datacollection import DataCollector
import random
from emergence_analysis import compute_global_adoption, compute_clustering_score, compute_morans_I, gini_between_income_classes

#random.seed(42)  # For reproducibility

class CityModel(Model):
    """ A city simulation model using the Mesa framework to represent households' decisions to adopt solar panels
    based on income, education, environmental consciousness, government subsidies, and social dynamics. """

    def __init__(self, width=120, height=120, num_agents=10000, subsidy=1, subsidy_timestep=0, max_steps=200, beta1 = 0.35,
        beta2 = 0.05, beta3 = 0.5, beta4 = 0.2, beta5 = 0.3, beta6 = 0.3, beta7 = 0.6, flag_random=0):
        """
        Initialize the CityModel.

        Args:
            width (int): Width of the grid.
            height (int): Height of the grid.
            num_agents (int): Total number of agents (households).
            subsidy (int): Whether subsidy is applied (1) or not (0).
            subsidy_timestep (int): Timestep at which subsidy begins.
            max_steps (int): Maximum number of simulation steps.
            beta1-7 (float): Parameters controlling behavioral/social influence effects.
        """

        self.num_agents = num_agents
        self.grid = Grid(width, height)
        self.schedule = RandomActivation(self)
        self.subsidy = subsidy  # Subsidy flag, 0 if government does not provide subsidy, 1 if it does
        self.running = True
        self.subsidy_timestep = subsidy_timestep # Timestep when subsidy is applied
        self.max_steps = max_steps

        self.beta1 = beta1
        self.beta2 = beta2
        self.beta3 = beta3
        self.beta4 = beta4
        self.beta5 = beta5
        self.beta6 = beta6
        self.beta7 = beta7

        # Number of households per income level and apartment type
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
            "Total Solar Panels": lambda m: sum(a.solar_panels for a in m.schedule.agents),
            "Global Adoption Rate": compute_global_adoption,
            "Clustering Score": compute_clustering_score,
            "Moran's I": compute_morans_I,
            "Between-Class Gini": gini_between_income_classes
            }
        )
     
        if flag_random == 0:
            # 11 neighborhoods with different income distributions and spatial geometry
            neighborhoods = [
                {"x_range": (0, 84), "y_range": (0, 64), "income_dist": [1, 2, 3], "weights": [0.85, 0.15, 0.0]},     
                {"x_range": (84, 120), "y_range": (66, 120), "income_dist": [1, 2, 3], "weights": [0.6, 0.39, 0.01]},     
                {"x_range": (0, 39), "y_range": (38, 64), "income_dist": [1, 2, 3], "weights": [0.75, 0.25, 0.0]},    
                {"x_range": (39, 51), "y_range": (46, 64), "income_dist": [2, 3, 1], "weights": [0.7, 0.2, 0.1]},    
                {"x_range": (39, 51), "y_range": (38, 46), "income_dist": [2, 1, 3], "weights": [0.7, 0.2, 0.1]},   
                {"x_range": (51, 57), "y_range": (38, 42), "income_dist": [2, 3, 1], "weights": [0.7, 0.2, 0.1]},   
                {"x_range": (51, 94), "y_range": (42, 64), "income_dist": [3, 2, 1], "weights": [0.7, 0.3, 0.0]},    
                {"x_range": (94, 120), "y_range": (42, 66), "income_dist": [2, 1, 3], "weights": [0.7, 0.1, 0.2]},    
                {"x_range": (57, 120), "y_range": (0, 42), "income_dist": [3, 2, 1], "weights": [0.7, 0.3, 0.0]},    
                {"x_range": (0, 84), "y_range": (64, 66), "income_dist": [3, 2, 1], "weights": [0.7, 0.3, 0.0]}, 
                {"x_range": (0, 84), "y_range": (64, 120), "income_dist": [2, 3, 1], "weights": [0.7, 0.2, 0.1]} 
            ]


            for n in neighborhoods:
                x_min, x_max = n["x_range"]
                y_min, y_max = n["y_range"]
                n["area"] = (x_max - x_min) * (y_max - y_min)

            total_area = sum(n["area"] for n in neighborhoods)
            area_weights = [n["area"] / total_area for n in neighborhoods]


            next_id = 0  # track agent IDs

            while next_id < self.num_agents:
                # Select neighborhood based on area weight
                neighborhood = random.choices(neighborhoods, weights=area_weights, k=1)[0]
                x_min, x_max = neighborhood["x_range"]
                y_min, y_max = neighborhood["y_range"]

                # Random position within the selected neighborhood
                x = self.random.randrange(x_min, x_max)
                y = self.random.randrange(y_min, y_max)

                agent = Household(next_id, self)
                # Set income level based on neighborhood distribution
                income = random.choices(neighborhood["income_dist"], weights=neighborhood["weights"])[0]
                agent.set_income(income)
                # Random environmental & behavioral traits
                agent.set_environmental_consciousness(random.uniform(0, 1))
                agent.set_stubborness_factor(random.uniform(0, 1))

                # Set education and housing type based on income
                if income == 1:
                    education = random.choices([1, 2, 3], weights=[0.1, 0.6, 0.3])[0]
                    agent_type = random.choices([1, 2], weights=[0.2, 0.8])[0]
                elif income == 2:
                    education = random.choices([1, 2, 3], weights=[0.05, 0.2, 0.75])[0]
                    agent_type = random.choices([1, 2], weights=[0.5, 0.5])[0]
                else:
                    education = random.choices([1, 2, 3], weights=[0.01, 0.1, 0.89])[0]
                    agent_type = random.choices([1, 2], weights=[0.8, 0.2])[0]

                agent.set_education_level(education)
                agent.set_subsidy(0)
                placed = False
                max_tries = 100
                for _ in range(max_tries):
                    x = self.random.randrange(x_min, x_max)
                    y = self.random.randrange(y_min, y_max)
                    contents = self.grid.get_cell_list_contents((x, y))

                    if agent_type == 1: # House: cell must be empty
                        if not contents:
                            placed = True
                            break
                    elif agent_type == 2: # Apartment: can share cell with other apartments
                        if all(a.type == 2 for a in contents):
                            placed = True
                            break
                if not placed:
                    continue  

                agent.set_type(agent_type)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
                self.incomes[income]["count"] += 1
                if agent_type == 1:
                    self.incomes[income]["houses"] += 1
                else:
                    self.incomes[income]["apartments"] += 1
                next_id += 1
            
        else:
            # Randomly place agents across the grid without neighborhood structure
            next_id = 0
            while next_id < self.num_agents:  
                agent = Household(next_id, self)
                # Randomly assign income level
                income = self.random.choice([1, 2, 3])
                agent.set_income(income)
                # Random environmental & behavioral traits
                agent.set_environmental_consciousness(self.random.uniform(0, 1))
                agent.set_stubborness_factor(self.random.uniform(0, 1))

                # Set education and housing type 
                education = self.random.choices([1, 2, 3])[0]
                agent_type = self.random.choices([1, 2])[0]
                
                agent.set_type(agent_type)
                agent.set_education_level(education)
                agent.set_subsidy(0)
                
                placed = False
                max_tries = 100
                for _ in range(max_tries):
                    x = self.random.randrange(self.grid.width)
                    y = self.random.randrange(self.grid.height)
                    contents = self.grid.get_cell_list_contents((x,y))

                    if agent_type == 1: # House: cell must be empty
                        if not contents:
                            placed = True
                            break
                    elif agent_type == 2: # Apartment: can share cell with other apartments
                        if all(a.type == 2 for a in contents):
                            placed = True
                            break
                if not placed:
                    continue
                
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
                self.incomes[income]["count"] += 1
                if agent_type == 1:
                    self.incomes[income]["houses"] += 1
                else:
                    self.incomes[income]["apartments"] += 1
                next_id += 1
            
        self.datacollector.collect(self)
        
    

    def step(self):
        """AAdvance the model by one step. If the step is the subsidy timestep and
        subsidy is enabled, apply subsidy logic. Then activate each agent."""

        # Stop if max steps reached
        if self.schedule.time >= self.max_steps:
            self.running = False
            print("Model has reached max steps, stopping.") 

        # Apply subsidies at configured timestep
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
                agents[key].step(self.grid, self, self.beta1, self.beta2, self.beta3, self.beta4, self.beta5, self.beta6, self.beta7)

        self.datacollector.collect(self)
        self.schedule.time += 1
        
    
    def run_model(self, steps=100):
        """Run the model for a specified number of steps."""
        for i in range(steps):
            self.step()
            #print(f"Step {i + 1}/{steps} completed.")
            if not self.running:
                break


        

