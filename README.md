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
