import argparse
from city import CityModel
import matplotlib.pyplot as plt
import warnings
from scipy.stats import norm
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore", category=RuntimeWarning)


"""This script runs the Citymodel simulation with and without subsidy, 
   collects results, and generates visualizations comparing the emergent phenomena of the two scenarios."""

def run_model_comparison(args):
    """    Run the CityModel simulation with and without subsidies, collecting results for comparison."""
    # Initialize models with and without subsidies
    model_with_subsidy = CityModel(
        width=args.width,
        height=args.height,
        num_agents=args.num_agents,
        subsidy=1,
        subsidy_timestep=args.subsidy_timestep,
        max_steps=args.max_steps,
        beta1=args.beta1,
        beta2=args.beta2,
        beta3=args.beta3,
        beta4=args.beta4,
        beta5=args.beta5,
        beta6=args.beta6,
        beta7=args.beta7,
        flag_random=args.flag_random
    )


    model_without_subsidy = CityModel(
        width=args.width,
        height=args.height,
        num_agents=args.num_agents,
        subsidy=0,
        subsidy_timestep=args.subsidy_timestep,
        max_steps=args.max_steps,
        beta1=args.beta1,
        beta2=args.beta2,
        beta3=args.beta3,
        beta4=args.beta4,
        beta5=args.beta5,
        beta6=args.beta6,
        beta7=args.beta7,
        flag_random=args.flag_random
    )

    # Run both models
    model_with_subsidy.run_model(steps=args.max_steps)
    print("Model with subsidy completed.")
    model_without_subsidy.run_model(steps=args.max_steps)
    print("Model without subsidy completed.")

    # Create DataFrames
    df_with = model_with_subsidy.datacollector.get_model_vars_dataframe()
    df_without = model_without_subsidy.datacollector.get_model_vars_dataframe()

    return df_with, df_without

def run_multiple_times(args):
    """Run the model comparison multiple times to collect replicates."""
    z = norm.ppf(0.975)  # for 95% confidence interval
    n_runs = 5          # number of replicates

    # Collect all replicates
    dfs_with = []
    dfs_without = []

    for i in range(n_runs):
        print(f"Running replicate {i+1}/{n_runs}")
        df_with, df_without = run_model_comparison(args)
        
        dfs_with.append(df_with.reset_index(drop=True))
        dfs_without.append(df_without.reset_index(drop=True))
    return dfs_with, dfs_without, z, n_runs

def compute_mean_ci(dfs, z, n_runs):
    """Compute mean and confidence intervals for the collected DataFrames."""
    combined = pd.concat(dfs, axis=1)
    # Group columns: each metric appears n_runs times, so we average every n-th column set
    means = pd.concat([combined.iloc[:, i::len(dfs[0].columns)].mean(axis=1) for i in range(len(dfs[0].columns))], axis=1)
    stds = pd.concat([combined.iloc[:, i::len(dfs[0].columns)].std(axis=1) for i in range(len(dfs[0].columns))], axis=1)
    cis = z * stds / np.sqrt(n_runs)
    means.columns = dfs[0].columns
    cis.columns = dfs[0].columns
    return means, cis

def plot_results(mean_with, mean_without, ci_with, ci_without):
    """Plot the results comparing the two scenarios."""
    plt.figure(figsize=(8, 6))
    plt.plot(mean_with['Global Adoption Rate'], label='Global Adoption Rate With Subsidy', color='olivedrab')
    plt.plot(mean_without['Global Adoption Rate'], label='Global Adoption Rate Without Subsidy', color='yellowgreen')
    plt.plot(mean_with["Moran's I"], label="Moran's I With Subsidy", color='firebrick')
    plt.plot(mean_without["Moran's I"], label="Moran's I Without Subsidy", color='tomato')

    # CI bands
    plt.fill_between(mean_with.index,
                    mean_with['Global Adoption Rate'] - ci_with['Global Adoption Rate'],
                    mean_with['Global Adoption Rate'] + ci_with['Global Adoption Rate'],
                    color='olivedrab', alpha=0.2)

    plt.fill_between(mean_without.index,
                    mean_without['Global Adoption Rate'] - ci_without['Global Adoption Rate'],
                    mean_without['Global Adoption Rate'] + ci_without['Global Adoption Rate'],
                    color='yellowgreen', alpha=0.2)

    plt.fill_between(mean_with.index,
                    mean_with["Moran's I"] - ci_with["Moran's I"],
                    mean_with["Moran's I"] + ci_with["Moran's I"],
                    color='firebrick', alpha=0.2)

    plt.fill_between(mean_without.index,
                    mean_without["Moran's I"] - ci_without["Moran's I"],
                    mean_without["Moran's I"] + ci_without["Moran's I"],
                    color='tomato', alpha=0.2)

    plt.title("Emergence Metrics: With vs Without Subsidy")
    plt.xlabel("Time Steps")
    plt.ylabel("Metric Value")
    plt.legend()
    plt.savefig("plots/emergence_metrics_comparison.png")
    plt.show()

    plt.figure(figsize=(8, 6))

    plt.plot(mean_with['Between-Class Gini'], label='Gini Coefficient With Subsidy', color='royalblue')
    plt.plot(mean_without['Between-Class Gini'], label='Gini Coefficient Without Subsidy', color='cornflowerblue')

    plt.fill_between(mean_with.index,
                    mean_with['Between-Class Gini'] - ci_with['Between-Class Gini'],
                    mean_with['Between-Class Gini'] + ci_with['Between-Class Gini'],
                    color='royalblue', alpha=0.2)

    plt.fill_between(mean_without.index,
                    mean_without['Between-Class Gini'] - ci_without['Between-Class Gini'],
                    mean_without['Between-Class Gini'] + ci_without['Between-Class Gini'],
                    color='cornflowerblue', alpha=0.2)

    plt.title("Gini Coefficient: With vs Without Subsidy")
    plt.xlabel("Time Steps")
    plt.ylabel("Gini Coefficient")
    plt.legend()
    plt.savefig("plots/gini_coefficient_comparison.png")
    plt.show()

     
def main():
    parser = argparse.ArgumentParser(description="Run the solar panel adoption ABM with customizable parameters.")
    
    parser.add_argument('--width', type=int, default=120, help='Width of the grid')
    parser.add_argument('--height', type=int, default=120, help='Height of the grid')
    parser.add_argument('--num_agents', type=int, default=10000, help='Number of agents in the model')
    parser.add_argument('--subsidy_timestep', type=int, default=0, help='Timestep at which subsidy starts')
    parser.add_argument('--max_steps', type=int, default=1000, help='Number of simulation steps')
    parser.add_argument('--flag_random', type=int, default=0, help='Randomize grid generation(1) or not (0)')

    
    # Beta parameters
    parser.add_argument('--beta1', type=float, default=0.35, help='Weight for income')
    parser.add_argument('--beta2', type=float, default=0.05, help='Weight for environmental consciousness')
    parser.add_argument('--beta3', type=float, default=0.5, help='Weight for neighbor solar adoption')
    parser.add_argument('--beta4', type=float, default=0.2, help='Weight for stubbornness')
    parser.add_argument('--beta5', type=float, default=0.3, help='Weight for education')
    parser.add_argument('--beta6', type=float, default=0.3, help='Weight for subsidy presence')
    parser.add_argument('--beta7', type=float, default=0.6, help='Weight for housing type')

    args = parser.parse_args()
    dfs_with, dfs_without, z, n_runs = run_multiple_times(args)
    means_with, ci_with = compute_mean_ci(dfs_with, z, n_runs)
    means_without, ci_without = compute_mean_ci(dfs_without, z, n_runs)
    plot_results(means_with, means_without, ci_with, ci_without)

if __name__ == "__main__":
    main()
