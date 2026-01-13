PyCORE
PyCORE is a Python package for simulating groundwater flow and reactive transport in porous media. It provides a flexible and extensible framework for modeling hydraulic head, solute transport, chemical reactions, ion exchange, and mineral reactions in 1D and 2D domains.

Features
Simulation of groundwater flow (confined flow, Darcy velocity, hydraulic head)
Reactive transport (solute transport, chemical reactions, ion exchange, mineral reactions)
Flexible input: Accepts data as Python dictionaries or DataFrames
Customizable chemical solver: Users can inject their own chemical equilibrium solver
Output and plotting: Built-in methods for exporting and visualizing results
Installation
Usage
Main Class: Simulation
Initialization
tran_input: Transport input data (dict)
chem_input: Chemistry input data (dict)
database_path: Path to the chemical database (str)
pecl, cour: Optional lists for Peclet and Courant numbers
chemical_equilibrium_callback: Optional user-defined function for chemical equilibrium
Key Methods
run(): Run the main simulation loop
plot_h_x(time, dimension): Plot hydraulic head distribution
plot_u_x(time, dimension, components): Plot concentration of selected components
write_hxt(file_name, dimension): Write hydraulic head data to file
write_totC(file_name, dimension): Write total primary species concentrations to file
set_chemical_equilibrium_callback(callback_fn): Set a custom chemical equilibrium solver