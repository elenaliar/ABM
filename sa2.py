from mesa.batchrunner import BatchRunner
from SALib.sample import saltelli
from SALib.analyze import sobol
import pandas as pd
import numpy as np
from city import CityModel
from IPython.display import clear_output
import matplotlib.pyplot as plt
from itertools import combinations

# ---- Sobol Problem Setup ----
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

# ---- Sampling ----
distinct_samples = 128
replicates = 5
steps = 100
param_values = saltelli.sample(problem, distinct_samples, calc_second_order=True)

# ---- Fixed Parameters ----
fixed_params = {
    "width": 120,
    "height": 120,
    "num_agents": 10000,
    "subsidy": 1,
    "subsidy_timestep": 0,
    "max_steps": 100,
}

# ---- BatchRunner Setup ----
batch = BatchRunner(
    CityModel,
    fixed_parameters=fixed_params,
    variable_parameters={name: [] for name in problem['names']},
    max_steps=steps,
    model_reporters={
                "Low Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 1 and a.solar_panels == 1 and a.type == 1),
                "Low Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 1 and a.solar_panels == 1 and a.type == 2),
                "Mid Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 2 and a.solar_panels == 1 and a.type == 1),
                "Mid Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 2 and a.solar_panels == 1 and a.type == 2),
                "High Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 3 and a.solar_panels == 1 and a.type == 1),
                "High Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 3 and a.solar_panels == 1 and a.type == 2),
                "Total Solar Panels": lambda m: sum(a.solar_panels for a in m.schedule.agents),
                },
    display_progress=True,
)

# ---- Run Experiments ----
results = []
count = 0
total = len(param_values) * replicates

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

# ---- Save Results ----
df = pd.DataFrame(results)
df.to_csv("sobol_sensitivity_results.csv", index=False)

# ---- Sobol Analysis (Optional) ----
Si = sobol.analyze(problem, df["Total Solar Panels"].values, calc_second_order=True)
print("First-order indices:", Si['S1'])
print("Second-order indices:", Si['S2'])
print("Total-order indices:", Si['ST'])


def plot_index(Si, params, order, title=''):
    """
    Plot Sobol sensitivity indices.

    Args:
        Si (dict): Output from sobol.analyze (contains 'S1', 'S1_conf', 'S2', etc.).
        params (list): Parameter names.
        order (str): '1' for first-order, '2' for second-order, 'T' for total-order.
        title (str): Plot title.
    """
    plt.figure(figsize=(10, 6))
    
    if order == '2':
        # Second-order indices
        p = len(params)
        index_pairs = list(combinations(params, 2))
        indices = Si['S2'].reshape(p, p)[np.triu_indices(p, k=1)]
        errors = Si['S2_conf'].reshape(p, p)[np.triu_indices(p, k=1)]
        labels = [f"{a}, {b}" for a, b in index_pairs]
    elif order == '1':
        indices = Si['S1']
        errors = Si['S1_conf']
        labels = params
    elif order.upper() == 'T':
        indices = Si['ST']
        errors = Si['ST_conf']
        labels = params
    else:
        raise ValueError("Order must be '1', '2', or 'T'.")

    y_pos = np.arange(len(labels))
    plt.barh(y_pos, indices, xerr=errors, align='center', alpha=0.7, capsize=5, color = 'dodgerblue')
    plt.yticks(y_pos, labels)
    plt.xlabel('Sobol Index')
    plt.title(title)
    plt.axvline(0, color='black', linewidth=0.8)
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

plot_index(Si, problem['names'], '1', 'First-order Sensitivity')
plot_index(Si, problem['names'], '2', 'Second-order Sensitivity')
plot_index(Si, problem['names'], 'T', 'Total-order Sensitivity')

