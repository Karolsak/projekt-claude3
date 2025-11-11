"""
Test script to verify solutions to all review problems
"""

from economic_dispatch_core import PowerPlant, EconomicDispatch


def test_problem1():
    """
    Problem 1: Three plants, 300 MW total load
    dC1/dP1 = 30 + 0.15*P1, 25 ≤ P1 ≤ 125
    dC2/dP2 = 40 + 0.20*P2, 30 ≤ P2 ≤ 100
    dC3/dP3 = 15 + 0.18*P3, 50 ≤ P3 ≤ 200
    """
    print("=" * 80)
    print("PROBLEM 1: Three plants, 300 MW load")
    print("=" * 80)

    # Convert incremental costs to cost functions
    # dC/dP = 2*a*P + b
    # For dC1/dP1 = 0.15*P1 + 30: 2*a1 = 0.15 => a1 = 0.075, b1 = 30
    plant1 = PowerPlant(0.075, 30, 0, "Plant 1", Pmin=25, Pmax=125)
    plant2 = PowerPlant(0.10, 40, 0, "Plant 2", Pmin=30, Pmax=100)
    plant3 = PowerPlant(0.09, 15, 0, "Plant 3", Pmin=50, Pmax=200)

    ed = EconomicDispatch([plant1, plant2, plant3])
    powers, costs, lam, feasible, total_cost = ed.solve(300)

    print(f"\nIncremental Cost Characteristics:")
    print(f"  dC1/dP1 = {2*plant1.a:.2f}P1 + {plant1.b:.2f}")
    print(f"  dC2/dP2 = {2*plant2.a:.2f}P2 + {plant2.b:.2f}")
    print(f"  dC3/dP3 = {2*plant3.a:.2f}P3 + {plant3.b:.2f}")

    print(f"\nOptimal Load Scheduling:")
    print(f"  Lambda (λ) = {lam:.4f} Rs/MWh")
    print(f"  P1 = {powers[0]:.4f} MW (Constraints: {plant1.Pmin}-{plant1.Pmax} MW)")
    print(f"  P2 = {powers[1]:.4f} MW (Constraints: {plant2.Pmin}-{plant2.Pmax} MW)")
    print(f"  P3 = {powers[2]:.4f} MW (Constraints: {plant3.Pmin}-{plant3.Pmax} MW)")
    print(f"  Total Generation = {sum(powers):.4f} MW")
    print(f"\nCosts:")
    print(f"  Cost1 = {costs[0]:.2f} Rs/hr")
    print(f"  Cost2 = {costs[1]:.2f} Rs/hr")
    print(f"  Cost3 = {costs[2]:.2f} Rs/hr")
    print(f"  Total Cost = {total_cost:.2f} Rs/hr")
    print(f"\nFeasibility: {'✓ FEASIBLE' if feasible else '✗ INFEASIBLE'}")

    # Verify equal lambda condition
    print(f"\nVerification (Equal Lambda Condition):")
    print(f"  dC1/dP1 at P1 = {plant1.incremental_cost(powers[0]):.4f} Rs/MWh")
    print(f"  dC2/dP2 at P2 = {plant2.incremental_cost(powers[1]):.4f} Rs/MWh")
    print(f"  dC3/dP3 at P3 = {plant3.incremental_cost(powers[2]):.4f} Rs/MWh")

    print()


def test_problem2():
    """
    Problem 2: Two plants, 300 MW load
    dC1/dP1 = 0.15*P1 + 30.0
    dC2/dP2 = 0.25*P2 + 20.0
    """
    print("=" * 80)
    print("PROBLEM 2: Two plants, 300 MW load")
    print("=" * 80)

    plant1 = PowerPlant(0.075, 30, 0, "Plant 1", Pmin=0, Pmax=300)
    plant2 = PowerPlant(0.125, 20, 0, "Plant 2", Pmin=0, Pmax=300)

    ed = EconomicDispatch([plant1, plant2])
    powers, costs, lam, feasible, total_cost = ed.solve(300)

    print(f"\nOptimal Load Sharing:")
    print(f"  Lambda (λ) = {lam:.4f} Rs/MWh")
    print(f"  P1 = {powers[0]:.4f} MW")
    print(f"  P2 = {powers[1]:.4f} MW")
    print(f"  Total = {sum(powers):.4f} MW")
    print(f"\nCosts:")
    print(f"  Cost1 = {costs[0]:.2f} Rs/hr")
    print(f"  Cost2 = {costs[1]:.2f} Rs/hr")
    print(f"  Total Cost = {total_cost:.2f} Rs/hr")

    # Calculate cost with equal sharing
    print(f"\nEqual Load Sharing (P1 = P2 = 150 MW):")
    cost1_equal = plant1.cost(150)
    cost2_equal = plant2.cost(150)
    total_equal = cost1_equal + cost2_equal
    print(f"  Cost1 = {cost1_equal:.2f} Rs/hr")
    print(f"  Cost2 = {cost2_equal:.2f} Rs/hr")
    print(f"  Total Cost = {total_equal:.2f} Rs/hr")
    print(f"\nExtra Cost with Equal Sharing = {total_equal - total_cost:.2f} Rs/hr")

    print()


def test_problem3():
    """
    Problem 3: Three plants, 180 MW load
    C1 = 0.04*P1² + 20*P1 + 230
    C2 = 0.06*P2² + 18*P2 + 200
    C3 = 0.15*P3² + 15*P3 + 180
    """
    print("=" * 80)
    print("PROBLEM 3: Three plants, 180 MW load")
    print("=" * 80)

    plant1 = PowerPlant(0.04, 20, 230, "Plant 1", Pmin=0, Pmax=200)
    plant2 = PowerPlant(0.06, 18, 200, "Plant 2", Pmin=0, Pmax=200)
    plant3 = PowerPlant(0.15, 15, 180, "Plant 3", Pmin=0, Pmax=200)

    ed = EconomicDispatch([plant1, plant2, plant3])
    powers, costs, lam, feasible, total_cost = ed.solve(180)

    print(f"\nCost Functions:")
    print(f"  C1 = {plant1.a}P1² + {plant1.b}P1 + {plant1.c}")
    print(f"  C2 = {plant2.a}P2² + {plant2.b}P2 + {plant2.c}")
    print(f"  C3 = {plant3.a}P3² + {plant3.b}P3 + {plant3.c}")

    print(f"\nOptimal Dispatch:")
    print(f"  Lambda (λ) = {lam:.4f} Rs/MWh")
    print(f"  P1 = {powers[0]:.4f} MW")
    print(f"  P2 = {powers[1]:.4f} MW")
    print(f"  P3 = {powers[2]:.4f} MW")
    print(f"  Total = {sum(powers):.4f} MW")

    print(f"\nCosts:")
    print(f"  Cost1 = {costs[0]:.2f} Rs/hr")
    print(f"  Cost2 = {costs[1]:.2f} Rs/hr")
    print(f"  Cost3 = {costs[2]:.2f} Rs/hr")
    print(f"  Total Cost = {total_cost:.2f} Rs/hr")

    print(f"\nMinimum Input Cost of Received Power:")
    # Input cost = Total cost / Total power
    unit_cost = total_cost / 180
    print(f"  {unit_cost:.4f} Rs/MWh")

    print()


def test_problem4():
    """
    Problem 4: Two plants, 210 MW load
    dC1/dP1 = 0.15*P1 + 50.0
    dC2/dP2 = 0.2*P2 + 40.0
    Compare optimal vs equal sharing (P1 = P2 = 105 MW)
    """
    print("=" * 80)
    print("PROBLEM 4: Two plants, 210 MW load")
    print("=" * 80)

    plant1 = PowerPlant(0.075, 50, 0, "Plant 1", Pmin=0, Pmax=210)
    plant2 = PowerPlant(0.10, 40, 0, "Plant 2", Pmin=0, Pmax=210)

    ed = EconomicDispatch([plant1, plant2])
    powers, costs, lam, feasible, total_cost = ed.solve(210)

    print(f"\nOptimal Load Scheduling:")
    print(f"  Lambda (λ) = {lam:.4f} Rs/MWh")
    print(f"  P1 = {powers[0]:.4f} MW")
    print(f"  P2 = {powers[1]:.4f} MW")
    print(f"  Total Cost = {total_cost:.2f} Rs/hr")

    # Calculate cost with P1 = P2 = 105 MW
    print(f"\nEqual Load Sharing (P1 = P2 = 105 MW):")
    cost1_equal = plant1.cost(105)
    cost2_equal = plant2.cost(105)
    total_equal = cost1_equal + cost2_equal
    print(f"  Cost1 = {cost1_equal:.2f} Rs/hr")
    print(f"  Cost2 = {cost2_equal:.2f} Rs/hr")
    print(f"  Total Cost = {total_equal:.2f} Rs/hr")

    print(f"\nExtra Cost Increased = {total_equal - total_cost:.2f} Rs/hr")

    print()


def main():
    """Run all problem tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ECONOMIC DISPATCH PROBLEM SOLUTIONS" + " " * 23 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    test_problem1()
    test_problem2()
    test_problem3()
    test_problem4()

    print("=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
