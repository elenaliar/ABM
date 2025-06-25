import argparse
from city import CityModel
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


"""This script runs the Citymodel simulation with and without subsidy, 
   collects results, and generates visualizations comparing the emergent phenomena of the two scenarios."""

def run_model_comparison(args):
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
    )

    # Run both models
    model_with_subsidy.run_model(steps=args.max_steps)
    model_without_subsidy.run_model(steps=args.max_steps)

    # Create DataFrames
    df_with = model_with_subsidy.datacollector.get_model_vars_dataframe()
    df_without = model_without_subsidy.datacollector.get_model_vars_dataframe()

    # Save CSVs
    df_with.to_csv("csv/results_with_subsidy.csv", index=False)
    df_without.to_csv("csv/results_without_subsidy.csv", index=False)

    # Plot emergence metrics
    plt.figure(figsize=(8, 6))
    plt.plot(df_with['Global Adoption Rate'], label='Global Adoption Rate With', color='olivedrab')
    plt.plot(df_without['Global Adoption Rate'], label='Global Adoption Rate Without', color='yellowgreen')
    plt.plot(df_with["Moran's I"], label='Moran\'s I With', color='firebrick')
    plt.plot(df_without["Moran's I"], label='Moran\'s I Without', color='tomato')
    plt.title("Emergence Metrics Comparison: With vs Without Subsidy")
    plt.xlabel("Time Steps")
    plt.ylabel("Metric Value")
    plt.legend()
    plt.savefig("plots/emergence_metrics_comparison.png")
    plt.show()

    plt.figure(figsize=(8, 6))
    plt.plot(df_with['Between-Class Gini'], label='Gini Coefficient With', color='royalblue')
    plt.plot(df_without['Between-Class Gini'], label='Gini Coefficient Without', color='cornflowerblue')
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
    
    # Beta parameters
    parser.add_argument('--beta1', type=float, default=0.35, help='Weight for income')
    parser.add_argument('--beta2', type=float, default=0.05, help='Weight for environmental consciousness')
    parser.add_argument('--beta3', type=float, default=0.5, help='Weight for neighbor solar adoption')
    parser.add_argument('--beta4', type=float, default=0.2, help='Weight for stubbornness')
    parser.add_argument('--beta5', type=float, default=0.3, help='Weight for education')
    parser.add_argument('--beta6', type=float, default=0.3, help='Weight for subsidy presence')
    parser.add_argument('--beta7', type=float, default=0.6, help='Weight for housing type')

    args = parser.parse_args()
    run_model_comparison(args)

if __name__ == "__main__":
    main()
