import argparse
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from city import CityModel
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


"""This script launches the Mesa server for the CityModel simulation of solar panel adoption."""

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
        color = "green"    # High income

    # Blue if solar panels installed
    if agent.solar_panels == 1:
        color = "blue"

    portrayal["Color"] = color
    portrayal["Layer"] = 0
    return portrayal

def main():
    parser = argparse.ArgumentParser(description="Launch the Solar Panel ABM Mesa Server.")

    parser.add_argument('--width', type=int, default=120, help='Width of the grid')
    parser.add_argument('--height', type=int, default=120, help='Height of the grid')
    parser.add_argument('--num_agents', type=int, default=10000, help='Number of agents in the model')
    parser.add_argument('--subsidy', type=int, default=1, help='Enable subsidy (1) or not (0)')
    parser.add_argument('--subsidy_timestep', type=int, default=0, help='Timestep at which subsidy is applied')
    parser.add_argument('--max_steps', type=int, default=500, help='Number of steps the model should run')

    # Beta parameters
    parser.add_argument('--beta1', type=float, default=0.35, help='Weight for income')
    parser.add_argument('--beta2', type=float, default=0.05, help='Weight for environmental consciousness')
    parser.add_argument('--beta3', type=float, default=0.5, help='Weight for neighbor solar adoption')
    parser.add_argument('--beta4', type=float, default=0.2, help='Weight for stubbornness')
    parser.add_argument('--beta5', type=float, default=0.3, help='Weight for education')
    parser.add_argument('--beta6', type=float, default=0.3, help='Weight for subsidy presence')
    parser.add_argument('--beta7', type=float, default=0.6, help='Weight for housing type')

    args = parser.parse_args()

    # Setup canvas and chart modules
    canvas_element = CanvasGrid(agent_portrayal, args.width, args.height, 600, 600)

    

    # Dynamic model params
    model_params = {
        "width": args.width,
        "height": args.height,
        "num_agents": args.num_agents,
        "subsidy": args.subsidy,
        "subsidy_timestep": args.subsidy_timestep,
        "max_steps": args.max_steps,
        "beta1": args.beta1,
        "beta2": args.beta2,
        "beta3": args.beta3,
        "beta4": args.beta4,
        "beta5": args.beta5,
        "beta6": args.beta6,
        "beta7": args.beta7,
    }

    server = ModularServer(
        CityModel,
        [canvas_element],
        "Solar Panel Adoption Simulation",
        model_params
    )

    server.port = 8521  # Default Mesa port
    server.launch()

if __name__ == "__main__":
    main()
