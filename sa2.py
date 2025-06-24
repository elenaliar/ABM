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
    'num_vars': 6,
    'names': [
        'income',                # 1–3 categorical
        'env_consciousness',     # 0–1
        'stubbornness',          # 0–1
        'education',             # 1–3 categorical
        'household_type',                  # 1–2 categorical
        'subsidy_eligibility'    # 0–1 binary
    ],
    'bounds': [
        [1, 3],      # income
        [0, 1],      # environmental consciousness
        [0, 1],      # stubbornness
        [1, 3],      # education
        [1, 2],      # household type
        [0, 1]       # subsidy eligibility
    ]
}

# ---- Sampling ----
distinct_samples = 8
replicates = 2
steps = 10
param_values = saltelli.sample(problem, distinct_samples, calc_second_order=True)

# ---- Fixed Parameters ----
fixed_params = {
    "width": 120,
    "height": 120,
    "num_agents": 100,
    "subsidy": 1,
    "subsidy_timestep": 0,
    "max_steps": 100,
    "sa": True  # Enable sensitivity analysis
}

# ---- BatchRunner Setup ----
batch = BatchRunner(
    CityModel,
    fixed_parameters=fixed_params,
    variable_parameters={name: [] for name in problem['names']},
    max_steps=steps,
    model_reporters={"SolarAdoption": lambda m: sum([a.solar_panels for a in m.schedule.agents])},
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

        # Round categorical/binary variables
        p[0] = int(round(p[0]))  # income
        p[3] = int(round(p[3]))  # education
        p[4] = int(round(p[4]))  # type
        p[5] = int(round(p[5]))  # subsidy_eligibility

        variable_dict = dict(zip(problem['names'], p))

        batch.run_iteration(variable_dict, tuple(p), count)

        result = batch.get_model_vars_dataframe().iloc[count]
        results.append({**variable_dict, "SolarAdoption": result["SolarAdoption"]})
        count += 1

        clear_output(wait=True)
        print(f"{(count / total) * 100:.2f}% complete")

# ---- Save Results ----
df = pd.DataFrame(results)
df.to_csv("sobol_sensitivity_results.csv", index=False)

# ---- Sobol Analysis (Optional) ----
Si = sobol.analyze(problem, df["SolarAdoption"].values, calc_second_order=True)
print("First-order indices:", Si['S1'])
print("Second-order indices:", Si['S2'])
print("Total-order indices:", Si['ST'])



def plot_index(s, params, i, title=''):
    """
    Creates a plot for Sobol sensitivity analysis that shows the contributions
    of each parameter to the global sensitivity.

    Args:
        s (dict): dictionary {'S#': dict, 'S#_conf': dict} of dicts that hold
            the values for a set of parameters
        params (list): the parameters taken from s
        i (str): string that indicates what order the sensitivity is.
        title (str): title for the plot
    """

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

for Si_var in Si:
    # First order
    plot_index(Si_var, problem['names'], '1', 'First order sensitivity')
    plt.show()

    # Second order
    plot_index(Si_var, problem['names'], '2', 'Second order sensitivity')
    plt.show()

    # Total order
    plot_index(Si_var, problem['names'], 'T', 'Total order sensitivity')
    plt.show()
