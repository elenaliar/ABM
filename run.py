from city import CityModel
import matplotlib.pyplot as plt


# Set model parameters
width = 120
height = 120
num_agents = 10000
subsidy = 0
num_steps = 100  # Run for 100 steps

# Initialize the model
model = CityModel(width, height, num_agents, subsidy)

# Run the model
for step in range(num_steps):
    model.step()

# Get and save results
results = model.datacollector.get_model_vars_dataframe()
results.to_csv("solar_adoption.csv", index=False)

print("Simulation complete. Data saved to solar_adoption.csv")

# Plot results
results.plot()
plt.title("Solar Panel Adoption Over Time")
plt.xlabel("Step")
plt.ylabel("Number of Households with Solar Panels")
plt.show()
