import argparse
import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from city import CityModel
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


"""This script runs the CityModel simulation for solar panel adoption, collects results, and generates visualizations."""

random.seed(42)  # For reproducibility


def parse_arguments():
    """
    Parse command-line arguments for the simulation parameters.

    Returns:
        argparse.Namespace: Parsed arguments including grid dimensions, number of agents,
                            subsidy settings, and simulation steps.
    """
    parser = argparse.ArgumentParser(description="Run solar panel adoption simulation and generate analysis.")
    parser.add_argument('--width', type=int, default=120, help='Grid width')
    parser.add_argument('--height', type=int, default=120, help='Grid height')
    parser.add_argument('--num_agents', type=int, default=10000, help='Number of agents')
    parser.add_argument('--subsidy', type=int, default=1, help='Enable subsidy (1) or not (0)')
    parser.add_argument('--subsidy_timestep', type=int, default=0, help='Time step when subsidy starts')
    parser.add_argument('--num_steps', type=int, default=200, help='Number of steps to simulate')
    # Beta parameters
    parser.add_argument('--beta1', type=float, default=0.35, help='Weight for income')
    parser.add_argument('--beta2', type=float, default=0.05, help='Weight for environmental consciousness')
    parser.add_argument('--beta3', type=float, default=0.5, help='Weight for neighbor solar adoption')
    parser.add_argument('--beta4', type=float, default=0.2, help='Weight for stubbornness')
    parser.add_argument('--beta5', type=float, default=0.3, help='Weight for education')
    parser.add_argument('--beta6', type=float, default=0.3, help='Weight for subsidy presence')
    parser.add_argument('--beta7', type=float, default=0.6, help='Weight for housing type')
    return parser.parse_args()


def run_simulation(args):
    """
    Initialize and run the CityModel simulation based on provided arguments.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        CityModel: The simulated model instance after running for the specified steps.
    """
    random.seed(42)  # For reproducibility

    model = CityModel(
        width=args.width,
        height=args.height,
        num_agents=args.num_agents,
        subsidy=args.subsidy,
        subsidy_timestep=args.subsidy_timestep,
        max_steps=args.num_steps,
        beta1=args.beta1,
        beta2=args.beta2,
        beta3=args.beta3,
        beta4=args.beta4,
        beta5=args.beta5,
        beta6=args.beta6,
        beta7=args.beta7,
    )

    for step in range(args.num_steps):
        model.step()

    return model


def save_results(model):
    """
    Extract model results and save them as a CSV file.

    Args:
        model (CityModel): The simulated CityModel instance.

    Returns:
        pandas.DataFrame: DataFrame containing model variables collected during simulation.
    """
    results = model.datacollector.get_model_vars_dataframe()
    results.to_csv("csv/solar_adoption.csv", index=False)
    print("Simulation complete. Data saved to solar_adoption.csv")
    return results


def print_income_summary(model):
    """
    Print a summary table showing counts of agents by income level and dwelling type.

    Args:
        model (CityModel): The simulated CityModel instance.
    """
    income_df = pd.DataFrame.from_dict({
        "Low Income": model.incomes[1]["count"],
        "Mid Income": model.incomes[2]["count"],
        "High Income": model.incomes[3]["count"]
    }, orient='index', columns=['Count'])

    income_df['Houses'] = [model.incomes[1]["houses"], model.incomes[2]["houses"], model.incomes[3]["houses"]]
    income_df['Apartments'] = [model.incomes[1]["apartments"], model.incomes[2]["apartments"], model.incomes[3]["apartments"]]
    income_df.index = ['Low Income', 'Mid Income', 'High Income']
    print(income_df)


def plot_time_series(results, model):
    """
    Plot the time series of solar panel adoption rates by income group.

    Args:
        results (pandas.DataFrame): DataFrame with model variable time series data.
        model (CityModel): The simulated CityModel instance.
    """
    plt.figure(figsize=(12, 6))
    plt.plot((results["Low Income Solar House"] + results["Low Income Solar Apartment"]) / model.incomes[1]["count"],
             color='red', label='Low Income Solar')
    plt.plot((results["Mid Income Solar House"] + results["Mid Income Solar Apartment"]) / model.incomes[2]["count"],
             color='orange', label='Mid Income Solar')
    plt.plot((results["High Income Solar House"] + results["High Income Solar Apartment"]) / model.incomes[3]["count"],
             color='green', label='High Income Solar')
    plt.title("Solar Panel Adoption Over Time")
    plt.xlabel("Step")
    plt.ylabel("Proportion of Households with Solar Panels")
    plt.legend()
    plt.tight_layout()
    plt.savefig("plots/solar_adoption_timeseries.png")
    plt.show()


def plot_adoption_histogram(results, model):
    """
    Plot a histogram of solar panel adoption rates at the final timestep
    separated by income level and dwelling type.

    Args:
        results (pandas.DataFrame): DataFrame with model variable time series data.
        model (CityModel): The simulated CityModel instance.
    """
    final_step = results.iloc[-1]
    income_labels = ['Low Income', 'Mid Income', 'High Income']
    x = np.arange(len(income_labels))

    solar_house = [final_step["Low Income Solar House"], final_step["Mid Income Solar House"], final_step["High Income Solar House"]]
    solar_apartment = [final_step["Low Income Solar Apartment"], final_step["Mid Income Solar Apartment"], final_step["High Income Solar Apartment"]]

    total_house = [model.incomes[1]["houses"], model.incomes[2]["houses"], model.incomes[3]["houses"]]
    total_apartment = [model.incomes[1]["apartments"], model.incomes[2]["apartments"], model.incomes[3]["apartments"]]

    house_pct = [s / t * 100 if t > 0 else 0 for s, t in zip(solar_house, total_house)]
    apartment_pct = [s / t * 100 if t > 0 else 0 for s, t in zip(solar_apartment, total_apartment)]

    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    bar1 = ax.bar(x - width/2, house_pct, width, label='House', color='skyblue')
    bar2 = ax.bar(x + width/2, apartment_pct, width, label='Apartment', color='salmon')

    ax.set_ylabel('Solar Panel Adoption (%)')
    ax.set_title('Adoption by Income Level and Dwelling Type (Final Step)')
    ax.set_xticks(x)
    ax.set_xticklabels(income_labels)
    ax.legend()

    for bars in [bar1, bar2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.1f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig("plots/adoption_by_income_and_type.png")
    plt.show()


def main():
    """
    Main function to parse arguments, run simulation, save results,
    print income summaries, and generate plots.
    """
    args = parse_arguments()
    model = run_simulation(args)
    results = save_results(model)
    print_income_summary(model)
    plot_time_series(results, model)
    plot_adoption_histogram(results, model)


if __name__ == "__main__":
    main()
