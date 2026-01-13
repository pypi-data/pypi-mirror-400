import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .grids.grid import Nodes, Elements
from .waterflow.confinedflow import SatFlow
from .chemicalsystem.chemicalsystem import ChemicalSystem
from .solutetransport.solutetransport import SoluteTransport


class Simulation:
    """
    Main simulation class for PyRetraS.
    Handles initialization, running, and output/plotting of groundwater flow and reactive transport simulations.
    """

    def __init__(
        self,
        tran_input,
        chem_input,
        database_path,
        pecl=None,
        cour=None,
        chemical_equilibrium_callback=None,
    ):
        """
        Initialize the Simulation object with all required input data and parameters.

        Parameters:
            tran_input (dict): Transport input data.
            chem_input (dict): Chemistry input data.
            database_path (str): Path to the chemical database.
            pecl (list, optional): Peclet numbers (default: empty list).
            cour (list, optional): Courant numbers (default: empty list).
            chemical_equilibrium_callback (callable, optional): User-defined callback for chemical equilibrium solving.
        """
        self.tran_input = tran_input
        self.chem_input = chem_input
        self.database_path = database_path
        self.elements_df = tran_input.get("data to elements", -1)
        self.nodes_df = tran_input.get("data to nodes", -1)
        self.nodes = Nodes(self.nodes_df)
        self.elements = Elements(self.nodes_df, self.elements_df)
        self.aqu_parameters = tran_input.get("aquifer parameters", -1)
        self.converge_tolerance = tran_input.get("data to convergence criteria", -1)
        self.flow_controls = tran_input.get(
            "flow and transport and general controls", -1
        )
        self.chemical_calc_controls = tran_input.get(
            "chemical calculation controls", -1
        )
        self.boundary_functions = tran_input.get("piecewise functions", -1)
        self.nboundfc = self.boundary_functions["numberBoundFunction"].loc[
            "val", "nboundfc"
        ]
        self.nboundfh = self.boundary_functions["numberBoundFunction"].loc[
            "val", "nboundfh"
        ]
        self.gflw = np.zeros((self.nodes.nnod, self.nodes.nnod))
        self.pflw = np.zeros((self.nodes.nnod, self.nodes.nnod))
        self.bflw = np.zeros(self.nodes.nnod)
        self.timesteps = tran_input["time steps"]
        self.confined_flow = SatFlow(
            self.nodes_df,
            self.elements_df,
            self.aqu_parameters,
            self.converge_tolerance,
            self.flow_controls,
            self.boundary_functions,
            self.gflw,
            self.pflw,
            self.bflw,
        )

        # Chemistry initialization
        self.water_chemistry = ChemicalSystem(
            self.nodes_df, self.elements_df, self.chem_input, self.database_path
        )

        if chemical_equilibrium_callback is not None:
            self.water_chemistry.chemical_equilibrium_callback = (
                chemical_equilibrium_callback
            )

        self.hxt = {
            "xx": self.nodes.xx,
            "y": self.nodes.y,
            "time_0": self.confined_flow.h0.copy(),
        }
        self.spt = {
            "xx": self.nodes.xx,
            "y": self.nodes.y,
            "time_0": self.water_chemistry.u.copy(),
        }
        self.cpt = {
            "xx": self.nodes.xx,
            "y": self.nodes.y,
            "time_0": self.water_chemistry.c.copy(),
        }
        self.xchanger = {
            "xx": self.nodes.xx,
            "y": self.nodes.y,
            "time_0": self.water_chemistry.x.copy(),
        }
        self.mineral_amount = {
            "xx": self.nodes.xx,
            "y": self.nodes.y,
            "time_0": self.water_chemistry.p.copy(),
        }
        self.solute_transport = SoluteTransport(
            self.nodes_df,
            self.elements_df,
            self.aqu_parameters,
            self.converge_tolerance,
            self.flow_controls,
            self.boundary_functions,
        )
        self.pecl = [] if pecl is None else pecl
        self.cour = [] if cour is None else cour

    def set_chemical_equilibrium_callback(self, callback_fn):
        """
        Set a user-defined callback for chemical equilibrium solving.
        """
        self.water_chemistry.chemical_equilibrium_callback = callback_fn

    def show_info(self):
        """
        Print all attributes and methods of the Simulation object for introspection.
        """
        print("Attributes:")
        for attr in dir(self):
            if not attr.startswith("__") and not callable(getattr(self, attr)):
                print(f"  {attr}")
        print("\nMethods:")
        for method in dir(self):
            if not method.startswith("__") and callable(getattr(self, method)):
                print(f"  {method}")

    def __repr__(self):
        """
        Return a string representation of the Simulation object.
        """
        return f"Simulation(attributes={vars(self)})"

    def __dir__(self):
        """
        Return a list of attributes and methods for introspection.
        """
        return sorted(
            attr
            for attr in set(dir(type(self))) | set(self.__dict__.keys())
            if not attr.startswith("__")
        )

    def run(self):
        """
        Run the main simulation loop for groundwater flow and reactive transport.
        Updates hydraulic head, solute concentrations, exchanger, and mineral amounts over time.
        """

        ### processing transport and flow initialization
        ## initializing the class for saturated flow
        caudal = np.zeros(self.nodes.nnod)
        vd = np.zeros((self.elements.nele, 2))
        ptra = np.zeros(self.nodes.nnod)
        gtra = np.zeros((self.nodes.nnod, self.nodes.nnod))
        btras = np.zeros((self.nodes.nnod, self.water_chemistry.npri))
        ub = self.water_chemistry.ub.copy()
        ubv = self.water_chemistry.ubv.copy()
        iub = self.water_chemistry.iub.copy()
        ur = self.water_chemistry.ur.copy()
        urv = self.water_chemistry.urv.copy()
        iur = self.water_chemistry.iur.copy()
        u = self.water_chemistry.u.copy()
        # outdir = r'E:\projects\coreDevp\src\verifications\adsorption\pycore'
        it = 0
        time = 0.0
        # Removed unused os.path.join usages
        h = self.confined_flow.h0.copy()

        for itime, timerow in self.timesteps.iterrows():

            dt = timerow["timeint"] / timerow["nstep"]
            for istep in range(int(timerow["nstep"])):
                time += dt
                it += 1
                print(f"Step {it}, substep {istep}")

                # solve flow equation
                if self.confined_flow.ioflu != 0 or it == 1:

                    if (
                        self.nboundfh > 0
                        and self.confined_flow.ioflu == 1
                        and istep == 0
                    ):
                        self.confined_flow.update_boundh(itime)
                    if (self.nboundfh > 0 and istep == 0) or it == 1:
                        self.confined_flow.area_recharge()

                    if self.confined_flow.iotpa in (0, 1):
                        self.confined_flow.set_h0(h)
                        h = self.confined_flow.flow_sat(it, dt, istep)
                        self.confined_flow.set_h(h)
                    timekey = f"time_{time:10.4e}"
                    self.hxt[timekey] = h.copy()

                # calculate velocity and nodal flux from boundary and point recharge
                if self.confined_flow.ioflu != 0 or it == 1:
                    vd, caudal = self.solute_transport.calc_darcy_velocity(
                        self.confined_flow.q1, self.confined_flow.hp, h
                    )

                # calculate dispersion coefficient
                if self.confined_flow.ioflu != 0 or it == 1:
                    self.solute_transport.calc_dispersivity(vd)

                if (
                    self.confined_flow.ioflu != 0
                    or it == 1
                    or (self.nboundfc > 0 and istep == 0)
                ):
                    ptra, gtra = self.solute_transport.proc_solute_transport_matrix(vd)
                    # check peclect and courant numbers
                    pecl, cour = self.solute_transport.calc_peclect_courant(vd, dt)
                    self.pecl.append([time, pecl])
                    self.cour.append([time, cour])

                if self.nboundfc > 0 and istep == 0:
                    ub, ur = self.solute_transport.update_boundc(
                        self.water_chemistry.nbwtype,
                        self.water_chemistry.nrwtype,
                        itime,
                        ubv,
                        urv,
                        iub,
                        iur,
                    )

                if (
                    self.confined_flow.ioflu != 0
                    or it == 1
                    or (self.nboundfc > 0 and istep == 0)
                ):
                    gtra, btras = self.solute_transport.solute_matrix_boundary(
                        gtra, self.confined_flow.q2, caudal, ub, ur
                    )

                # count initial conditions and sink and source terms of solute transport
                gptflw, btras1, w = self.solute_transport.decompose_transport_matrix(
                    dt, gtra, ptra, btras, u
                )
                ## Looks like w has an issue. will check later
                # solve solute transport equations coupled with reactions
                self.water_chemistry.update_u0(u)
                self.water_chemistry.calc_transport_chem(
                    dt,
                    ptra,
                    btras1,
                    gptflw,
                    w,
                    self.flow_controls,
                    self.chemical_calc_controls,
                    self.converge_tolerance,
                )

                # u = solute_transport.calc_transport(dt, ptra, btras1, gptflw, w)
                u = self.water_chemistry.utem.copy()
                self.water_chemistry.u = self.water_chemistry.utem.copy()
                timekey = f"time_{time:10.4e}"
                self.spt[timekey] = u.copy()
                self.cpt[timekey] = self.water_chemistry.c.copy()
                if self.water_chemistry.nexc > 0:
                    self.xchanger[timekey] = self.water_chemistry.x.copy()
                if self.water_chemistry.nmin > 0:
                    self.mineral_amount[timekey] = self.water_chemistry.p.copy()

    def plot_h_x(self, time, dimension="2D"):
        """
        Plot hydraulic head distribution at a given time.

        Parameters:
            time (float): Simulation time to plot.
            dimension (str): '2D' for contour plot, '1D' for line plot.
        """
        timekey = f"time_{time:10.4e}"
        h = self.hxt.get(timekey, None)
        if h is None:
            print(f"No data found for time {time}")
            return
        plt.figure()
        if dimension == "2D":
            plt.tricontourf(self.nodes.xx, self.nodes.y, h, levels=14, cmap="viridis")
            plt.colorbar(label="Hydraulic Head (h)")
            plt.ylabel("Y")
        elif dimension == "1D":
            x = self.nodes.xx[::2]
            h = h[::2]
            plt.plot(x, h, linestyle="-", marker="None")
            plt.ylabel("Hydraulic Head (h)")
        plt.title(f"Hydraulic Head Distribution at time {time}")
        plt.xlabel("X")
        plt.show()

    def write_hxt(self, file_name, dimension="2D"):
        """
        Write hydraulic head data to a file for all time steps.

        Parameters:
            file_name (str): Output file name.
            dimension (str): '2D' or '1D' output format.
        """

        times = [item for item in self.hxt.keys() if item not in ("xx", "y")]

        with open(file_name, "w", encoding="utf-8") as f:
            for timekey in times:
                f.write(timekey + "\n")
                header = "X,Y,h\n"
                f.write(header)
                if dimension == "2D":
                    for i in range(self.nodes.nnod):
                        line = f"{self.nodes.xx[i]},{self.nodes.y[i]},{self.hxt[timekey][i]:.4e}\n"
                        f.write(line)
                elif dimension == "1D":
                    for i in range(0, self.nodes.nnod, 2):  # Example: every second node
                        line = f"{self.nodes.xx[i]},{self.nodes.y[i]},{self.hxt[timekey][i]:.4e}\n"
                        f.write(line)

    def plot_h_t(self, x, y):
        """
        Plot hydraulic head at a specific (x, y) point over time.

        Parameters:
            x (float): X coordinate.
            y (float): Y coordinate.
        """

        xx = self.nodes.xx
        yy = self.nodes.y
        point = np.array([x, y])
        points = np.column_stack((xx, yy))
        distances = np.linalg.norm(points - point, axis=1)
        idx = np.argmin(distances)
        for timekey in self.hxt.keys():
            if timekey == "xx" or timekey == "y":
                continue
            h = self.hxt[timekey]
            plt.plot(float(timekey.split("_")[1]), h[idx], marker="o", color="b")
        plt.title(f"Hydraulic Head Distribution at point ({x}, {y}) over time")
        plt.xlabel("Time")
        plt.ylabel("Hydraulic Head (h)")
        plt.show()

    def write_totC(self, file_name, dimension="2D"):
        """
        Write total primary species concentrations to a file for all time steps.

        Parameters:
            file_name (str): Output file name.
            dimension (str): '2D' or '1D' output format.
        """

        times = [item for item in self.spt.keys() if item not in ("xx", "y")]
        name_primary_species = self.water_chemistry.name_primary_species

        with open(file_name, "w", encoding="utf-8") as f:
            for timekey in times:
                f.write(timekey + "\n")
                header = (
                    "X,Y,"
                    + ",".join([f"{name}" for name in name_primary_species])
                    + "\n"
                )
                f.write(header)
                if dimension == "2D":
                    for i in range(self.nodes.nnod):
                        line = f"{self.nodes.xx[i]},{self.nodes.y[i]},"
                        u0 = self.spt[timekey][i]
                        line += ",".join([f"{con:.4e}" for con in u0])
                        line += "\n"
                        f.write(line)
                elif dimension == "1D":
                    for i in range(0, self.nodes.nnod, 2):  # Example: every second node
                        line = f"{self.nodes.xx[i]},{self.nodes.y[i]},"
                        u0 = self.spt[timekey][i]
                        line += ",".join([f"{con:.4e}" for con in u0])
                        line += "\n"
                        f.write(line)

    def write_cpt(self, file_name, dimension="2D"):
        """
        Write all species (primary + aqueous complexes) concentrations to a file for all time steps.

        Parameters:
            file_name (str): Output file name.
            dimension (str): '2D' or '1D' output format.
        """

        times = [item for item in self.spt.keys() if item not in ("xx", "y")]
        name_species = (
            self.water_chemistry.name_primary_species
            + self.water_chemistry.name_aqu_complexes
        )

        with open(file_name, "w", encoding="utf-8") as f:
            for timekey in times:
                f.write(timekey + "\n")
                header = "X,Y," + ",".join([f"{name}" for name in name_species]) + "\n"
                f.write(header)
                if dimension == "2D":
                    for i in range(self.nodes.nnod):
                        line = f"{self.nodes.xx[i]},{self.nodes.y[i]},"
                        u0 = self.cpt[timekey][i]
                        line += ",".join([f"{con:.4e}" for con in u0])
                        line += "\n"
                        f.write(line)
                elif dimension == "1D":
                    for i in range(0, self.nodes.nnod, 2):  # Example: every second node
                        line = f"{self.nodes.xx[i]},{self.nodes.y[i]},"
                        u0 = self.cpt[timekey][i]
                        line += ",".join([f"{con:.4e}" for con in u0])
                        line += "\n"
                        f.write(line)

    def write_xchanger(self, file_name, dimension="2D"):
        """
        Write exchanger concentrations and CEC to a file for all time steps.

        Parameters:
            file_name (str): Output file name.
            dimension (str): '2D' or '1D' output format.
        """

        times = [item for item in self.xchanger.keys() if item not in ("xx", "y")]
        name_exchangers = self.water_chemistry.name_exchangers

        nbx = self.water_chemistry.nbx
        z = self.water_chemistry.z
        por = self.water_chemistry.porosity.copy()
        nexc = self.water_chemistry.nexc
        with open(file_name, "w", encoding="utf-8") as f:
            for timekey in times:
                f.write(timekey + "\n")
                header = (
                    "X,Y,"
                    + ",".join([f"{name}" for name in name_exchangers])
                    + ", CEC \n"
                )
                f.write(header)
                if dimension == "2D":
                    for i in range(self.nodes.nnod):
                        line = f"{self.nodes.xx[i]},{self.nodes.y[i]},"
                        x0 = self.xchanger[timekey][i]
                        exchme = np.zeros(nexc)
                        cec_calc = 0.0
                        for j in range(nexc):
                            exchme[j] = x0[j] * por[i] * 100.0 / ((1 - por[i]) * 2.65)
                            if self.water_chemistry.iex != 2:
                                exchme[j] = exchme[j] * z[nbx[j]]
                        cec_calc = sum(exchme)

                        line += ",".join([f"{amt:.4e}" for amt in exchme])
                        line += f" ,{cec_calc:.4e}"
                        line += "\n"
                        f.write(line)
                elif dimension == "1D":
                    for i in range(0, self.nodes.nnod, 2):  # Example: every second node
                        line = f"{i+1},{self.nodes.xx[i]},{self.nodes.y[i]},"
                        x0 = self.xchanger[timekey][i]
                        exchme = np.zeros(nexc)
                        cec_calc = 0.0
                        for j in range(nexc):
                            exchme[j] = x0[j] * por[i] * 100.0 / ((1 - por[i]) * 2.65)
                            if self.water_chemistry.iex != 2:
                                exchme[j] = exchme[j] * z[nbx[j]]
                        cec_calc = sum(exchme)

                        line += ",".join([f"{amt:.4e}" for amt in exchme])
                        line += f", {cec_calc:.4e}"
                        line += "\n"
                        f.write(line)

    def plot_u_x(self, time, dimension="2D", components=None):
        """
        Plot concentration of selected components at a given time.

        Parameters:
            time (float): Simulation time to plot.
            dimension (str): '2D' for contour plot, '1D' for line plot.
            components (list): List of component names to plot.
        """
        if components is None:
            components = ["na+"]
        timekey = f"time_{time:10.4e}"
        u = self.spt.get(timekey, None)
        for component in components:
            if component not in u:
                print(f"Component {component} not found in conc data at time {time}")
                return
        if u is None:
            print(f"No data found for time {time}")
            return
        for component in components:
            fig, ax = plt.subplots()
            if dimension == "2D":
                contour = ax.tricontourf(
                    self.nodes.xx, self.nodes.y, u[component], levels=14, cmap="viridis"
                )
                fig.colorbar(contour, ax=ax, label=component + " Concentration")
                ax.set_ylabel("Y")
                ax.set_xlabel("X")
                ax.set_title(f"{component} Concentration Distribution at time {time}")
                plt.show()
            else:
                x = self.nodes.xx[::2]
                u0 = u[component][::2]
                ax.plot(x, u0, linestyle="-", marker="None")
                ax.set_ylabel(f"{component} Concentration")
                ax.set_title(f"{component} Concentration Distribution at time {time}")
                ax.set_xlabel("X")
                plt.show()

    def plot_u_t(self, x, y, components=None):
        """
        Plot concentration of selected components at a specific (x, y) point over time.

        Parameters:
            x (float): X coordinate.
            y (float): Y coordinate.
            components (list): List of component names to plot.
        """
        if components is None:
            components = ["na+"]

        xx = self.nodes.xx
        yy = self.nodes.y
        point = np.array([x, y])
        points = np.column_stack((xx, yy))
        distances = np.linalg.norm(points - point, axis=1)
        idx = np.argmin(distances)
        name_primary_species = self.water_chemistry.name_primary_species
        component_indices = [
            name_primary_species.index(comp)
            for comp in components
            if comp in name_primary_species
        ]

        u_plot = []
        t_plot = []
        for timekey in self.spt.keys():
            if timekey == "xx" or timekey == "y":
                continue
            u = self.spt[timekey]
            t_plot.append(float(timekey.split("_")[1]))
            u_plot.append(u[idx][component_indices])

        df = pd.DataFrame(u_plot, columns=components, index=t_plot)
        df.index.name = "Time"
        df.plot()
        plt.title(f"Concentration Distribution at point ({x}, {y}) over time")
        plt.xlabel("Time")
        plt.ylabel("Concentration")
        plt.show()
