import numpy as np
from libpysal.weights import lat2W
from esda.moran import Moran


def compute_global_adoption(model):
    """Calculate the global adoption rate of solar panels in the model."""
    adopters = sum(1 for a in model.schedule.agents if a.solar_panels == 1)
    return adopters / model.num_agents


def compute_clustering_score(model):
    """Average fraction of Moore neighbors of adopters that are also adopters."""
    cluster_scores = []
    for agent in model.schedule.agents:
        neighbors = []
        # Separate between apartments and houses
        if agent.type == 2:  
            if agent.solar_panels == 1:
                neighbors = model.grid.get_neighbors(agent.pos, include_center=True)
        else:
            if agent.solar_panels == 1:
                neighbors = model.grid.get_neighbors(agent.pos, include_center=False)
        if neighbors:
            adopter_neighbors = sum(1 for n in neighbors if n.solar_panels == 1)
            cluster_scores.append(adopter_neighbors / len(neighbors))
            
    return sum(cluster_scores) / len(cluster_scores) if cluster_scores else 0


def compute_morans_I(model):
    """Calculate Moran's I for solar panel adoption across the grid."""
    grid_w, grid_h = model.grid.width, model.grid.height
    grid_array = np.zeros((grid_w, grid_h))

    for agent in model.schedule.agents:
        x, y = agent.pos
        grid_array[x, y] = 1 if agent.solar_panels == 1 else 0

    flat = grid_array.flatten()
    w = lat2W(grid_w, grid_h)  # spatial weight matrix
    moran = Moran(flat, w)
    return moran.I

def gini_coefficient(values):
    """Calculate the Gini coefficient from a list or array of values."""
    sorted_vals = np.sort(np.array(values))
    n = len(sorted_vals)
    if n == 0:
        return 0
    cumvals = np.cumsum(sorted_vals)
    return (n + 1 - 2 * np.sum(cumvals) / cumvals[-1]) / n if cumvals[-1] != 0 else 0

def gini_between_income_classes(model):
    """
    Compute Gini coefficient of solar panel adoption fractions across income classes.
    This measures how equally different income classes are adopting solar panels,
    adjusted for the number of agents in each class.
    """
    income_levels = [1, 2, 3]
    adoption_fractions = []

    for income in income_levels:
        income_agents = [a for a in model.schedule.agents if a.income == income]
        n = len(income_agents)
        if n == 0:
            adoption_fractions.append(0.0)
        else:
            adopted = sum(a.solar_panels for a in income_agents)
            fraction = adopted / n
            adoption_fractions.append(fraction)

    return gini_coefficient(adoption_fractions)
