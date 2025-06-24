from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from city import CityModel

# Portrayal function to visualize household agents 
def agent_portrayal(agent):
    if agent is None:
        return

    portrayal = {"Shape": "circle", "Filled": "true", "r": 2}
    
    # Color by income level
    if agent.income == 1:
        color = "red"      # Low income
    elif agent.income == 2:
        color = "orange"   # Mid income
    else:
        color = "green"     # High income

    # Blue for when solar panels are installed
    if agent.solar_panels == 1:
        color = "blue"

    portrayal["Color"] = color
    portrayal["Layer"] = 0
    return portrayal

# Create the CanvasGrid for visualization
grid_width = 120
grid_height = 120
canvas_element = CanvasGrid(agent_portrayal, grid_width, grid_height, 600, 600)

# Chart to show proportion of solar panel adoption over time
chart = ChartModule([
    {"Label": "Solar Adoption", "Color": "blue"}
])

# Define model parameters for the UI
model_params = {
    "width": grid_width,
    "height": grid_height,
    "num_agents": 10000, 
    "subsidy": 1,  # 0 = no subsidy, 1 = subsidy available
    "subsidy_timestep": 0,  # when the subsidy is applied
    "max_steps": 500,  # number of steps to run the model
}

# Create the ModularServer
server = ModularServer(
    CityModel,
    [canvas_element],
    "Solar Panel Adoption Simulation",
    model_params
)

# Launch the server
if __name__ == "__main__":
    server.port = 8521  # Default Mesa port
    server.launch()

