from city import CityModel
import matplotlib.pyplot as plt

"""This script run the CityModel with and without subsidies and compares the emergence metrics."""

model_with_subsidy = CityModel(width=120, height=120, num_agents=10000, subsidy=1, subsidy_timestep=0, max_steps=1000, beta1 = 0.35,
        beta2 = 0.05, beta3 = 0.5, beta4 = 0.2, beta5 = 0.3, beta6 = 0.3, beta7 = 0.6)

model_without_subsidy = CityModel(width=120, height=120, num_agents=10000, subsidy=0, subsidy_timestep=0, max_steps=1000, beta1 = 0.35,
        beta2 = 0.05, beta3 = 0.5, beta4 = 0.2, beta5 = 0.3, beta6 = 0.3, beta7 = 0.6)


model_with_subsidy.run_model(steps=1000)
model_without_subsidy.run_model(steps=1000)

# Create DataFrames for analysis
df_with = model_with_subsidy.datacollector.get_model_vars_dataframe()
df_without = model_without_subsidy.datacollector.get_model_vars_dataframe()

# Save results to CSV files
df_with.to_csv("results_with_subsidy.csv", index=False)
df_without.to_csv("results_without_subsidy.csv", index=False)

# Plotting the results 
plt.figure(figsize=(8, 6))
plt.plot(df_with['Global Adoption Rate'], label='Global Adoption Rate With', color='olivedrab')
plt.plot(df_without['Global Adoption Rate'], label='Global Adoption Rate Without', color='yellowgreen')
plt.plot(df_with["Moran's I"], label='Moran\'s I With', color='firebrick')
plt.plot(df_without["Moran's I"], label='Moran\'s I Without', color='tomato')
plt.title("Emergence Metrics Comparison: With vs Without Subsidy")
plt.xlabel("Time Steps")
plt.ylabel("Metric Value")
plt.legend()
plt.savefig("emergence_metrics_comparison.png")
plt.show()

plt.figure(figsize=(8, 6))
plt.plot(df_with['Between-Class Gini'], label='Gini Coefficient With', color='royalblue')
plt.plot(df_without['Between-Class Gini'], label='Gini Coefficient Without', color='cornflowerblue')
plt.title("Gini Coefficient: With vs Without Subsidy")
plt.xlabel("Time Steps")
plt.ylabel("Gini Coefficient")
plt.legend()
plt.savefig("gini_coefficient_comparison.png")
plt.show()





