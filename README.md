# ABM Project: Household Adoption of Renewable Energies
Group 16: Costanza D'Ercole, Eleni Liarou, Sofia Tété Garcia Ramos Nunes, Zoë Azra Blei

### Overview
This project presents an agent-based model (ABM) that simulates the adoption of solar panels in a heterogeneous urban environment. The model explores how factors like income level, housing type, environmental consciousness, peer influence, and government subsidies interact to shape the dynamics of solar panel adoption in cities.

The simulation is designed to analyze how targeted subsidies can increase solar adoption, especially in low and middle-income neighborhoods, and how social influence mechanisms can lead to clustered adoption patterns.

### Key Features

- Simulates a city with **11 spatially and socio-economically distinct neighborhoods**
- Each household is modeled as an autonomous agent with traits such as:
  - **Income level** (low, middle, high)
  - **Education level**
  - **Housing type** (house or apartment)
  - **Environmental consciousness** (`[0, 1]`)
  - **Stubbornness** (`[0, 1]`)
  - **Solar panel adoption status**
  - **Subsidy status**
- Incorporates **spatial interactions** (e.g., neighborhood effect, apartment co-residency)
- Evaluates the **impact of government subsidies** on adoption rates
- Uses a **Probit model** to simulate adoption decisions based on utility computations
- Includes **sensitivity analysis** to assess the importance of different factors

### Model Structure

The simulation runs on a **2D spatial grid**, where each cell corresponds to a housing unit within one of the 11 neighborhoods. These neighborhoods differ in:

- Population density  
- Distribution of housing types (houses vs apartments)  
- Income and education distributions

Agents are placed based on neighborhood profiles and assigned traits according to probabilistic distributions.

### Neighborhood & Social Influence

- **Houses**: One household per cell, neighbors are the 8 surrounding cells (Moore neighborhood)
- **Apartments**: Multiple households may share a cell; co-located households influence each other

### Subsidy Rules

- **Low-income**: Always receive a subsidy
- **Middle-income**: Receive subsidy with probability 0.4
- **High-income**: Not eligible for subsidies

### Adoption Decision

Each agent calculates a **utility score (U)** based on weighted contributions from:

- Income  
- Environmental consciousness  
- Education  
- Stubbornness  
- Neighbor adoption rate (`f_solar`)  
- Subsidy status  
- Housing type  
- Additive noise (ε ~ N(0, 0.5))

The utility is mapped to an adoption probability using the **standard normal CDF**.  
An agent adopts solar panels if this probability exceeds `0.98`.

## Setup & Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/elenaliar/ABM.git
   cd <your-project-folder>
   ```
 2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
    
### How to Run the Project 
To run different parts of the model, use the following scripts:
1. Simulate and analyze emergent statistics (with and without subsidy)
   ```bash
   python run_emergence.py
   ```
2. Launch interactive Mesa visualization
   ```bash
   python server.py
   ```
3. Run simulations and get solar panel adoption stats (per income level and household type)
   ```bash
   python run.py
   ```
4. Do global sensitivity analysis with Sobol indices
   ```bash
   python sa.py
   ```
### Running the Model with Custom Parameters

You can customize the simulation parameters directly from the command line using the available arguments. For example:

```bash
python <script_filename>.py --width 120 --height 120 --num_agents 10000 --subsidy_timestep 0 --max_steps 500 --beta1 0.4 --beta2 0.1 --beta3 0.55 --beta4 0.25 --beta5 0.35 --beta6 0.4 --beta7 0.7
```

#### Command Line Arguments for Model Parameters

| Argument          | Explanation                                                                                          | Default |
|-------------------|----------------------------------------------------------------------------------------------------|---------|
| `--width`         | Width of the simulation grid. Determines the horizontal size of the environment.                    | 120     |
| `--height`        | Height of the simulation grid. Determines the vertical size of the environment.                     | 120     |
| `--num_agents`    | Number of agents in the model. Defines the population size of the simulation.                       | 10000   |
| `--subsidy`       | Whether or not the governemnt provides subsidies                                                   | 0       |
| `--subsidy_timestep` | The simulation timestep when subsidy is introduced.                                             | 0       |
| `--max_steps`     | Total number of simulation steps to run. Controls the duration of the simulation.                   | 1000    |
| `--flag_random`    | Flag that shows whether or not the grid generated is random(1) or based on the 11 heterogeneous neighborhouds(0)     | 0|
| `--beta1`         | Weight for **income influence** on solar panel adoption. Higher values increase adoption likelihood for higher-income agents. | 0.35    |
| `--beta2`         | Weight for **environmental consciousness** impact. Reflects how much agents care about the environment. | 0.05    |
| `--beta3`         | Weight for **neighbor solar adoption influence**. Represents peer effects on adoption decisions.   | 0.5     |
| `--beta4`         | Weight for **stubbornness** or resistance to change. Higher values decrease adoption likelihood despite other factors. | 0.2     |
| `--beta5`         | Weight for **education level** impact on adoption. Reflects the effect of education on solar panel uptake. | 0.3     |
| `--beta6`         | Weight for **subsidy presence** impact. Models how subsidy availability influences adoption decisions. | 0.3     |
| `--beta7`         | Weight for **housing type** influence (house vs apartment). Reflects differences in adoption likelihood based on dwelling type. | 0.6     |


