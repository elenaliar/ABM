from city import CityModel
import matplotlib.pyplot as plt

def plot_grid(model):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, model.grid.width)
    ax.set_ylim(0, model.grid.height)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])

    for agent in model.schedule.agents:
        x, y = agent.pos

        if agent.income == 1:
            color = 'yellow'
        elif agent.income == 2:
            color = 'orange'
        else:
            color = 'red'

        if agent.type == 1:  # house
            shape = plt.Circle((x + 0.5, y + 0.5), 0.4, color=color)
        else:  # apartment
            shape = plt.Rectangle((x + 0.1, y + 0.1), 0.8, 0.8, color=color)

        ax.add_patch(shape)

    plt.gca().invert_yaxis()
    plt.title("Household Grid Snapshot")
    plt.show()


if __name__ == "__main__":
    model = CityModel(width=120, height=120, num_agents=10000)
    plot_grid(model)