# Quick Start Guide

## Running the Simulator

### Linux/Mac
```bash
chmod +x run_simulator.sh
./run_simulator.sh
```

### Windows
```batch
run_simulator.bat
```

### Direct Python
```bash
python3 economic_dispatch_simulator_enhanced.py
```

## First Time Usage

### Step 1: Load a Problem
Click one of the preset buttons on the left panel:
- **Problem 1** (default): 3 plants, 300 MW load
- **Problem 2**: 2 plants, 300 MW load
- **Problem 3**: 3 plants, 180 MW load
- **Problem 4**: 2 plants, 210 MW load

### Step 2: View Results
The results panel at the bottom shows:
- Optimal power generation for each plant
- Individual and total costs
- Lambda (system marginal cost)
- Feasibility status
- Power balance verification

### Step 3: Explore Parameters
Use the sliders on the left to adjust:
- **a, b, c**: Cost function coefficients (C = aP² + bP + c)
- **Pmin, Pmax**: Generator capacity constraints
- **Load**: Total system demand

Watch the plots update in real-time!

### Step 4: Run Dynamic Simulation
1. Select an ODE solver (Euler or RK45)
2. Adjust simulation speed (0.1x to 5x)
3. Click **"Start Simulation"**
4. Watch the 24-hour load cycle animation
5. Click **"Stop Simulation"** to pause

## Understanding the Plots

### Static Analysis Mode (Default)
- **Top Left**: Cost curves for each plant
- **Top Middle**: Incremental cost curves with optimal λ line
- **Top Right**: Power allocation pie chart
- **Bottom Left**: Cost breakdown by plant
- **Bottom Middle**: Generation vs constraints
- **Bottom Right**: Verification of equal lambda condition

### Dynamic Simulation Mode
- **Top Left**: Load demand over 24 hours
- **Top Middle**: Power generation from each plant over time
- **Top Right**: Total operating cost over time
- **Bottom Left**: System marginal cost (λ) over time
- **Bottom Middle**: Stacked area chart of power distribution
- **Bottom Right**: Cumulative cost accumulation

## Key Concepts

### What is Economic Dispatch?
The problem of allocating generation among plants to minimize total cost while meeting load demand and respecting constraints.

### Why Equal Lambda?
For minimum cost, all plants must operate at the same **incremental cost** (λ):
```
dC₁/dP₁ = dC₂/dP₂ = dC₃/dP₃ = λ
```

This is the **equal incremental cost principle** - the fundamental optimality condition.

### What is Lambda (λ)?
- System marginal cost (Rs/MWh)
- Cost to generate one more MW
- Lagrange multiplier for power balance constraint
- Same for all plants at optimal dispatch

## Tips & Tricks

### Adjusting Parameters
- Small changes in 'a' have large impact on cost curves
- Reducing Pmax forces other plants to pick up slack
- Try making Plant 1 very expensive (high a, b) - it will generate less

### Exploring Infeasibility
- Set total load > sum of all Pmax values
- Set total load < sum of all Pmin values
- The solver will get as close as possible and flag infeasibility

### Comparing Solvers
- Euler: Faster but less accurate (first-order)
- RK45: Slower but more accurate (fourth-order)
- Speed difference is negligible for this problem

### Window Resizing
- Drag window edges - plots automatically adjust
- Maximize window for best viewing experience
- Works on any screen size (minimum 1200x800)

## Interpreting Results

### Feasible Solution
```
✓ FEASIBLE
```
- All constraints satisfied
- Power balance achieved
- All plants within limits

### Infeasible Solution
```
✗ INFEASIBLE
```
- One or more constraints violated
- Check warnings in results panel
- Adjust load or constraints

### Cost Comparison
Compare optimal vs equal sharing:
- **Problem 2**: Optimal saves 31.22 Rs/hr over equal split
- **Problem 4**: Optimal saves 32.27 Rs/hr over equal split

This demonstrates the value of economic dispatch!

## Keyboard Shortcuts

- **Ctrl+C**: Close simulator (in terminal)
- Window resize: Drag edges or maximize

## Common Issues

### Plots not visible
- Resize window slightly to trigger redraw
- Check that matplotlib is properly installed

### Simulation doesn't start
- Ensure parameters are valid
- Check that load is within feasible range
- Try resetting to defaults

### Sliders feel sluggish
- This is normal - calculations run on every change
- For smoother experience, stop simulation before adjusting

## Next Steps

1. **Experiment**: Try different cost functions
2. **Compare**: Load different problems and compare results
3. **Analyze**: Watch dynamic simulation to see how dispatch adapts to load
4. **Learn**: Read the mathematical background in README.md

## Running Tests

To verify all problem solutions:
```bash
python3 test_problems.py
```

Expected output:
- Problem 1: Total Cost = 10,190.43 Rs/hr
- Problem 2: Total Cost = 11,968.78 Rs/hr
- Problem 3: Total Cost = 4,596.72 Rs/hr
- Problem 4: Total Cost = 11,347.11 Rs/hr

## Getting Help

If you encounter issues:
1. Check README.md for detailed documentation
2. Verify all dependencies are installed
3. Try the test script to ensure calculations are correct
4. Reset to defaults and try again

---

**Enjoy exploring economic dispatch!** 🔌⚡💡
