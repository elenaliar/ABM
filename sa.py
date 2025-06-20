from mesa.batchrunner import BatchRunner
import SALib

from SALib.sample import saltelli
from grid import Grid
from city import CityModel
# Import necessary libraries for sensitivity analysis
from mesa.batchrunner import FixedBatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import random
# Set random seed for reproducibility
random.seed(42)

# Define problem for SALib
problem = {
    'num_vars': 6,
    'names': [
        'income',                     # Average income group: 1 (low), 2 (mid), 3 (high)
        'environmental_consciousness',# Mean environmental consciousness
        'stubbornness_factor',        # Mean stubbornness
        'education_level',            # Average education level: 1 (low), 2 (mid), 3 (high)
        'subsidy',                    # Model-wide subsidy
        'type'                        # Housing type: 1 (house), 2 (apartment)
    ],
    'bounds': [
        [1, 3],      # income group
        [0, 1],      # environmental_consciousness
        [0, 1],      # stubbornness
        [1, 3],      # education level
        [0, 1],      # subsidy
        [1, 2]       # housing type
    ]
}

replicates = 16
max_steps = 150
distinct_samples = 64 # or 128

# Generate Sobol samples
param_values = saltelli.sample(problem, distinct_samples, calc_second_order=True)

# Run model function
def run_model(params, run_id=0):
    random.seed(run_id)  # Ensure reproducibility for each run
    np.random.seed(run_id)
    income_raw, env_mean, stub_mean, edu_raw, subsidy_raw, type_raw = params

    # Convert categorical values to integers
    income = int(round(income_raw))
    edu_level = int(round(edu_raw))
    housing_type = int(round(type_raw))
    subsidy = int(round(subsidy_raw))

    N = 10000
    model = CityModel(num_agents=N, width=120, height=120, subsidy=subsidy, seed=run_id)

    agents = model.schedule.agents
    random.shuffle(agents)
    print("about to modify agents")
    for i, agent in enumerate(agents):
        # Set categorical variables
        agent.income = income
        agent.education_level = edu_level   
        agent.type = housing_type

        # Set continuous attributes
        agent.environmental_consciousness = np.clip(np.random.normal(env_mean, 0.1), 0, 1)
        agent.stubborness_factor = np.clip(np.random.normal(stub_mean, 0.1), 0, 1)

        # Initial adoption
        agent.solar_panels = 0
    for _ in range(max_steps):
        model.step()
    df = model.datacollector.get_model_vars_dataframe().iloc[-1]
    return df.tolist()

# Run all samples with replicates
Y = []
for i, p in enumerate(param_values):
    for r in range(replicates):
        print(f"Running sample {i + 1}/{len(param_values)} with parameters: {p}")
        run_id = i * replicates + r  # Unique run ID for each replicate
        result = run_model(p, run_id=run_id)
        Y.append(result)

Y = np.array(Y)

output_labels = [
    "Low Income Solar House",
    "Low Income Solar Apartment",
    "Mid Income Solar House",
    "Mid Income Solar Apartment",
    "High Income Solar House",
    "High Income Solar Apartment"
]

# Run Sobol analysis per output variable
sobol_results = {}
for i, label in enumerate(output_labels):
    Si = sobol.analyze(problem, Y[:, i], calc_second_order=True)
    sobol_results[label] = Si

# Optional: show first-order sensitivity for each output
for label in output_labels:
    print(f"\nSobol Indices for {label}:")
    print("S1:", sobol_results[label]['S1'])
    print("S2:", sobol_results[label]['S2'])
    print("ST:", sobol_results[label]['ST'])

# Save results to CSV
results_df = pd.DataFrame(Y, columns=output_labels)
results_df.to_csv("sensitivity_analysis_results.csv", index=False)
# Plotting Sobol indices
plt.figure(figsize=(12, 8)) 
for i, label in enumerate(output_labels):
    Si = sobol_results[label]
    plt.bar(np.arange(len(Si['S1'])), Si['S1'], label=label)
plt.xticks(np.arange(len(problem['names'])), problem['names'], rotation=45)
plt.ylabel('Sobol First-Order Indices')
plt.title('Sobol First-Order Sensitivity Indices')
plt.legend()
plt.tight_layout()
plt.savefig("sobol_first_order_indices.png")
plt.show()

#plot second order
plt.figure(figsize=(12, 8))
for i, label in enumerate(output_labels):
    Si = sobol_results[label]
    plt.bar(np.arange(len(Si['S2'])), Si['S2'], label=label)
plt.xticks(np.arange(len(problem['names'])), problem['names'], rotation=45)
plt.ylabel('Sobol Second-Order Indices')
plt.title('Sobol Second-Order Sensitivity Indices')
plt.legend()
plt.tight_layout()
plt.savefig("sobol_second_order_indices.png")


# Plotting Total Sobol indices
plt.figure(figsize=(12, 8))
for i, label in enumerate(output_labels):
    Si = sobol_results[label]
    plt.bar(np.arange(len(Si['ST'])), Si['ST'], label=label)        
plt.xticks(np.arange(len(problem['names'])), problem['names'], rotation=45)
plt.ylabel('Sobol Total Indices')
plt.title('Sobol Total Sensitivity Indices')
plt.legend()
plt.tight_layout()
plt.savefig("sobol_total_indices.png")
plt.show()