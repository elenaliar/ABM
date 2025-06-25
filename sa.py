from mesa.batchrunner import BatchRunner
from SALib.sample import saltelli
from SALib.analyze import sobol
import pandas as pd
from city import CityModel
from IPython.display import clear_output
from visualize_funcs import plot_sensitivity_indices
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


"""This script performs Sobol sensitivity analysis on the CityModel simulation
   to understand how different parameters affect solar panel adoption. First order, second order, and total order indices are calculated.
   It generates parameter samples, runs simulations, collects results, and visualizes the sensitivity indices."""


def define_sobol_problem():
    """
    Define the Sobol sensitivity analysis problem with 7 parameters.

    Returns:
        dict: Dictionary specifying the number of variables, their names, and bounds.
    """
    return {
        'num_vars': 7,
        'names': [
            'beta1', 'beta2', 'beta3', 'beta4', 'beta5', 'beta6', 'beta7'
        ],
        'bounds': [[0, 1]] * 7
    }


def generate_param_samples(problem, distinct_samples):
    """
    Generate parameter samples using Saltelli's sampling method.

    Args:
        problem (dict): Sobol problem definition.
        distinct_samples (int): Number of distinct samples to generate.

    Returns:
        numpy.ndarray: Parameter value samples.
    """
    return saltelli.sample(problem, distinct_samples, calc_second_order=True)


def get_fixed_params():
    """
    Define fixed parameters for the CityModel simulation.

    Returns:
        dict: Fixed model parameters.
    """
    return {
        "width": 120,
        "height": 120,
        "num_agents": 10000,
        "subsidy": 1,
        "subsidy_timestep": 0,
        "max_steps": 1,
    }


def get_model_reporters():
    """
    Define model reporters to collect solar panel adoption statistics by income and housing type.

    Returns:
        dict: Reporter functions mapping reporter names to lambdas extracting values from the model.
    """
    return {
        "Low Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 1 and a.solar_panels and a.type == 1),
        "Low Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 1 and a.solar_panels and a.type == 2),
        "Mid Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 2 and a.solar_panels and a.type == 1),
        "Mid Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 2 and a.solar_panels and a.type == 2),
        "High Income Solar House": lambda m: sum(1 for a in m.schedule.agents if a.income == 3 and a.solar_panels and a.type == 1),
        "High Income Solar Apartment": lambda m: sum(1 for a in m.schedule.agents if a.income == 3 and a.solar_panels and a.type == 2),
        "Total Solar Panels": lambda m: sum(a.solar_panels for a in m.schedule.agents),
    }


def run_batch_simulations(problem, param_values, replicates, fixed_params, reporters, max_steps):
    """
    Run batch simulations for all parameter samples and replicates.

    Args:
        problem (dict): Sobol problem definition.
        param_values (numpy.ndarray): Parameter samples to run.
        replicates (int): Number of replicates per parameter set.
        fixed_params (dict): Fixed parameters for the model.
        reporters (dict): Model reporters for data collection.
        max_steps (int): Number of steps to run each simulation.

    Returns:
        list: List of dictionaries with parameter values and simulation results.
    """
    batch = BatchRunner(
        CityModel,
        fixed_parameters=fixed_params,
        variable_parameters={name: [] for name in problem['names']},
        max_steps=max_steps,
        model_reporters=reporters,
        display_progress=True,
    )

    results = []
    count = 0
    total = len(param_values) * replicates

    for i in range(replicates):
        print(f"Running replicate {i + 1}/{replicates}...")
        for params in param_values:
            print(f"Parameters: {params}")
            variable_dict = dict(zip(problem['names'], params))
            batch.run_iteration(variable_dict, tuple(params), count)
            result = batch.get_model_vars_dataframe().iloc[count]

            results.append({
                **variable_dict,
                "Low Income Solar House": result["Low Income Solar House"],
                "Low Income Solar Apartment": result["Low Income Solar Apartment"],
                "Mid Income Solar House": result["Mid Income Solar House"],
                "Mid Income Solar Apartment": result["Mid Income Solar Apartment"],
                "High Income Solar House": result["High Income Solar House"],
                "High Income Solar Apartment": result["High Income Solar Apartment"],
                "Total Solar Panels": result["Total Solar Panels"],
            })

            count += 1
            clear_output(wait=True)
            print(f"{(count / total) * 100:.2f}% complete")

    return results


def perform_sobol_analysis(problem, df):
    """
    Perform Sobol sensitivity analysis on the total solar panels output.

    Args:
        problem (dict): Sobol problem definition.
        df (pandas.DataFrame): DataFrame containing simulation results.

    Returns:
        dict: Dictionary of Sobol indices.
    """
    Si = sobol.analyze(problem, df["Total Solar Panels"].values, calc_second_order=True)
    print("First-order indices:", Si['S1'])
    print("Second-order indices:", Si['S2'])
    print("Total-order indices:", Si['ST'])
    return Si


def main():
    """
    Main driver function to perform Sobol sensitivity analysis on the CityModel.
    """
    problem = define_sobol_problem()
    distinct_samples = 8
    replicates = 1
    max_steps = 1

    param_values = generate_param_samples(problem, distinct_samples)
    fixed_params = get_fixed_params()
    reporters = get_model_reporters()

    results = run_batch_simulations(problem, param_values, replicates, fixed_params, reporters, max_steps)
    df = pd.DataFrame(results)
    df.to_csv("csv/sobol_sensitivity_results.csv", index=False)

    Si = perform_sobol_analysis(problem, df)
    plot_sensitivity_indices(Si, problem['names'])


if __name__ == "__main__":
    main()
