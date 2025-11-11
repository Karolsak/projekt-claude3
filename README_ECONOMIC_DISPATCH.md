# Power System Economic Dispatch Simulator

## Overview

This application solves the economic dispatch problem for power systems with dynamic simulation capabilities. It implements Example 2.18 from power system analysis, demonstrating optimal load distribution between two power plants.

## Features

### 1. **Interactive GUI with Tkinter**
   - Responsive layout with automatic width/height adjustment
   - Real-time updates when window is resized
   - Professional interface with organized control panels

### 2. **Economic Dispatch Solver**
   - Lambda iteration method for optimal power distribution
   - Constraint handling for minimum/maximum generation limits
   - Cost optimization based on quadratic cost functions:
     - Plant 1: C₁ = 0.1P₁² + 60P₁ + 135 Rs/hr
     - Plant 2: C₂ = 0.15P₂² + 40P₂ + 100 Rs/hr

### 3. **Dynamic Simulation with ODE Solvers**
   - **Euler Method**: First-order numerical integration
   - **RK45 (Runge-Kutta)**: Fourth-order accurate method
   - Real-time visualization of load variation over 24-hour cycle
   - Sinusoidal load profile from 7 MW to 70 MW

### 4. **Interactive Sliders**
   - Adjust cost coefficients (a, b, c) for both plants
   - Modify load demand (1-150 MW)
   - Set startup costs (0-1000 Rs)
   - Control simulation speed (0.1x to 5x)

### 5. **Comprehensive Visualization**
   Four dynamic plots:

   **Static Mode:**
   - **Cost Curves**: Total cost vs power generation for both plants
   - **Incremental Cost Curves**: Shows optimal λ (lambda) intersection
   - **Power Allocation Pie Chart**: Visual distribution of generation
   - **Cost Breakdown Bar Chart**: Individual and total costs

   **Simulation Mode:**
   - **Load Demand vs Time**: 24-hour load profile
   - **Power Generation vs Time**: Dynamic allocation to plants
   - **Operating Costs vs Time**: Real-time cost tracking
   - **Lambda (λ) vs Time**: Incremental cost variation

### 6. **Detailed Results Display**
   - Plant parameters and incremental cost equations
   - Optimal dispatch solution with λ value
   - Power generation and costs for each plant
   - Feasibility check
   - Example 2.18 specific calculations:
     - 0-6 hours (7 MW load)
     - 18-24 hours (70 MW load)
     - Daily operating and startup costs

## Installation

### Requirements
```bash
pip install numpy matplotlib
```

Python 3.6+ with tkinter (usually included with Python)

## Usage

### Running the Application
```bash
python economic_dispatch_simulator.py
```

### Using the Interface

1. **Adjust Parameters**:
   - Use sliders to modify plant cost coefficients
   - Change load demand using the Load slider
   - Preset buttons load Example 2.18 scenarios

2. **Calculate Economic Dispatch**:
   - Click "Calculate" to solve for current parameters
   - Results appear in plots and text area

3. **Run Dynamic Simulation**:
   - Select ODE solver (Euler or RK45)
   - Adjust simulation speed
   - Click "Start Simulation" to animate 24-hour cycle
   - Click "Stop Simulation" to pause

4. **Reset**:
   - Click "Reset" to restore default Example 2.18 values

## Example 2.18 Solution

### Problem Statement
Two plants with cost characteristics must meet a daily load cycle:
- 0 to 6 hrs: 7 MW
- 18 to 24 hrs: 70 MW

Determine if it's economical to keep both plants running or shut one down during light load.

### Solution Approach

1. **Optimality Condition**:
   ```
   dC₁/dP₁ = dC₂/dP₂ = λ
   ```

2. **For 7 MW Load**:
   - Solving: 0.2P₁ + 60 = 0.3P₂ + 40
   - With: P₁ + P₂ = 7
   - Result: P₁ = -35.8 MW (infeasible!)
   - Solution: Run Plant 2 only with P₂ = 7 MW
   - Cost: 387.35 Rs/hr

3. **For 70 MW Load**:
   - Solving same optimality condition
   - With: P₁ + P₂ = 70
   - Result: P₁ = 2 MW, P₂ = 68 MW
   - Cost: 255.4 + 3,513.6 = 3,769 Rs/hr

4. **Daily Cost Analysis**:
   - Operating cost: 387.35 × 6 + 3,769 × 6 = 24,938.10 Rs
   - Startup cost: 450 Rs
   - **Total: 25,388.10 Rs**

## Mathematical Background

### Cost Function
For each plant i:
```
Cᵢ = aᵢPᵢ² + bᵢPᵢ + cᵢ
```

### Incremental Cost
```
dCᵢ/dPᵢ = 2aᵢPᵢ + bᵢ
```

### Lambda Iteration Method
1. Initialize λ (incremental cost)
2. Calculate power: Pᵢ = (λ - bᵢ) / (2aᵢ)
3. Apply limits: Pᵢ,min ≤ Pᵢ ≤ Pᵢ,max
4. Check power balance: ΣPᵢ = PD
5. Adjust λ until convergence

### ODE Solver for Load Dynamics

**Sinusoidal Load Model**:
```
L(t) = Lmean + Lamplitude × sin(ωt)
dL/dt = Lamplitude × ω × cos(ωt)
```

**Euler Method**:
```
y[n+1] = y[n] + h × f(t[n], y[n])
```

**RK45 Method**:
```
k₁ = f(tₙ, yₙ)
k₂ = f(tₙ + h/2, yₙ + h×k₁/2)
k₃ = f(tₙ + h/2, yₙ + h×k₂/2)
k₄ = f(tₙ + h, yₙ + h×k₃)
y[n+1] = y[n] + (h/6) × (k₁ + 2k₂ + 2k₃ + k₄)
```

## Features Implemented

✅ Automatic window resize handling
✅ Dynamic simulation with real-time updates
✅ ODE solvers (Euler and RK45)
✅ Interactive sliders for all parameters
✅ Multiple synchronized visualizations
✅ Detailed results analysis
✅ Example 2.18 preset buttons
✅ Threaded simulation for smooth UI
✅ Cost optimization algorithms
✅ Feasibility checking
✅ Professional layout and styling

## Technical Details

- **GUI Framework**: Tkinter with ttk widgets
- **Plotting**: Matplotlib with FigureCanvasTkAgg
- **Numerical Methods**: NumPy for calculations
- **Threading**: Separate thread for simulation
- **Update Rate**: 50ms base (adjustable with speed slider)

## Troubleshooting

1. **Import Errors**:
   ```bash
   pip install --upgrade numpy matplotlib
   ```

2. **Tkinter Not Found**:
   - Ubuntu/Debian: `sudo apt-get install python3-tk`
   - macOS: Included with Python
   - Windows: Included with Python

3. **Plots Not Updating**:
   - Check if simulation is running
   - Try stopping and restarting simulation

## License

Educational use - Power System Analysis Example 2.18

## Author

Created for power system economic dispatch analysis and optimization studies.
