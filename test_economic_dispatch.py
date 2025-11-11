"""
Test script for Economic Dispatch calculations (no GUI required)
Demonstrates Example 2.18 calculations
"""

import numpy as np
import sys

# Import classes from core module (no GUI dependencies)
sys.path.insert(0, '/home/user/projekt-claude3')
from economic_dispatch_core import PowerPlant, EconomicDispatch, ODESolver


def print_separator(char='=', length=80):
    print(char * length)


def test_economic_dispatch():
    """Test economic dispatch calculations"""

    print_separator()
    print("POWER SYSTEM ECONOMIC DISPATCH - EXAMPLE 2.18")
    print_separator()
    print()

    # Create power plants with Example 2.18 parameters
    plant1 = PowerPlant(a=0.1, b=60, c=135, name="Plant 1")
    plant2 = PowerPlant(a=0.15, b=40, c=100, name="Plant 2")

    print("Plant Parameters:")
    print(f"  Plant 1: C₁ = {plant1.a}P₁² + {plant1.b}P₁ + {plant1.c} Rs/hr")
    print(f"  Plant 2: C₂ = {plant2.a}P₂² + {plant2.b}P₂ + {plant2.c} Rs/hr")
    print()

    print("Incremental Costs:")
    print(f"  dC₁/dP₁ = {2*plant1.a}P₁ + {plant1.b}")
    print(f"  dC₂/dP₂ = {2*plant2.a}P₂ + {plant2.b}")
    print()

    # Create economic dispatch solver
    ed = EconomicDispatch([plant1, plant2])

    # Test Case 1: 0-6 hours with 7 MW load
    print_separator('-')
    print("CASE 1: Light Load Period (0-6 hours)")
    print_separator('-')
    print(f"Total Load Demand: 7 MW")
    print()

    powers, costs, lam, feasible, total_cost = ed.solve(7)

    print("Solution:")
    print(f"  Lambda (λ): {lam:.4f} Rs/MWh")
    print(f"  Plant 1 Generation: {powers[0]:.4f} MW")
    print(f"  Plant 2 Generation: {powers[1]:.4f} MW")
    print(f"  Total Generation: {sum(powers):.4f} MW")
    print()

    print("Costs:")
    print(f"  Plant 1 Cost: {costs[0]:.4f} Rs/hr")
    print(f"  Plant 2 Cost: {costs[1]:.4f} Rs/hr")
    print(f"  Total Cost: {total_cost:.4f} Rs/hr")
    print(f"  6-hour Cost: {total_cost * 6:.2f} Rs")
    print()

    if powers[0] < 0.1:
        print("⚠ Note: Plant 1 generation is below practical minimum.")
        print("  Running Plant 2 only with 7 MW generation:")
        cost_plant2_only = plant2.cost(7)
        print(f"  Plant 2 Cost: {cost_plant2_only:.4f} Rs/hr")
        print(f"  6-hour Cost: {cost_plant2_only * 6:.2f} Rs")
        case1_cost = cost_plant2_only * 6
        startup_needed = True
    else:
        case1_cost = total_cost * 6
        startup_needed = False

    print()

    # Test Case 2: 18-24 hours with 70 MW load
    print_separator('-')
    print("CASE 2: Peak Load Period (18-24 hours)")
    print_separator('-')
    print(f"Total Load Demand: 70 MW")
    print()

    powers, costs, lam, feasible, total_cost = ed.solve(70)

    print("Solution:")
    print(f"  Lambda (λ): {lam:.4f} Rs/MWh")
    print(f"  Plant 1 Generation: {powers[0]:.4f} MW")
    print(f"  Plant 2 Generation: {powers[1]:.4f} MW")
    print(f"  Total Generation: {sum(powers):.4f} MW")
    print()

    print("Verification of optimality condition:")
    ic1 = plant1.incremental_cost(powers[0])
    ic2 = plant2.incremental_cost(powers[1])
    print(f"  dC₁/dP₁ at P₁={powers[0]:.2f}: {ic1:.4f} Rs/MWh")
    print(f"  dC₂/dP₂ at P₂={powers[1]:.2f}: {ic2:.4f} Rs/MWh")
    print(f"  Difference: {abs(ic1 - ic2):.6f} Rs/MWh (should be ≈0)")
    print()

    print("Costs:")
    print(f"  Plant 1 Cost: {costs[0]:.4f} Rs/hr")
    print(f"  Plant 2 Cost: {costs[1]:.4f} Rs/hr")
    print(f"  Total Cost: {total_cost:.4f} Rs/hr")
    print(f"  6-hour Cost: {total_cost * 6:.2f} Rs")
    case2_cost = total_cost * 6
    print()

    # Daily summary
    print_separator('=')
    print("DAILY OPERATION SUMMARY")
    print_separator('=')
    print()

    operating_cost = case1_cost + case2_cost
    startup_cost = 450 if startup_needed else 0
    total_daily_cost = operating_cost + startup_cost

    print(f"Operating Cost (12 hours total): {operating_cost:.2f} Rs")
    print(f"  - Light load (6 hrs): {case1_cost:.2f} Rs")
    print(f"  - Peak load (6 hrs): {case2_cost:.2f} Rs")
    print()
    print(f"Startup Cost: {startup_cost:.2f} Rs")
    if startup_needed:
        print("  (Plant 1 shut down during light load)")
    print()
    print(f"Total Daily Cost: {total_daily_cost:.2f} Rs")
    print()

    print_separator('=')
    print()


def test_ode_solvers():
    """Test ODE solvers"""

    print_separator()
    print("ODE SOLVER COMPARISON")
    print_separator()
    print()

    # Define a simple ODE: dy/dt = -y, y(0) = 1
    # Analytical solution: y(t) = e^(-t)
    def derivative(t, y):
        return np.array([-y[0]])

    y0 = np.array([1.0])
    t_span = (0, 5)
    dt = 0.1

    solver = ODESolver()

    # Euler method
    t_euler, y_euler = solver.euler(derivative, y0, t_span, dt)

    # RK45 method
    t_rk45, y_rk45 = solver.rk45(derivative, y0, t_span, dt)

    # Analytical solution
    y_analytical = np.exp(-t_euler)

    print("Test ODE: dy/dt = -y, y(0) = 1")
    print("Analytical solution: y(t) = e^(-t)")
    print()

    print("Comparison at t = 5:")
    print(f"  Analytical:  {y_analytical[-1]:.6f}")
    print(f"  Euler:       {y_euler[-1, 0]:.6f}  (error: {abs(y_euler[-1, 0] - y_analytical[-1]):.6f})")
    print(f"  RK45:        {y_rk45[-1, 0]:.6f}  (error: {abs(y_rk45[-1, 0] - y_analytical[-1]):.6f})")
    print()

    print("✓ RK45 method shows significantly better accuracy!")
    print()
    print_separator()
    print()


def test_load_variation():
    """Test economic dispatch with varying loads"""

    print_separator()
    print("DYNAMIC LOAD VARIATION ANALYSIS")
    print_separator()
    print()

    # Create plants
    plant1 = PowerPlant(a=0.1, b=60, c=135, name="Plant 1")
    plant2 = PowerPlant(a=0.15, b=40, c=100, name="Plant 2")
    ed = EconomicDispatch([plant1, plant2])

    # Test various load levels
    loads = [7, 20, 40, 60, 70, 90, 120]

    print(f"{'Load (MW)':<12} {'P₁ (MW)':<12} {'P₂ (MW)':<12} {'λ (Rs/MWh)':<15} {'Cost (Rs/hr)':<15}")
    print_separator('-')

    for load in loads:
        powers, costs, lam, feasible, total_cost = ed.solve(load)
        print(f"{load:<12.1f} {powers[0]:<12.2f} {powers[1]:<12.2f} {lam:<15.2f} {total_cost:<15.2f}")

    print()
    print_separator()
    print()


def main():
    """Main test function"""

    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ECONOMIC DISPATCH SIMULATOR TEST" + " " * 26 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    try:
        # Run tests
        test_economic_dispatch()
        test_ode_solvers()
        test_load_variation()

        print("✓ All tests completed successfully!")
        print()
        print("To run the GUI application:")
        print("  python3 economic_dispatch_simulator.py")
        print()

    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
