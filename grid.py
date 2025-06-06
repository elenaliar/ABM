#create the grid for our abm project, using mesa and multigrid
from mesa.space import MultiGrid
class Grid(MultiGrid):
    """A grid for the agent-based model, extending Mesa's MultiGrid."""
    
    def __init__(self, width, height):
        """Initialize the grid with given width and height."""
        super().__init__(width, height, torus=False)
        self.width = width
        self.height = height



    def get_neighbors_apt(self, pos, include_center=True):
        """Get neighbors of a given position moore neighborhood."""
        return super().get_neighbors(pos, include_center=include_center, moore=True)
    
    def get_neighbors_house(self, pos, include_center=False):
        """Get neighbors of a given position moore neighborhood."""
        return super().get_neighbors(pos, include_center=include_center, moore=True)
    
