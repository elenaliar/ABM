from city import CityModel
import matplotlib.pyplot as plt
import random
import pandas as pd
import numpy as np


random.seed(42)  # For reproducibility

# Set model parameters
width = 120
height = 120
num_agents = 10000
subsidy = 0
num_steps = 1000  # Run for 100 steps
subsidy_timestep = 0  # Apply subsidy at step 50

# Initialize the model
model = CityModel(width=width, height=height, num_agents=num_agents, subsidy=subsidy, subsidy_timestep=subsidy_timestep, max_steps=num_steps)

# Run the model
for step in range(num_steps):
    model.step()

# Get and save results
results = model.datacollector.get_model_vars_dataframe()
results.to_csv("solar_adoption.csv", index=False)

print("Simulation complete. Data saved to solar_adoption.csv")

# Print dictionary of income levels and their counts and types
income_counts = {
    "Low Income": model.incomes[1]["count"],
    "Mid Income": model.incomes[2]["count"],
    "High Income": model.incomes[3]["count"]
}

# Print dictionary of income levels and their counts and types
income_types = {
    "Low Income Houses": model.incomes[1]["houses"],
    "Low Income Apartments": model.incomes[1]["apartments"],
    "Mid Income Houses": model.incomes[2]["houses"],
    "Mid Income Apartments": model.incomes[2]["apartments"],
    "High Income Houses": model.incomes[3]["houses"],
    "High Income Apartments": model.incomes[3]["apartments"]
}

income_df = pd.DataFrame.from_dict(income_counts, orient='index', columns=['Count'])
income_df['Houses'] = [model.incomes[1]["houses"], model.incomes[2]["houses"], model.incomes[3]["houses"]]
income_df['Apartments'] = [model.incomes[1]["apartments"], model.incomes[2]["apartments"], model.incomes[3]["apartments"]]
income_df.index = ['Low Income', 'Mid Income', 'High Income']
print(income_df)

# Plot results
plt.figure(figsize=(12, 6))
plt.plot((results["Low Income Solar House"] + results["Low Income Solar Apartment"])/model.incomes[1]["count"], color='red', label='Low Income Solar')
plt.plot((results["Mid Income Solar House"] + results["Mid Income Solar Apartment"])/model.incomes[2]["count"], color='orange', label='Mid Income Solar')
plt.plot((results["High Income Solar House"] + results["High Income Solar Apartment"])/model.incomes[3]["count"], color='green', label='High Income Solar')
plt.title("Solar Panel Adoption Over Time")
plt.legend()
plt.xlabel("Step")
plt.ylabel("Proportion of Households with Solar Panels")
plt.show()

# Histogram of solar panel adoption by income level and dwelling type (6 bars: House + Apartment for each income level)

# Get the final timestep data
final_step = results.iloc[-1]

# Define labels and structure
income_labels = ['Low Income', 'Mid Income', 'High Income']
dwelling_labels = ['House', 'Apartment']
x = np.arange(len(income_labels))  # base x-axis positions

# Solar counts at final timestep
solar_house = [
    final_step["Low Income Solar House"],
    final_step["Mid Income Solar House"],
    final_step["High Income Solar House"]
]

solar_apartment = [
    final_step["Low Income Solar Apartment"],
    final_step["Mid Income Solar Apartment"],
    final_step["High Income Solar Apartment"]
]

# Total dwellings per group
total_house = [
    model.incomes[1]["houses"],
    model.incomes[2]["houses"],
    model.incomes[3]["houses"]
]

total_apartment = [
    model.incomes[1]["apartments"],
    model.incomes[2]["apartments"],
    model.incomes[3]["apartments"]
]

# Compute % adoption
house_pct = [s / t * 100 if t > 0 else 0 for s, t in zip(solar_house, total_house)]
apartment_pct = [s / t * 100 if t > 0 else 0 for s, t in zip(solar_apartment, total_apartment)]

# Plotting
width = 0.35  # width of each bar

fig, ax = plt.subplots(figsize=(10, 6))
bar1 = ax.bar(x - width/2, house_pct, width, label='House', color='skyblue')
bar2 = ax.bar(x + width/2, apartment_pct, width, label='Apartment', color='salmon')

# Axis labeling
ax.set_ylabel('Solar Panel Adoption (%)')
ax.set_title('Solar Panel Adoption by Income Level and Dwelling Type (Final Step)')
ax.set_xticks(x)
ax.set_xticklabels(income_labels)
ax.legend()

# Add percentage labels on top of each bar
for bars in [bar1, bar2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')

plt.tight_layout()
plt.show()
