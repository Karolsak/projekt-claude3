# Quick Start Guide - Economic Dispatch Simulator

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements_ed.txt
   ```

2. **Install tkinter (if not already installed):**
   - **Ubuntu/Debian:**
     ```bash
     sudo apt-get install python3-tk
     ```
   - **macOS:** Already included with Python
   - **Windows:** Already included with Python

## Running the Application

### GUI Mode (Full Interactive Visualization)

```bash
python3 economic_dispatch_simulator.py
```

**Features:**
- Interactive sliders for all parameters
- Real-time calculation updates
- Four dynamic visualization plots
- Dynamic simulation with ODE solvers (Euler/RK45)
- 24-hour load cycle animation
- Detailed results display

### Test Mode (Calculations Only, No GUI Required)

```bash
python3 test_economic_dispatch.py
```

**Output:**
- Example 2.18 calculations for 7 MW and 70 MW loads
- Daily cost analysis with startup costs
- ODE solver accuracy comparison
- Load variation analysis table

## Quick Usage Examples

### 1. Solve Example 2.18 (Default)

Launch GUI and click "Calculate" - parameters are pre-set!

Or use preset buttons:
- **"0-6 hrs (7 MW)"** - Light load scenario
- **"18-24 hrs (70 MW)"** - Peak load scenario

### 2. Run Dynamic Simulation

1. Select ODE solver: **RK45** (recommended) or **Euler**
2. Adjust **Simulation Speed** slider (0.1x to 5x)
3. Click **"Start Simulation"**
4. Watch load vary over 24 hours with real-time power allocation

### 3. Experiment with Parameters

Adjust any slider:
- **Plant 1 coefficients:** a₁, b₁, c₁
- **Plant 2 coefficients:** a₂, b₂, c₂
- **Load demand:** 1-150 MW
- **Startup cost:** 0-1000 Rs

The system recalculates automatically!

### 4. Analyze Results

Check the **Results** panel for:
- Optimal power dispatch (P₁, P₂)
- Incremental cost (λ)
- Individual and total costs
- Feasibility status
- Example 2.18 specific analysis

## Key Results from Example 2.18

| Period | Load | P₁ (MW) | P₂ (MW) | Cost (Rs/hr) | 6-hr Cost (Rs) |
|--------|------|---------|---------|--------------|----------------|
| 0-6 hrs | 7 MW | 0 (off) | 7.0 | 387.35 | 2,324.10 |
| 18-24 hrs | 70 MW | 2.0 | 68.0 | 3,769.04 | 22,614.26 |

**Total Daily Operating Cost:** 24,938.36 Rs
**Startup Cost (Plant 1):** 450.00 Rs
**Total Daily Cost:** **25,388.36 Rs**

## Visualization Plots

### Static Mode (After "Calculate"):
1. **Cost Curves** - Quadratic cost functions for both plants
2. **Incremental Cost Curves** - Shows optimal λ intersection
3. **Power Allocation Pie Chart** - Visual load distribution
4. **Cost Breakdown Bar Chart** - Individual and total costs

### Dynamic Mode (During "Start Simulation"):
1. **Load Demand vs Time** - Sinusoidal 24-hour profile
2. **Power Generation vs Time** - Dynamic P₁ and P₂ allocation
3. **Operating Costs vs Time** - Real-time cost tracking
4. **Lambda (λ) vs Time** - Incremental cost variation

## Troubleshooting

**"ModuleNotFoundError: No module named 'numpy'"**
```bash
pip install numpy matplotlib
```

**"ModuleNotFoundError: No module named 'tkinter'"**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Run test mode instead (no GUI required)
python3 test_economic_dispatch.py
```

**GUI window too small/large**
- The window auto-resizes! Just resize manually
- All plots adjust automatically

**Simulation too fast/slow**
- Adjust **Simulation Speed** slider (0.1x - 5x)

## Understanding the Results

### Optimality Condition
Economic dispatch is optimal when:
```
dC₁/dP₁ = dC₂/dP₂ = λ
```

This means both plants operate at the same **incremental cost** (λ).

### Why Plant 1 Shuts Down at 7 MW
- At low loads, Plant 2 is more economical
- Plant 1 would need negative generation (impossible!)
- Solution: Run Plant 2 only, save startup cost

### Lambda (λ) Interpretation
- λ = marginal cost of supplying 1 more MW
- Higher load → higher λ
- All running plants have same λ (optimal condition)

## Advanced Features

### Custom Cost Functions
Modify sliders to test different plant characteristics:
- **Higher a → steeper quadratic cost**
- **Higher b → higher linear cost**
- **Higher c → higher fixed cost**

### ODE Solver Comparison
- **Euler:** Fast, less accurate (1st order)
- **RK45:** Slower, very accurate (4th order)

Try both to see the difference!

## File Structure

```
projekt-claude3/
├── economic_dispatch_core.py       # Core algorithms (no GUI)
├── economic_dispatch_simulator.py  # Full GUI application
├── test_economic_dispatch.py       # Test calculations (no GUI)
├── requirements_ed.txt             # Python dependencies
├── README_ECONOMIC_DISPATCH.md     # Detailed documentation
└── QUICKSTART.md                   # This file
```

## Support

For issues or questions:
1. Check README_ECONOMIC_DISPATCH.md for detailed info
2. Run test mode to verify calculations
3. Ensure all dependencies are installed

## Example Session

```bash
# Install dependencies
pip install numpy matplotlib

# Run test calculations
python3 test_economic_dispatch.py

# Launch GUI (if tkinter available)
python3 economic_dispatch_simulator.py

# In GUI:
# 1. Click "0-6 hrs (7 MW)" preset
# 2. Click "Calculate"
# 3. Observe Plant 1 shuts down
# 4. Click "18-24 hrs (70 MW)" preset
# 5. Click "Calculate"
# 6. See optimal dispatch P₁=2, P₂=68
# 7. Click "Start Simulation"
# 8. Watch 24-hour dynamic simulation!
```

Enjoy exploring power system economic dispatch! 🔌⚡
