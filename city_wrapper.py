from city import CityModel
import numpy as np
class CityModelWrapper(CityModel):
    def __init__(self, income, environmental_consciousness, stubbornness_factor,
                 education_level, subsidy, housing_type,
                 width=120, height=120, num_agents=10000, max_steps=150, seed=None):

        # Init base model with fixed arguments
        super().__init__(width, height, num_agents, subsidy=subsidy, seed=seed)

        # Inject param values into agents
        for agent in self.schedule.agents:
            agent.income = int(round(income))
            agent.education_level = int(round(education_level))  # Normalize to [0, 1]
            agent.type = int(round(housing_type))
            agent.environmental_consciousness = np.clip(
                np.random.normal(environmental_consciousness, 0.1), 0, 1)
            agent.stubborness_factor = np.clip(
                np.random.normal(stubbornness_factor, 0.1), 0, 1)
