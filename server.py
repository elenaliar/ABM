from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from city import CityModel
from household import Household

def household_portrayal(agent):
    if agent is None:
        return

    portrayal = {
        "Shape": "rect",
        "w": 0.8,
        "h": 0.8,
        "Filled": "true",
        "Layer": 0,
    }


    # Set color based on income and type
    if agent.income == 1:
        portrayal["Color"] = "yellow"
    elif agent.income == 2:
        portrayal["Color"] = "orange"
    else:
        portrayal["Color"] = "red"

    if agent.type == 1:  # House
        portrayal["Shape"] = "circle"
    elif agent.type == 2:  # Apartment
        portrayal["Shape"] = "rect"

    return portrayal

grid = CanvasGrid(household_portrayal, 100, 100, 500, 500)

server = ModularServer(
    CityModel,
    [grid],
    "City Model",
    {"width": 100, "height": 100, "num_agents": 10000}
)