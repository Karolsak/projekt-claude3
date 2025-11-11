"""
Power System Economic Dispatch Simulator
Solves Example 2.18 with dynamic simulation and interactive visualization
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time

# Import core classes
from economic_dispatch_core import PowerPlant, EconomicDispatch, ODESolver


class EconomicDispatchGUI:
    """Main GUI application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Power System Economic Dispatch Simulator")
        self.root.geometry("1400x900")

        # Default parameters from Example 2.18
        self.a1_var = tk.DoubleVar(value=0.1)
        self.b1_var = tk.DoubleVar(value=60)
        self.c1_var = tk.DoubleVar(value=135)

        self.a2_var = tk.DoubleVar(value=0.15)
        self.b2_var = tk.DoubleVar(value=40)
        self.c2_var = tk.DoubleVar(value=100)

        self.load_var = tk.DoubleVar(value=70)
        self.startup_cost_var = tk.DoubleVar(value=450)

        self.solver_var = tk.StringVar(value="RK45")
        self.simulation_speed_var = tk.DoubleVar(value=1.0)

        # Simulation state
        self.is_simulating = False
        self.simulation_thread = None

        # Setup GUI
        self.setup_gui()

        # Initial calculation
        self.calculate()

    def setup_gui(self):
        """Setup the GUI layout"""

        # Configure root grid to be resizable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Left panel - Controls
        self.create_control_panel(main_frame)

        # Right panel - Visualization
        self.create_visualization_panel(main_frame)

        # Bottom panel - Results
        self.create_results_panel(main_frame)

    def create_control_panel(self, parent):
        """Create control panel with sliders"""

        control_frame = ttk.LabelFrame(parent, text="Control Panel", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))

        row = 0

        # Plant 1 parameters
        ttk.Label(control_frame, text="Plant 1: C₁ = a₁P₁² + b₁P₁ + c₁",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        self.create_slider(control_frame, "a₁ (Quadratic):", self.a1_var, 0.01, 1.0, row)
        row += 1
        self.create_slider(control_frame, "b₁ (Linear):", self.b1_var, 10, 100, row)
        row += 1
        self.create_slider(control_frame, "c₁ (Constant):", self.c1_var, 50, 500, row)
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Plant 2 parameters
        ttk.Label(control_frame, text="Plant 2: C₂ = a₂P₂² + b₂P₂ + c₂",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        self.create_slider(control_frame, "a₂ (Quadratic):", self.a2_var, 0.01, 1.0, row)
        row += 1
        self.create_slider(control_frame, "b₂ (Linear):", self.b2_var, 10, 100, row)
        row += 1
        self.create_slider(control_frame, "c₂ (Constant):", self.c2_var, 50, 500, row)
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Load and cost parameters
        ttk.Label(control_frame, text="System Parameters",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        self.create_slider(control_frame, "Load (MW):", self.load_var, 1, 150, row)
        row += 1
        self.create_slider(control_frame, "Startup Cost (Rs):", self.startup_cost_var, 0, 1000, row)
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # ODE Solver selection
        ttk.Label(control_frame, text="ODE Solver:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=5)
        solver_combo = ttk.Combobox(control_frame, textvariable=self.solver_var,
                                    values=["Euler", "RK45"], state="readonly", width=15)
        solver_combo.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Simulation speed
        self.create_slider(control_frame, "Simulation Speed:", self.simulation_speed_var, 0.1, 5.0, row)
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="Calculate", command=self.calculate).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Start Simulation", command=self.toggle_simulation).pack(side=tk.LEFT, padx=5)
        self.sim_button = button_frame.winfo_children()[1]  # Store reference to simulation button
        ttk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.LEFT, padx=5)
        row += 1

        # Example 2.18 preset buttons
        ttk.Label(control_frame, text="Load Presets (Example 2.18):",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        preset_frame = ttk.Frame(control_frame)
        preset_frame.grid(row=row, column=0, columnspan=3, pady=5)

        ttk.Button(preset_frame, text="0-6 hrs (7 MW)",
                  command=lambda: self.load_var.set(7)).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="18-24 hrs (70 MW)",
                  command=lambda: self.load_var.set(70)).pack(side=tk.LEFT, padx=2)

    def create_slider(self, parent, label, variable, from_, to, row):
        """Create a slider with label and value display"""

        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)

        slider = ttk.Scale(parent, from_=from_, to=to, orient=tk.HORIZONTAL,
                          variable=variable, command=lambda v: self.on_slider_change(variable))
        slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)

        value_label = ttk.Label(parent, text=f"{variable.get():.2f}")
        value_label.grid(row=row, column=2, sticky=tk.W, pady=2)

        # Store reference to update later
        variable.label = value_label

        # Configure column weights
        parent.grid_columnconfigure(1, weight=1)

    def on_slider_change(self, variable):
        """Update slider value label and recalculate"""
        variable.label.config(text=f"{variable.get():.2f}")
        if not self.is_simulating:
            self.calculate()

    def create_visualization_panel(self, parent):
        """Create visualization panel with plots"""

        viz_frame = ttk.LabelFrame(parent, text="Visualization", padding="10")
        viz_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)

        # Create subplots
        self.ax1 = self.fig.add_subplot(2, 2, 1)
        self.ax2 = self.fig.add_subplot(2, 2, 2)
        self.ax3 = self.fig.add_subplot(2, 2, 3)
        self.ax4 = self.fig.add_subplot(2, 2, 4)

        self.fig.tight_layout(pad=3.0)

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Bind resize event
        self.canvas.get_tk_widget().bind('<Configure>', self.on_resize)

    def create_results_panel(self, parent):
        """Create results panel"""

        results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=10, width=80,
                                                      font=('Courier', 9))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def calculate(self):
        """Calculate economic dispatch and update displays"""

        # Create power plants
        plant1 = PowerPlant(self.a1_var.get(), self.b1_var.get(), self.c1_var.get(), "Plant 1")
        plant2 = PowerPlant(self.a2_var.get(), self.b2_var.get(), self.c2_var.get(), "Plant 2")

        # Solve economic dispatch
        ed = EconomicDispatch([plant1, plant2])
        total_load = self.load_var.get()
        powers, costs, lam, feasible, total_cost = ed.solve(total_load)

        # Update plots
        self.update_plots(plant1, plant2, powers, costs, lam, total_load)

        # Update results text
        self.update_results_text(plant1, plant2, powers, costs, lam, total_cost, feasible)

    def update_plots(self, plant1, plant2, powers, costs, lam, total_load):
        """Update all plots"""

        # Clear all axes
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()

        # Plot 1: Cost curves and incremental costs
        P_range = np.linspace(0, 100, 200)

        C1 = [plant1.cost(P) for P in P_range]
        C2 = [plant2.cost(P) for P in P_range]

        self.ax1.plot(P_range, C1, 'b-', label='Plant 1 Cost', linewidth=2)
        self.ax1.plot(P_range, C2, 'r-', label='Plant 2 Cost', linewidth=2)
        self.ax1.axvline(powers[0], color='b', linestyle='--', alpha=0.7, label=f'P₁={powers[0]:.2f} MW')
        self.ax1.axvline(powers[1], color='r', linestyle='--', alpha=0.7, label=f'P₂={powers[1]:.2f} MW')
        self.ax1.set_xlabel('Power (MW)', fontsize=10)
        self.ax1.set_ylabel('Cost (Rs/hr)', fontsize=10)
        self.ax1.set_title('Cost Curves', fontsize=11, fontweight='bold')
        self.ax1.legend(fontsize=8)
        self.ax1.grid(True, alpha=0.3)

        # Plot 2: Incremental cost curves
        IC1 = [plant1.incremental_cost(P) for P in P_range]
        IC2 = [plant2.incremental_cost(P) for P in P_range]

        self.ax2.plot(P_range, IC1, 'b-', label='dC₁/dP₁', linewidth=2)
        self.ax2.plot(P_range, IC2, 'r-', label='dC₂/dP₂', linewidth=2)
        self.ax2.axhline(lam, color='g', linestyle='--', linewidth=2, label=f'λ={lam:.2f} Rs/MWh')
        self.ax2.axvline(powers[0], color='b', linestyle=':', alpha=0.5)
        self.ax2.axvline(powers[1], color='r', linestyle=':', alpha=0.5)
        self.ax2.set_xlabel('Power (MW)', fontsize=10)
        self.ax2.set_ylabel('Incremental Cost (Rs/MWh)', fontsize=10)
        self.ax2.set_title('Incremental Cost Curves', fontsize=11, fontweight='bold')
        self.ax2.legend(fontsize=8)
        self.ax2.grid(True, alpha=0.3)

        # Plot 3: Power allocation pie chart
        self.ax3.pie(powers, labels=[f'Plant 1\n{powers[0]:.2f} MW', f'Plant 2\n{powers[1]:.2f} MW'],
                    autopct='%1.1f%%', colors=['#3498db', '#e74c3c'], startangle=90)
        self.ax3.set_title(f'Power Allocation\nTotal Load: {total_load:.2f} MW',
                          fontsize=11, fontweight='bold')

        # Plot 4: Cost breakdown bar chart
        plants = ['Plant 1', 'Plant 2', 'Total']
        cost_values = [costs[0], costs[1], sum(costs)]
        colors = ['#3498db', '#e74c3c', '#2ecc71']

        bars = self.ax4.bar(plants, cost_values, color=colors, alpha=0.7, edgecolor='black')
        self.ax4.set_ylabel('Cost (Rs/hr)', fontsize=10)
        self.ax4.set_title('Cost Breakdown', fontsize=11, fontweight='bold')
        self.ax4.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, value in zip(bars, cost_values):
            height = bar.get_height()
            self.ax4.text(bar.get_x() + bar.get_width()/2., height,
                         f'{value:.2f}', ha='center', va='bottom', fontsize=9)

        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()

    def update_results_text(self, plant1, plant2, powers, costs, lam, total_cost, feasible):
        """Update results text area"""

        self.results_text.delete(1.0, tk.END)

        output = []
        output.append("=" * 80)
        output.append("ECONOMIC DISPATCH RESULTS")
        output.append("=" * 80)
        output.append("")

        output.append("PLANT PARAMETERS:")
        output.append(f"  Plant 1: C₁ = {plant1.a}P₁² + {plant1.b}P₁ + {plant1.c}")
        output.append(f"  Plant 2: C₂ = {plant2.a}P₂² + {plant2.b}P₂ + {plant2.c}")
        output.append("")

        output.append("INCREMENTAL COSTS:")
        output.append(f"  dC₁/dP₁ = {2*plant1.a}P₁ + {plant1.b}")
        output.append(f"  dC₂/dP₂ = {2*plant2.a}P₂ + {plant2.b}")
        output.append("")

        output.append("OPTIMAL DISPATCH:")
        output.append(f"  Total Load Demand: {self.load_var.get():.2f} MW")
        output.append(f"  Lambda (λ): {lam:.4f} Rs/MWh")
        output.append("")

        output.append(f"  Plant 1 Generation: {powers[0]:.4f} MW")
        output.append(f"  Plant 1 Cost: {costs[0]:.4f} Rs/hr")
        output.append(f"  Plant 1 Inc. Cost: {plant1.incremental_cost(powers[0]):.4f} Rs/MWh")
        output.append("")

        output.append(f"  Plant 2 Generation: {powers[1]:.4f} MW")
        output.append(f"  Plant 2 Cost: {costs[1]:.4f} Rs/hr")
        output.append(f"  Plant 2 Inc. Cost: {plant2.incremental_cost(powers[1]):.4f} Rs/MWh")
        output.append("")

        output.append(f"  Total Cost: {total_cost:.4f} Rs/hr")
        output.append(f"  Feasibility: {'✓ Feasible' if feasible else '✗ Infeasible'}")
        output.append("")

        # Add Example 2.18 specific calculations
        output.append("-" * 80)
        output.append("EXAMPLE 2.18 - DAILY OPERATION ANALYSIS:")
        output.append("-" * 80)
        output.append("")

        # Calculate for 7 MW load
        ed = EconomicDispatch([plant1, plant2])
        powers_7, costs_7, lam_7, feasible_7, total_cost_7 = ed.solve(7)

        output.append("Period 0-6 hrs (Load = 7 MW):")
        output.append(f"  P₁ = {powers_7[0]:.2f} MW, Cost₁ = {costs_7[0]:.2f} Rs/hr")
        output.append(f"  P₂ = {powers_7[1]:.2f} MW, Cost₂ = {costs_7[1]:.2f} Rs/hr")
        output.append(f"  Total Cost = {total_cost_7:.2f} Rs/hr")
        output.append(f"  6-hour Cost = {total_cost_7 * 6:.2f} Rs")

        if powers_7[0] < 0.1:  # Plant 1 essentially off
            output.append(f"  Note: Plant 1 generation too low ({powers_7[0]:.2f} MW < min)")
            output.append(f"        Running Plant 2 only with P₂ = 7 MW")
            cost_2_only = plant2.cost(7)
            output.append(f"        Plant 2 Cost = {cost_2_only:.2f} Rs/hr")
            output.append(f"        6-hour Cost = {cost_2_only * 6:.2f} Rs")

        output.append("")

        # Calculate for 70 MW load
        powers_70, costs_70, lam_70, feasible_70, total_cost_70 = ed.solve(70)

        output.append("Period 18-24 hrs (Load = 70 MW):")
        output.append(f"  P₁ = {powers_70[0]:.2f} MW, Cost₁ = {costs_70[0]:.2f} Rs/hr")
        output.append(f"  P₂ = {powers_70[1]:.2f} MW, Cost₂ = {costs_70[1]:.2f} Rs/hr")
        output.append(f"  Total Cost = {total_cost_70:.2f} Rs/hr")
        output.append(f"  6-hour Cost = {total_cost_70 * 6:.2f} Rs")
        output.append("")

        # Daily totals
        cost_low = plant2.cost(7) if powers_7[0] < 0.1 else total_cost_7
        daily_operating_cost = cost_low * 6 + total_cost_70 * 6
        startup_cost = self.startup_cost_var.get() if powers_7[0] < 0.1 else 0
        total_daily_cost = daily_operating_cost + startup_cost

        output.append("DAILY SUMMARY (assuming same loads for middle 12 hours as 18-24):")
        output.append(f"  Operating Cost: {daily_operating_cost:.2f} Rs")
        output.append(f"  Startup Cost: {startup_cost:.2f} Rs")
        output.append(f"  Total Daily Cost: {total_daily_cost:.2f} Rs")
        output.append("")

        output.append("=" * 80)

        self.results_text.insert(1.0, '\n'.join(output))

    def on_resize(self, event):
        """Handle window resize"""
        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()

    def toggle_simulation(self):
        """Start or stop dynamic simulation"""

        if not self.is_simulating:
            self.is_simulating = True
            self.sim_button.config(text="Stop Simulation")
            self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.simulation_thread.start()
        else:
            self.is_simulating = False
            self.sim_button.config(text="Start Simulation")

    def run_simulation(self):
        """Run dynamic simulation with ODE solver"""

        # Define dynamics: load varies sinusoidally
        # dLoad/dt = amplitude * cos(omega * t)

        def load_derivative(t, y):
            # y[0] is the load
            # Sinusoidal variation: 7 MW at min, 70 MW at max
            amplitude = 31.5  # (70-7)/2
            mean = 38.5  # (70+7)/2
            omega = 2 * np.pi / 24  # 24-hour period

            # Rate of change of load
            dLoad = amplitude * omega * np.cos(omega * t)

            return np.array([dLoad])

        # Initial conditions
        y0 = np.array([7.0])  # Start with 7 MW
        t_span = (0, 24)  # 24 hours
        dt = 0.1  # Time step

        # Choose solver
        solver = ODESolver()
        if self.solver_var.get() == "Euler":
            t, y = solver.euler(load_derivative, y0, t_span, dt)
        else:  # RK45
            t, y = solver.rk45(load_derivative, y0, t_span, dt)

        # Store power generations and costs
        powers1_history = []
        powers2_history = []
        costs1_history = []
        costs2_history = []
        total_costs_history = []
        lambda_history = []

        plant1 = PowerPlant(self.a1_var.get(), self.b1_var.get(), self.c1_var.get(), "Plant 1")
        plant2 = PowerPlant(self.a2_var.get(), self.b2_var.get(), self.c2_var.get(), "Plant 2")
        ed = EconomicDispatch([plant1, plant2])

        # Calculate dispatch for each time point
        for load in y[:, 0]:
            # Ensure load is within reasonable bounds
            load = max(1, min(150, abs(load)))

            powers, costs, lam, feasible, total_cost = ed.solve(load)
            powers1_history.append(powers[0])
            powers2_history.append(powers[1])
            costs1_history.append(costs[0])
            costs2_history.append(costs[1])
            total_costs_history.append(total_cost)
            lambda_history.append(lam)

        # Animate the simulation
        for i in range(len(t)):
            if not self.is_simulating:
                break

            # Update current load
            current_load = y[i, 0]
            self.root.after(0, lambda load=current_load: self.load_var.set(abs(load)))

            # Update plots with history
            self.root.after(0, lambda idx=i: self.update_simulation_plots(
                t[:idx+1], y[:idx+1, 0],
                powers1_history[:idx+1], powers2_history[:idx+1],
                costs1_history[:idx+1], costs2_history[:idx+1],
                total_costs_history[:idx+1], lambda_history[:idx+1]
            ))

            # Sleep based on simulation speed
            time.sleep(0.05 / self.simulation_speed_var.get())

        self.is_simulating = False
        self.root.after(0, lambda: self.sim_button.config(text="Start Simulation"))

    def update_simulation_plots(self, t, loads, powers1, powers2, costs1, costs2, total_costs, lambdas):
        """Update plots during simulation"""

        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()

        # Plot 1: Load variation over time
        self.ax1.plot(t, np.abs(loads), 'g-', linewidth=2)
        self.ax1.set_xlabel('Time (hours)', fontsize=10)
        self.ax1.set_ylabel('Load (MW)', fontsize=10)
        self.ax1.set_title('Load Demand vs Time', fontsize=11, fontweight='bold')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_xlim(0, 24)

        # Plot 2: Power generation over time
        self.ax2.plot(t, powers1, 'b-', label='Plant 1', linewidth=2)
        self.ax2.plot(t, powers2, 'r-', label='Plant 2', linewidth=2)
        self.ax2.set_xlabel('Time (hours)', fontsize=10)
        self.ax2.set_ylabel('Power (MW)', fontsize=10)
        self.ax2.set_title('Power Generation vs Time', fontsize=11, fontweight='bold')
        self.ax2.legend(fontsize=8)
        self.ax2.grid(True, alpha=0.3)
        self.ax2.set_xlim(0, 24)

        # Plot 3: Costs over time
        self.ax3.plot(t, costs1, 'b-', label='Plant 1 Cost', linewidth=2)
        self.ax3.plot(t, costs2, 'r-', label='Plant 2 Cost', linewidth=2)
        self.ax3.plot(t, total_costs, 'g-', label='Total Cost', linewidth=2)
        self.ax3.set_xlabel('Time (hours)', fontsize=10)
        self.ax3.set_ylabel('Cost (Rs/hr)', fontsize=10)
        self.ax3.set_title('Operating Costs vs Time', fontsize=11, fontweight='bold')
        self.ax3.legend(fontsize=8)
        self.ax3.grid(True, alpha=0.3)
        self.ax3.set_xlim(0, 24)

        # Plot 4: Lambda over time
        self.ax4.plot(t, lambdas, 'm-', linewidth=2)
        self.ax4.set_xlabel('Time (hours)', fontsize=10)
        self.ax4.set_ylabel('λ (Rs/MWh)', fontsize=10)
        self.ax4.set_title('Incremental Cost (λ) vs Time', fontsize=11, fontweight='bold')
        self.ax4.grid(True, alpha=0.3)
        self.ax4.set_xlim(0, 24)

        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()

    def reset(self):
        """Reset to default values"""

        self.is_simulating = False

        self.a1_var.set(0.1)
        self.b1_var.set(60)
        self.c1_var.set(135)

        self.a2_var.set(0.15)
        self.b2_var.set(40)
        self.c2_var.set(100)

        self.load_var.set(70)
        self.startup_cost_var.set(450)
        self.simulation_speed_var.set(1.0)

        self.calculate()


def main():
    """Main entry point"""

    root = tk.Tk()
    app = EconomicDispatchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
