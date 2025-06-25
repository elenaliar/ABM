from mesa.batchrunner import BatchRunner
from SALib.sample import saltelli
from SALib.analyze import sobol
import pandas as pd
from city import CityModel
from IPython.display import clear_output
from visualize_funcs import plot_index, plot_second_order_heatmap


# # Define the Sobol problem with 7 parameters, each ranging from 0 to 1
problem = {
    'num_vars': 7,
    'names': [
        'beta1',                  # 0–1
        'beta2',                  # 0–1
        'beta3',                  # 0–1
        'beta4',                  # 0–1
        'beta5',                  # 0–1
        'beta6',                  # 0–1
        'beta7',                  # 0–1
    ],
    'bounds': [
        [0, 1],      # beta1
        [0, 1],      # beta2
        [0, 1],      # beta3
        [0, 1],      # beta4
        [0, 1],      # beta5
        [0, 1],      # beta6
        [0, 1]       # beta7
    ]
}

distinct_samples = 64
replicates = 5
steps = 300

# Generate parameter samples using Saltelli's method for Sobol analysis
param_values = saltelli.sample(problem, distinct_samples, calc_second_order=True)

# Fixed parameters for the CityModel simulation
fixed_params = {
    "width": 120,
    "height": 120,
    "num_agents": 10000,
    "subsidy": 1,
    "subsidy_timestep": 0,
    "max_steps": 300,
}

# Define model reporters to track various solar panel counts by income and housing type
reporters = {
    "Low Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 1 and a.solar_panels and a.type == 1),
    "Low Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 1 and a.solar_panels and a.type == 2),
    "Mid Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 2 and a.solar_panels and a.type == 1),
    "Mid Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 2 and a.solar_panels and a.type == 2),
    "High Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 3 and a.solar_panels and a.type == 1),
    "High Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 3 and a.solar_panels and a.type == 2),
    "Total Solar Panels": lambda m: sum(a.solar_panels for a in m.schedule.agents),
}

# Initialize the batch runner with fixed and variable parameters and reporters
batch = BatchRunner(
    CityModel,
    fixed_parameters=fixed_params,
    variable_parameters={name: [] for name in problem['names']},
    max_steps=steps,
    model_reporters=reporters,
    display_progress=True,
)

results = []
count = 0
total = len(param_values) * replicates

# Run the simulation for each replicate and parameter set
for i in range(replicates):
    print(f"Running replicate {i + 1}/{replicates}...")
    for params in param_values:
        print(f"Parameters: {params}")
        p = list(params)

        variable_dict = dict(zip(problem['names'], p))

        batch.run_iteration(variable_dict, tuple(p), count)

        result = batch.get_model_vars_dataframe().iloc[count]
        results.append({
            **variable_dict,
            "Low Income Solar House": result["Low Income Solar House"],
            "Low Income Solar Apartment": result["Low Income Solar Apartment"],
            "Mid Income Solar House": result["Mid Income Solar House"],
            "Mid Income Solar Apartment": result["Mid Income Solar Apartment"],
            "High Income Solar House": result["High Income Solar House"],
            "High Income Solar Apartment": result["High Income Solar Apartment"],
            "Total Solar Panels": result["Total Solar Panels"]
        })

        count += 1
        clear_output(wait=True)
        print(f"{(count / total) * 100:.2f}% complete")

# Convert results to a DataFrame and save as CSV
df = pd.DataFrame(results)
df.to_csv("sobol_sensitivity_results.csv", index=False)

# Perform Sobol sensitivity analysis on total solar panels output

Si = sobol.analyze(problem, df["Total Solar Panels"].values, calc_second_order=True)
print("First-order indices:", Si['S1'])
print("Second-order indices:", Si['S2'])
print("Total-order indices:", Si['ST'])

# Plot the sensitivity indices
plot_index(Si, problem['names'], '1', 'First-order Sensitivity')
plot_index(Si, problem['names'], '2', 'Second-order Sensitivity')
plot_index(Si, problem['names'], 'T', 'Total-order Sensitivity')

plot_second_order_heatmap(Si, problem['names'])

