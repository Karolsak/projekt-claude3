"""
Core economic dispatch algorithms (no GUI dependencies)
"""

import numpy as np


class PowerPlant:
    """Represents a power plant with cost characteristics"""

    def __init__(self, a, b, c, name="Plant"):
        self.a = a  # Quadratic coefficient
        self.b = b  # Linear coefficient
        self.c = c  # Constant
        self.name = name
        self.Pmin = 0  # Minimum power generation (MW)
        self.Pmax = 100  # Maximum power generation (MW)

    def cost(self, P):
        """Calculate total cost C = a*P^2 + b*P + c"""
        return self.a * P**2 + self.b * P + self.c

    def incremental_cost(self, P):
        """Calculate incremental cost dC/dP = 2*a*P + b"""
        return 2 * self.a * P + self.b

    def power_from_lambda(self, lam):
        """Calculate power generation from lambda (incremental cost)"""
        # lambda = 2*a*P + b  =>  P = (lambda - b) / (2*a)
        return (lam - self.b) / (2 * self.a)


class EconomicDispatch:
    """Solves economic dispatch problem"""

    def __init__(self, plants):
        self.plants = plants

    def solve(self, total_load):
        """
        Solve economic dispatch for given total load
        Returns: (powers, costs, lambda, feasible, total_cost)
        """
        n = len(self.plants)

        # Initial lambda (average of incremental costs at mid-range)
        lambda_min = min(plant.incremental_cost(plant.Pmin) for plant in self.plants)
        lambda_max = max(plant.incremental_cost(plant.Pmax) for plant in self.plants)
        lam = (lambda_min + lambda_max) / 2

        # Lambda iteration method
        tolerance = 0.001
        max_iterations = 100

        for iteration in range(max_iterations):
            powers = []

            for plant in self.plants:
                # Calculate power for this lambda
                P = plant.power_from_lambda(lam)

                # Apply limits
                if P < plant.Pmin:
                    P = plant.Pmin
                elif P > plant.Pmax:
                    P = plant.Pmax

                powers.append(P)

            # Check if power balance is satisfied
            total_generation = sum(powers)
            error = total_generation - total_load

            if abs(error) < tolerance:
                break

            # Adjust lambda
            # If generation > load, decrease lambda
            # If generation < load, increase lambda
            if error > 0:
                lambda_max = lam
            else:
                lambda_min = lam

            lam = (lambda_min + lambda_max) / 2

        # Calculate costs
        costs = [plant.cost(P) for plant, P in zip(self.plants, powers)]
        total_cost = sum(costs)

        # Check feasibility
        feasible = all(plant.Pmin <= P <= plant.Pmax for plant, P in zip(self.plants, powers))

        return powers, costs, lam, feasible, total_cost


class ODESolver:
    """Implements ODE solvers for dynamic simulation"""

    @staticmethod
    def euler(f, y0, t_span, dt):
        """
        Euler method
        f: derivative function dy/dt = f(t, y)
        y0: initial conditions
        t_span: (t0, tf) time span
        dt: time step
        """
        t0, tf = t_span
        t = np.arange(t0, tf + dt, dt)
        n = len(t)
        y = np.zeros((n, len(y0)))
        y[0] = y0

        for i in range(n - 1):
            y[i + 1] = y[i] + dt * f(t[i], y[i])

        return t, y

    @staticmethod
    def rk45(f, y0, t_span, dt):
        """
        Runge-Kutta 4th order method (RK45)
        f: derivative function dy/dt = f(t, y)
        y0: initial conditions
        t_span: (t0, tf) time span
        dt: time step
        """
        t0, tf = t_span
        t = np.arange(t0, tf + dt, dt)
        n = len(t)
        y = np.zeros((n, len(y0)))
        y[0] = y0

        for i in range(n - 1):
            k1 = f(t[i], y[i])
            k2 = f(t[i] + dt/2, y[i] + dt*k1/2)
            k3 = f(t[i] + dt/2, y[i] + dt*k2/2)
            k4 = f(t[i] + dt, y[i] + dt*k3)

            y[i + 1] = y[i] + (dt/6) * (k1 + 2*k2 + 2*k3 + k4)

        return t, y
