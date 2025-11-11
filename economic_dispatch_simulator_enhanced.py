"""
Enhanced Power System Economic Dispatch Simulator
Supports 3 plants, dynamic simulation with RK45/Euler, and automatic window resizing
Solves all review questions and problems
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
    """Enhanced GUI application with 3-plant support"""

    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Economic Dispatch Simulator - 3 Plants")

        # Make window resizable
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)

        # Configure root grid for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Plant parameters (default to Problem 1)
        self.num_plants = tk.IntVar(value=3)

        # Plant 1
        self.a1_var = tk.DoubleVar(value=0.075)  # dC/dP = 0.15P + 30 => C = 0.075P² + 30P
        self.b1_var = tk.DoubleVar(value=30)
        self.c1_var = tk.DoubleVar(value=0)
        self.pmin1_var = tk.DoubleVar(value=25)
        self.pmax1_var = tk.DoubleVar(value=125)

        # Plant 2
        self.a2_var = tk.DoubleVar(value=0.10)  # dC/dP = 0.20P + 40 => C = 0.10P² + 40P
        self.b2_var = tk.DoubleVar(value=40)
        self.c2_var = tk.DoubleVar(value=0)
        self.pmin2_var = tk.DoubleVar(value=30)
        self.pmax2_var = tk.DoubleVar(value=100)

        # Plant 3
        self.a3_var = tk.DoubleVar(value=0.09)  # dC/dP = 0.18P + 15 => C = 0.09P² + 15P
        self.b3_var = tk.DoubleVar(value=15)
        self.c3_var = tk.DoubleVar(value=0)
        self.pmin3_var = tk.DoubleVar(value=50)
        self.pmax3_var = tk.DoubleVar(value=200)

        # System parameters
        self.load_var = tk.DoubleVar(value=300)
        self.solver_var = tk.StringVar(value="RK45")
        self.simulation_speed_var = tk.DoubleVar(value=1.0)

        # Simulation state
        self.is_simulating = False
        self.simulation_thread = None

        # History for dynamic plotting
        self.time_history = []
        self.load_history = []
        self.power1_history = []
        self.power2_history = []
        self.power3_history = []
        self.cost_history = []
        self.lambda_history = []

        # Setup GUI
        self.setup_gui()

        # Initial calculation
        self.calculate()

    def setup_gui(self):
        """Setup the GUI layout with automatic resizing"""

        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure main frame grid weights for resizing
        main_frame.grid_rowconfigure(0, weight=3)  # Visualization area
        main_frame.grid_rowconfigure(1, weight=1)  # Results area
        main_frame.grid_columnconfigure(0, weight=0)  # Control panel (fixed width)
        main_frame.grid_columnconfigure(1, weight=1)  # Visualization (expandable)

        # Left panel - Controls
        self.create_control_panel(main_frame)

        # Right panel - Visualization
        self.create_visualization_panel(main_frame)

        # Bottom panel - Results
        self.create_results_panel(main_frame)

        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)

    def create_control_panel(self, parent):
        """Create scrollable control panel with sliders"""

        # Create frame with scrollbar
        control_outer = ttk.Frame(parent)
        control_outer.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        control_outer.grid_rowconfigure(0, weight=1)
        control_outer.grid_columnconfigure(0, weight=1)

        # Canvas for scrolling
        canvas = tk.Canvas(control_outer, width=350, highlightthickness=0)
        scrollbar = ttk.Scrollbar(control_outer, orient="vertical", command=canvas.yview)

        control_frame = ttk.Frame(canvas)

        canvas.create_window((0, 0), window=control_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Update scroll region when frame changes
        control_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        row = 0

        # Title
        ttk.Label(control_frame, text="Economic Dispatch Control Panel",
                 font=('Arial', 12, 'bold')).grid(row=row, column=0, columnspan=3, pady=10)
        row += 1

        # Number of plants selector
        ttk.Label(control_frame, text="Number of Plants:",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=5)
        plant_combo = ttk.Combobox(control_frame, textvariable=self.num_plants,
                                   values=[2, 3], state="readonly", width=10)
        plant_combo.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=5)
        plant_combo.bind('<<ComboboxSelected>>', lambda e: self.on_num_plants_change())
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Plant 1 parameters
        ttk.Label(control_frame, text="Plant 1 Parameters",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        ttk.Label(control_frame, text="C₁ = a₁P₁² + b₁P₁ + c₁",
                 font=('Arial', 9, 'italic')).grid(row=row, column=0, columnspan=3)
        row += 1

        self.create_slider(control_frame, "a₁:", self.a1_var, 0.01, 0.5, row, resolution=0.001)
        row += 1
        self.create_slider(control_frame, "b₁:", self.b1_var, 0, 100, row)
        row += 1
        self.create_slider(control_frame, "c₁:", self.c1_var, 0, 500, row)
        row += 1
        self.create_slider(control_frame, "P₁ min:", self.pmin1_var, 0, 50, row)
        row += 1
        self.create_slider(control_frame, "P₁ max:", self.pmax1_var, 50, 300, row)
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Plant 2 parameters
        ttk.Label(control_frame, text="Plant 2 Parameters",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        ttk.Label(control_frame, text="C₂ = a₂P₂² + b₂P₂ + c₂",
                 font=('Arial', 9, 'italic')).grid(row=row, column=0, columnspan=3)
        row += 1

        self.create_slider(control_frame, "a₂:", self.a2_var, 0.01, 0.5, row, resolution=0.001)
        row += 1
        self.create_slider(control_frame, "b₂:", self.b2_var, 0, 100, row)
        row += 1
        self.create_slider(control_frame, "c₂:", self.c2_var, 0, 500, row)
        row += 1
        self.create_slider(control_frame, "P₂ min:", self.pmin2_var, 0, 50, row)
        row += 1
        self.create_slider(control_frame, "P₂ max:", self.pmax2_var, 50, 300, row)
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Plant 3 parameters
        ttk.Label(control_frame, text="Plant 3 Parameters",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        ttk.Label(control_frame, text="C₃ = a₃P₃² + b₃P₃ + c₃",
                 font=('Arial', 9, 'italic')).grid(row=row, column=0, columnspan=3)
        row += 1

        self.create_slider(control_frame, "a₃:", self.a3_var, 0.01, 0.5, row, resolution=0.001)
        row += 1
        self.create_slider(control_frame, "b₃:", self.b3_var, 0, 100, row)
        row += 1
        self.create_slider(control_frame, "c₃:", self.c3_var, 0, 500, row)
        row += 1
        self.create_slider(control_frame, "P₃ min:", self.pmin3_var, 0, 100, row)
        row += 1
        self.create_slider(control_frame, "P₃ max:", self.pmax3_var, 100, 400, row)
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # System parameters
        ttk.Label(control_frame, text="System Parameters",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        self.create_slider(control_frame, "Load (MW):", self.load_var, 10, 600, row)
        row += 1

        # ODE Solver selection
        ttk.Label(control_frame, text="ODE Solver:").grid(row=row, column=0, sticky=tk.W, pady=5)
        solver_combo = ttk.Combobox(control_frame, textvariable=self.solver_var,
                                    values=["Euler", "RK45"], state="readonly", width=15)
        solver_combo.grid(row=row, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1

        # Simulation speed
        self.create_slider(control_frame, "Sim Speed:", self.simulation_speed_var, 0.1, 5.0, row)
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="Calculate", command=self.calculate).pack(side=tk.TOP, pady=2, fill=tk.X)
        self.sim_button = ttk.Button(button_frame, text="Start Simulation", command=self.toggle_simulation)
        self.sim_button.pack(side=tk.TOP, pady=2, fill=tk.X)
        ttk.Button(button_frame, text="Reset", command=self.reset).pack(side=tk.TOP, pady=2, fill=tk.X)
        row += 1

        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3,
                                                               sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Problem presets
        ttk.Label(control_frame, text="Problem Presets",
                 font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1

        preset_buttons = [
            ("Problem 1 (3 plants, 300 MW)", self.load_problem1),
            ("Problem 2 (2 plants, 300 MW)", self.load_problem2),
            ("Problem 3 (3 plants, 180 MW)", self.load_problem3),
            ("Problem 4 (2 plants, 210 MW)", self.load_problem4),
        ]

        for text, command in preset_buttons:
            ttk.Button(control_frame, text=text, command=command).grid(
                row=row, column=0, columnspan=3, pady=2, sticky=(tk.W, tk.E))
            row += 1

    def create_slider(self, parent, label, variable, from_, to, row, resolution=0.1):
        """Create a slider with label and value display"""

        ttk.Label(parent, text=label, width=12).grid(row=row, column=0, sticky=tk.W, pady=2)

        slider = ttk.Scale(parent, from_=from_, to=to, orient=tk.HORIZONTAL,
                          variable=variable, command=lambda v: self.on_slider_change(variable))
        slider.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)

        value_label = ttk.Label(parent, text=f"{variable.get():.3f}", width=8)
        value_label.grid(row=row, column=2, sticky=tk.W, pady=2)

        # Store reference to update later
        variable.label = value_label

        # Configure column weights
        parent.grid_columnconfigure(1, weight=1)

    def on_slider_change(self, variable):
        """Update slider value label and recalculate"""
        variable.label.config(text=f"{variable.get():.3f}")
        if not self.is_simulating:
            self.calculate()

    def on_num_plants_change(self):
        """Handle change in number of plants"""
        self.calculate()

    def create_visualization_panel(self, parent):
        """Create visualization panel with dynamic plots"""

        viz_frame = ttk.LabelFrame(parent, text="Visualization", padding="5")
        viz_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        viz_frame.grid_rowconfigure(0, weight=1)
        viz_frame.grid_columnconfigure(0, weight=1)

        # Create matplotlib figure with tight layout
        self.fig = Figure(figsize=(12, 8), dpi=100)
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.08, hspace=0.3, wspace=0.3)

        # Create 2x3 subplot grid
        self.ax1 = self.fig.add_subplot(2, 3, 1)
        self.ax2 = self.fig.add_subplot(2, 3, 2)
        self.ax3 = self.fig.add_subplot(2, 3, 3)
        self.ax4 = self.fig.add_subplot(2, 3, 4)
        self.ax5 = self.fig.add_subplot(2, 3, 5)
        self.ax6 = self.fig.add_subplot(2, 3, 6)

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_results_panel(self, parent):
        """Create results panel"""

        results_frame = ttk.LabelFrame(parent, text="Results", padding="5")
        results_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=12, width=100,
                                                      font=('Courier', 9))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def calculate(self):
        """Calculate economic dispatch and update displays"""

        num_plants = self.num_plants.get()

        # Create power plants
        plant1 = PowerPlant(self.a1_var.get(), self.b1_var.get(), self.c1_var.get(),
                           "Plant 1", self.pmin1_var.get(), self.pmax1_var.get())
        plant2 = PowerPlant(self.a2_var.get(), self.b2_var.get(), self.c2_var.get(),
                           "Plant 2", self.pmin2_var.get(), self.pmax2_var.get())

        plants = [plant1, plant2]

        if num_plants == 3:
            plant3 = PowerPlant(self.a3_var.get(), self.b3_var.get(), self.c3_var.get(),
                               "Plant 3", self.pmin3_var.get(), self.pmax3_var.get())
            plants.append(plant3)

        # Solve economic dispatch
        ed = EconomicDispatch(plants)
        total_load = self.load_var.get()
        powers, costs, lam, feasible, total_cost = ed.solve(total_load)

        # Update plots
        self.update_static_plots(plants, powers, costs, lam, total_load, feasible)

        # Update results text
        self.update_results_text(plants, powers, costs, lam, total_cost, feasible)

    def update_static_plots(self, plants, powers, costs, lam, total_load, feasible):
        """Update static analysis plots"""

        # Clear all axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
            ax.clear()

        n = len(plants)
        colors = ['#3498db', '#e74c3c', '#2ecc71']

        # Plot 1: Cost curves
        P_max = max(plant.Pmax for plant in plants)
        P_range = np.linspace(0, P_max, 300)

        for i, plant in enumerate(plants):
            P_plot = np.linspace(plant.Pmin, plant.Pmax, 100)
            C = [plant.cost(P) for P in P_plot]
            self.ax1.plot(P_plot, C, color=colors[i], label=f'{plant.name}', linewidth=2)
            self.ax1.axvline(powers[i], color=colors[i], linestyle='--', alpha=0.5)

        self.ax1.set_xlabel('Power (MW)', fontsize=9)
        self.ax1.set_ylabel('Cost (Rs/hr)', fontsize=9)
        self.ax1.set_title('Cost Curves', fontsize=10, fontweight='bold')
        self.ax1.legend(fontsize=8)
        self.ax1.grid(True, alpha=0.3)

        # Plot 2: Incremental cost curves
        for i, plant in enumerate(plants):
            P_plot = np.linspace(plant.Pmin, plant.Pmax, 100)
            IC = [plant.incremental_cost(P) for P in P_plot]
            self.ax2.plot(P_plot, IC, color=colors[i], label=f'dC{i+1}/dP{i+1}', linewidth=2)
            self.ax2.axvline(powers[i], color=colors[i], linestyle=':', alpha=0.5)

        self.ax2.axhline(lam, color='purple', linestyle='--', linewidth=2, label=f'λ={lam:.2f}')
        self.ax2.set_xlabel('Power (MW)', fontsize=9)
        self.ax2.set_ylabel('Inc. Cost (Rs/MWh)', fontsize=9)
        self.ax2.set_title('Incremental Cost Curves', fontsize=10, fontweight='bold')
        self.ax2.legend(fontsize=7)
        self.ax2.grid(True, alpha=0.3)

        # Plot 3: Power allocation pie chart
        labels = [f'{plant.name}\n{powers[i]:.1f} MW' for i, plant in enumerate(plants)]
        self.ax3.pie(powers, labels=labels, autopct='%1.1f%%',
                    colors=colors[:n], startangle=90)
        self.ax3.set_title(f'Power Allocation\nTotal: {total_load:.1f} MW\nFeasible: {"Yes" if feasible else "No"}',
                          fontsize=10, fontweight='bold')

        # Plot 4: Cost breakdown
        plant_names = [f'P{i+1}' for i in range(n)] + ['Total']
        cost_values = costs + [sum(costs)]
        bars = self.ax4.bar(plant_names, cost_values, color=colors[:n] + ['purple'],
                           alpha=0.7, edgecolor='black')
        self.ax4.set_ylabel('Cost (Rs/hr)', fontsize=9)
        self.ax4.set_title('Cost Breakdown', fontsize=10, fontweight='bold')
        self.ax4.grid(True, alpha=0.3, axis='y')

        # Add value labels on bars
        for bar, value in zip(bars, cost_values):
            height = bar.get_height()
            self.ax4.text(bar.get_x() + bar.get_width()/2., height,
                         f'{value:.1f}', ha='center', va='bottom', fontsize=8)

        # Plot 5: Power generation bar chart
        plant_names = [f'P{i+1}' for i in range(n)]
        bars = self.ax5.bar(plant_names, powers, color=colors[:n], alpha=0.7, edgecolor='black')

        # Add constraint lines
        for i, plant in enumerate(plants):
            self.ax5.plot([i-0.3, i+0.3], [plant.Pmin, plant.Pmin], 'k--', linewidth=1, alpha=0.5)
            self.ax5.plot([i-0.3, i+0.3], [plant.Pmax, plant.Pmax], 'k--', linewidth=1, alpha=0.5)

        self.ax5.set_ylabel('Power (MW)', fontsize=9)
        self.ax5.set_title('Power Generation vs Constraints', fontsize=10, fontweight='bold')
        self.ax5.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, value in zip(bars, powers):
            height = bar.get_height()
            self.ax5.text(bar.get_x() + bar.get_width()/2., height,
                         f'{value:.1f}', ha='center', va='bottom', fontsize=8)

        # Plot 6: Incremental costs at operating points
        plant_names = [f'P{i+1}' for i in range(n)]
        inc_costs = [plant.incremental_cost(P) for plant, P in zip(plants, powers)]
        bars = self.ax6.bar(plant_names, inc_costs, color=colors[:n], alpha=0.7, edgecolor='black')
        self.ax6.axhline(lam, color='purple', linestyle='--', linewidth=2, label=f'λ={lam:.2f}')
        self.ax6.set_ylabel('Inc. Cost (Rs/MWh)', fontsize=9)
        self.ax6.set_title('Incremental Costs at Operating Points', fontsize=10, fontweight='bold')
        self.ax6.legend(fontsize=8)
        self.ax6.grid(True, alpha=0.3, axis='y')

        # Add value labels
        for bar, value in zip(bars, inc_costs):
            height = bar.get_height()
            self.ax6.text(bar.get_x() + bar.get_width()/2., height,
                         f'{value:.2f}', ha='center', va='bottom', fontsize=8)

        self.canvas.draw_idle()

    def update_results_text(self, plants, powers, costs, lam, total_cost, feasible):
        """Update results text area"""

        self.results_text.delete(1.0, tk.END)

        output = []
        output.append("=" * 100)
        output.append("ECONOMIC DISPATCH RESULTS")
        output.append("=" * 100)
        output.append("")

        output.append("PLANT PARAMETERS:")
        for i, plant in enumerate(plants):
            output.append(f"  {plant.name}: C{i+1} = {plant.a:.4f}P{i+1}² + {plant.b:.4f}P{i+1} + {plant.c:.4f}")
            output.append(f"             Constraints: {plant.Pmin:.1f} ≤ P{i+1} ≤ {plant.Pmax:.1f} MW")
        output.append("")

        output.append("INCREMENTAL COSTS:")
        for i, plant in enumerate(plants):
            output.append(f"  dC{i+1}/dP{i+1} = {2*plant.a:.4f}P{i+1} + {plant.b:.4f}")
        output.append("")

        output.append("OPTIMAL DISPATCH:")
        output.append(f"  Total Load Demand: {self.load_var.get():.2f} MW")
        output.append(f"  Lambda (λ): {lam:.4f} Rs/MWh")
        output.append(f"  Feasibility: {'✓ FEASIBLE' if feasible else '✗ INFEASIBLE'}")
        output.append("")

        for i, plant in enumerate(plants):
            output.append(f"  {plant.name}:")
            output.append(f"    Generation: {powers[i]:.4f} MW")
            output.append(f"    Cost: {costs[i]:.4f} Rs/hr")
            output.append(f"    Incremental Cost: {plant.incremental_cost(powers[i]):.4f} Rs/MWh")

            # Check if within constraints
            if powers[i] < plant.Pmin - 0.01:
                output.append(f"    ⚠ WARNING: Below minimum ({plant.Pmin} MW)")
            elif powers[i] > plant.Pmax + 0.01:
                output.append(f"    ⚠ WARNING: Above maximum ({plant.Pmax} MW)")
            output.append("")

        output.append(f"  TOTAL COST: {total_cost:.4f} Rs/hr")
        output.append("")

        # Power balance check
        total_gen = sum(powers)
        output.append(f"  Total Generation: {total_gen:.4f} MW")
        output.append(f"  Power Balance Error: {abs(total_gen - self.load_var.get()):.6f} MW")
        output.append("")

        output.append("=" * 100)

        self.results_text.insert(1.0, '\n'.join(output))

    def on_window_resize(self, event):
        """Handle window resize event"""
        # Only redraw if the window itself was resized, not child widgets
        if event.widget == self.root:
            self.canvas.draw_idle()

    def toggle_simulation(self):
        """Start or stop dynamic simulation"""

        if not self.is_simulating:
            self.is_simulating = True
            self.sim_button.config(text="Stop Simulation")

            # Clear history
            self.time_history.clear()
            self.load_history.clear()
            self.power1_history.clear()
            self.power2_history.clear()
            self.power3_history.clear()
            self.cost_history.clear()
            self.lambda_history.clear()

            self.simulation_thread = threading.Thread(target=self.run_simulation, daemon=True)
            self.simulation_thread.start()
        else:
            self.is_simulating = False
            self.sim_button.config(text="Start Simulation")

    def run_simulation(self):
        """Run dynamic simulation with ODE solver"""

        # Define load variation dynamics
        def load_derivative(t, y):
            # Sinusoidal load variation over 24 hours
            load_min = 100
            load_max = 400
            amplitude = (load_max - load_min) / 2
            mean = (load_max + load_min) / 2
            omega = 2 * np.pi / 24  # 24-hour period

            dLoad = amplitude * omega * np.cos(omega * t)
            return np.array([dLoad])

        # Initial conditions
        y0 = np.array([100.0])  # Start with minimum load
        t_span = (0, 24)  # 24 hours
        dt = 0.1

        # Choose solver
        solver = ODESolver()
        if self.solver_var.get() == "Euler":
            t, y = solver.euler(load_derivative, y0, t_span, dt)
        else:  # RK45
            t, y = solver.rk45(load_derivative, y0, t_span, dt)

        # Get current plant configuration
        num_plants = self.num_plants.get()
        plant1 = PowerPlant(self.a1_var.get(), self.b1_var.get(), self.c1_var.get(),
                           "Plant 1", self.pmin1_var.get(), self.pmax1_var.get())
        plant2 = PowerPlant(self.a2_var.get(), self.b2_var.get(), self.c2_var.get(),
                           "Plant 2", self.pmin2_var.get(), self.pmax2_var.get())

        plants = [plant1, plant2]

        if num_plants == 3:
            plant3 = PowerPlant(self.a3_var.get(), self.b3_var.get(), self.c3_var.get(),
                               "Plant 3", self.pmin3_var.get(), self.pmax3_var.get())
            plants.append(plant3)

        ed = EconomicDispatch(plants)

        # Animate the simulation
        for i in range(len(t)):
            if not self.is_simulating:
                break

            current_load = abs(y[i, 0])

            # Solve dispatch for current load
            powers, costs, lam, feasible, total_cost = ed.solve(current_load)

            # Store history
            self.time_history.append(t[i])
            self.load_history.append(current_load)
            self.power1_history.append(powers[0])
            self.power2_history.append(powers[1] if len(powers) > 1 else 0)
            self.power3_history.append(powers[2] if len(powers) > 2 else 0)
            self.cost_history.append(total_cost)
            self.lambda_history.append(lam)

            # Update GUI
            self.root.after(0, lambda: self.load_var.set(current_load))
            self.root.after(0, lambda: self.update_dynamic_plots())

            # Sleep based on simulation speed
            time.sleep(0.05 / self.simulation_speed_var.get())

        self.is_simulating = False
        self.root.after(0, lambda: self.sim_button.config(text="Start Simulation"))

    def update_dynamic_plots(self):
        """Update plots during dynamic simulation"""

        if len(self.time_history) < 2:
            return

        # Clear axes
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6]:
            ax.clear()

        t = self.time_history

        # Plot 1: Load vs Time
        self.ax1.plot(t, self.load_history, 'g-', linewidth=2, label='Load Demand')
        self.ax1.set_xlabel('Time (hours)', fontsize=9)
        self.ax1.set_ylabel('Load (MW)', fontsize=9)
        self.ax1.set_title('Load Demand vs Time', fontsize=10, fontweight='bold')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_xlim(0, 24)
        self.ax1.legend(fontsize=8)

        # Plot 2: Power Generation vs Time
        self.ax2.plot(t, self.power1_history, 'b-', linewidth=2, label='Plant 1')
        self.ax2.plot(t, self.power2_history, 'r-', linewidth=2, label='Plant 2')
        if self.num_plants.get() == 3:
            self.ax2.plot(t, self.power3_history, 'g-', linewidth=2, label='Plant 3')
        self.ax2.set_xlabel('Time (hours)', fontsize=9)
        self.ax2.set_ylabel('Power (MW)', fontsize=9)
        self.ax2.set_title('Power Generation vs Time', fontsize=10, fontweight='bold')
        self.ax2.legend(fontsize=8)
        self.ax2.grid(True, alpha=0.3)
        self.ax2.set_xlim(0, 24)

        # Plot 3: Total Cost vs Time
        self.ax3.plot(t, self.cost_history, 'm-', linewidth=2, label='Total Cost')
        self.ax3.set_xlabel('Time (hours)', fontsize=9)
        self.ax3.set_ylabel('Cost (Rs/hr)', fontsize=9)
        self.ax3.set_title('Total Operating Cost vs Time', fontsize=10, fontweight='bold')
        self.ax3.grid(True, alpha=0.3)
        self.ax3.set_xlim(0, 24)
        self.ax3.legend(fontsize=8)

        # Plot 4: Lambda vs Time
        self.ax4.plot(t, self.lambda_history, 'purple', linewidth=2, label='λ')
        self.ax4.set_xlabel('Time (hours)', fontsize=9)
        self.ax4.set_ylabel('λ (Rs/MWh)', fontsize=9)
        self.ax4.set_title('Incremental Cost (λ) vs Time', fontsize=10, fontweight='bold')
        self.ax4.grid(True, alpha=0.3)
        self.ax4.set_xlim(0, 24)
        self.ax4.legend(fontsize=8)

        # Plot 5: Power Distribution (Stacked Area)
        if self.num_plants.get() == 3:
            self.ax5.fill_between(t, 0, self.power1_history, alpha=0.5, color='b', label='Plant 1')
            p1_array = np.array(self.power1_history)
            p2_array = np.array(self.power2_history)
            self.ax5.fill_between(t, p1_array, p1_array + p2_array, alpha=0.5, color='r', label='Plant 2')
            self.ax5.fill_between(t, p1_array + p2_array,
                                 p1_array + p2_array + np.array(self.power3_history),
                                 alpha=0.5, color='g', label='Plant 3')
        else:
            self.ax5.fill_between(t, 0, self.power1_history, alpha=0.5, color='b', label='Plant 1')
            self.ax5.fill_between(t, self.power1_history,
                                 np.array(self.power1_history) + np.array(self.power2_history),
                                 alpha=0.5, color='r', label='Plant 2')

        self.ax5.set_xlabel('Time (hours)', fontsize=9)
        self.ax5.set_ylabel('Power (MW)', fontsize=9)
        self.ax5.set_title('Stacked Power Generation', fontsize=10, fontweight='bold')
        self.ax5.legend(fontsize=8)
        self.ax5.grid(True, alpha=0.3)
        self.ax5.set_xlim(0, 24)

        # Plot 6: Cumulative Cost
        if len(t) > 1:
            cumulative_cost = np.cumsum(np.array(self.cost_history) * np.gradient(t))
            self.ax6.plot(t, cumulative_cost, 'orange', linewidth=2, label='Cumulative Cost')
            self.ax6.set_xlabel('Time (hours)', fontsize=9)
            self.ax6.set_ylabel('Cumulative Cost (Rs)', fontsize=9)
            self.ax6.set_title('Cumulative Operating Cost', fontsize=10, fontweight='bold')
            self.ax6.grid(True, alpha=0.3)
            self.ax6.set_xlim(0, 24)
            self.ax6.legend(fontsize=8)

        self.canvas.draw_idle()

    def load_problem1(self):
        """Load Problem 1: Three plants, 300 MW"""
        self.num_plants.set(3)

        # dC1/dP1 = 30 + 0.15*P1  => C1 = 0.075*P1² + 30*P1
        self.a1_var.set(0.075)
        self.b1_var.set(30)
        self.c1_var.set(0)
        self.pmin1_var.set(25)
        self.pmax1_var.set(125)

        # dC2/dP2 = 40 + 0.20*P2  => C2 = 0.10*P2² + 40*P2
        self.a2_var.set(0.10)
        self.b2_var.set(40)
        self.c2_var.set(0)
        self.pmin2_var.set(30)
        self.pmax2_var.set(100)

        # dC3/dP3 = 15 + 0.18*P3  => C3 = 0.09*P3² + 15*P3
        self.a3_var.set(0.09)
        self.b3_var.set(15)
        self.c3_var.set(0)
        self.pmin3_var.set(50)
        self.pmax3_var.set(200)

        self.load_var.set(300)
        self.calculate()

    def load_problem2(self):
        """Load Problem 2: Two plants, 300 MW"""
        self.num_plants.set(2)

        # dC1/dP1 = 0.15*P1 + 30  => C1 = 0.075*P1² + 30*P1
        self.a1_var.set(0.075)
        self.b1_var.set(30)
        self.c1_var.set(0)
        self.pmin1_var.set(0)
        self.pmax1_var.set(300)

        # dC2/dP2 = 0.25*P2 + 20  => C2 = 0.125*P2² + 20*P2
        self.a2_var.set(0.125)
        self.b2_var.set(20)
        self.c2_var.set(0)
        self.pmin2_var.set(0)
        self.pmax2_var.set(300)

        self.load_var.set(300)
        self.calculate()

    def load_problem3(self):
        """Load Problem 3: Three plants with quadratic costs, 180 MW"""
        self.num_plants.set(3)

        # C1 = 0.04*P1² + 20*P1 + 230
        self.a1_var.set(0.04)
        self.b1_var.set(20)
        self.c1_var.set(230)
        self.pmin1_var.set(0)
        self.pmax1_var.set(200)

        # C2 = 0.06*P2² + 18*P2 + 200
        self.a2_var.set(0.06)
        self.b2_var.set(18)
        self.c2_var.set(200)
        self.pmin2_var.set(0)
        self.pmax2_var.set(200)

        # C3 = 0.15*P3² + 15*P3 + 180
        self.a3_var.set(0.15)
        self.b3_var.set(15)
        self.c3_var.set(180)
        self.pmin3_var.set(0)
        self.pmax3_var.set(200)

        self.load_var.set(180)
        self.calculate()

    def load_problem4(self):
        """Load Problem 4: Two plants, 210 MW"""
        self.num_plants.set(2)

        # dC1/dP1 = 0.15*P1 + 50  => C1 = 0.075*P1² + 50*P1
        self.a1_var.set(0.075)
        self.b1_var.set(50)
        self.c1_var.set(0)
        self.pmin1_var.set(0)
        self.pmax1_var.set(210)

        # dC2/dP2 = 0.2*P2 + 40  => C2 = 0.10*P2² + 40*P2
        self.a2_var.set(0.10)
        self.b2_var.set(40)
        self.c2_var.set(0)
        self.pmin2_var.set(0)
        self.pmax2_var.set(210)

        self.load_var.set(210)
        self.calculate()

    def reset(self):
        """Reset to Problem 1 defaults"""
        self.is_simulating = False
        self.load_problem1()
        self.simulation_speed_var.set(1.0)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = EconomicDispatchGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
