from mesa.batchrunner import BatchRunner
from SALib.sample import saltelli
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from city import CityModel
import random
from IPython.display import clear_output
from city_wrapper import CityModelWrapper

# Set reproducibility
random.seed(42)
np.random.seed(42)

# Define your problem
problem = {
    'num_vars': 6,
    'names': [
        'income', 'environmental_consciousness', 'stubbornness_factor',
        'education_level', 'subsidy', 'housing_type'
    ],
    'bounds': [
        [1, 3],     # income group
        [0, 1],     # environmental_consciousness
        [0, 1],     # stubbornness
        [1, 3],     # education level
        [0, 1],     # subsidy
        [1, 2]      # housing type
    ]
}

# Config
replicates = 15
max_steps = 150
distinct_samples = 64 # or 128

# Get parameter samples
param_values = saltelli.sample(problem, distinct_samples, calc_second_order=True)

# Define output labels (6 solar adoption categories)
output_labels = [
    "Low Income Solar House", "Low Income Solar Apartment",
    "Mid Income Solar House", "Mid Income Solar Apartment",
    "High Income Solar House", "High Income Solar Apartment"
]

# Model reporter to extract last timestep's adoption counts
def get_outputs(model):
    return model.datacollector.get_model_vars_dataframe().iloc[-1].to_dict()

# Setup batch runner
batch = BatchRunner(
    CityModelWrapper,
    max_steps=max_steps,
    model_reporters={"adoption_data": get_outputs}
)

# Prepare output dataframe
total_runs = replicates * len(param_values)
data = pd.DataFrame(index=range(total_runs), columns=problem['names'] + output_labels + ['Run'])
count = 0

# Run all parameter combinations
for i in range(replicates):
    print(f"Running replicate {i + 1}/{replicates}")
    for vals in param_values:
        vals = list(vals)
        # Round categorical inputs
        vals[0] = int(round(vals[0]))  # income
        vals[3] = int(round(vals[3]))  # education
        vals[5] = int(round(vals[5]))  # housing type
        vals[4] = round(vals[4])       # subsidy as 0/1

        # Construct param dict
        variable_parameters = dict(zip(problem['names'], vals))

        # Run model with params
        batch.run_iteration(variable_parameters, tuple(vals), count)
        iteration_data = batch.get_model_vars_dataframe().iloc[count]["adoption_data"]

        # Fill data row
        data.iloc[count, 0:6] = vals
        for label in output_labels:
            data.at[count, label] = iteration_data.get(label, 0)
        data.at[count, 'Run'] = count

        count += 1
        clear_output(wait=True)
        print(f'{count / total_runs * 100:.2f}% done')

# Save raw data
data.to_csv("citymodel_sobol_raw.csv", index=False)

# Sobol analysis
sobol_results = {}
for label in output_labels:
    Si = sobol.analyze(problem, data[label].astype(float).values, print_to_console=True)
    sobol_results[label] = Si

# Plotting helper
def plot_index(s, params, i, title=''):
    if i == '2':
        p = len(params)
        params = list(combinations(params, 2))
        indices = s['S' + i].reshape((p ** 2))
        indices = indices[~np.isnan(indices)]
        errors = s['S' + i + '_conf'].reshape((p ** 2))
        errors = errors[~np.isnan(errors)]
    else:
        indices = s['S' + i]
        errors = s['S' + i + '_conf']
        plt.figure()

    l = len(indices)
    plt.title(title)
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
    plt.axvline(0, c='k')

# Plot Sobol indices for each output
for label, Si in sobol_results.items():
    print(f"\n--- Sobol Indices for {label} ---")
    plot_index(Si, problem['names'], '1', f'{label}: First-order sensitivity')
    plt.show()
    plot_index(Si, problem['names'], '2', f'{label}: Second-order sensitivity')
    plt.show()
    plot_index(Si, problem['names'], 'T', f'{label}: Total-order sensitivity')
    plt.show()
