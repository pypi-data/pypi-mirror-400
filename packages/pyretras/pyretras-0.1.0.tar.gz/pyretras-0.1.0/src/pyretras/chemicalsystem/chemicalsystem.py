import numpy as np
import scipy
import sys
from ..dataloaders.dbaseloader import get_database
from ..grids.grid import Elements

from ..solutetransport.solutetransport import SoluteTransport


class ChemicalSystem(Elements):
    """
    ChemicalSystem represents a geochemical system for reactive transport modeling.
    This class manages the initialization, state, and equilibrium calculations for a chemical system
    consisting of aqueous species, minerals, gases, surface complexes, and exchangeable cations.
    It provides methods for initializing concentrations, computing chemical equilibria, updating
    system state, and handling transport and reaction processes across multiple nodes.
    Key Features:
        - Vectorized initialization and assignment of chemical species and reactions.
        - Support for aqueous, mineral, gas, surface complex, and cation exchange phases.
        - Calculation of activity coefficients using the Debye-Hückel model.
        - Newton-Raphson solvers for chemical equilibrium and transport-chemistry coupling.
        - Flexible initialization from input dataframes and chemical databases.
        - Methods for updating, retrieving, and setting system state variables.
        - Calculation of Jacobian matrices and derivatives for nonlinear solvers.
        - Support for adsorption and ion exchange conventions (Gaines-Thomas, Vanselow, Gapon).
    nodes_df : pandas.DataFrame
        DataFrame containing node information for the spatial discretization.
    element_df : pandas.DataFrame
        DataFrame containing element or grid information.
    chem_input : dict
        Dictionary containing chemical system input, including species names, initial/boundary conditions,
        and zone assignments.
    database_path : str
        Path to the chemical database file.
    chemicals_reactions : tuple or None, optional
        Pre-loaded chemical reactions data (stoichiometry, equilibrium constants, etc.).
        If None, the database will be loaded using the provided path.
    Attributes
    name_primary_species : list
        Names of primary aqueous species.
    name_aqu_complexes : list
        Names of secondary aqueous complexes.
    name_minerals : list
        Names of mineral phases.
    name_gases : list
        Names of gas phases.
    name_surface_complexes : list
        Names of surface complexes.
    exchange_reactions : pandas.DataFrame
        DataFrame of exchangeable cation reactions.
    tc2 : float
        System temperature (°C).
    npri, naqx, nmin, ngas, nads, nexc : int
        Number of primary, secondary, mineral, gas, surface, and exchanger species.
    chemicals_reactions : tuple
        Chemical reactions data loaded from the database.
    stqt, ekt, logK_coeffs : np.ndarray
        Stoichiometric coefficients, equilibrium constants, and logK coefficients.
    stqs, eks, stqm, ekm, stqg, ekg, stqd, ekd, stqx, ekx : np.ndarray
        Phase-specific stoichiometric and equilibrium constant arrays.
    z, ion_sizes, zd : np.ndarray
        Charges and ion sizes for species.
    ct, dct, cginit, gamt, dgamt, u2, tt, du2, si2, dsi2, sig2, dsig2 : np.ndarray
        Arrays for concentrations, derivatives, activity coefficients, and saturation indices.
    u, c, r, ub, iub, ur, iur, utem, u0, ubv, urv : np.ndarray
        Arrays for node-wise and zone-wise concentrations and states.
    cm, isat, mout, p, si, pold, aream, vfm : np.ndarray
        Arrays for mineral concentrations and properties.
    cg, g, cgnode, cgpres : np.ndarray
        Arrays for gas concentrations and pressures.
    cd, d, dcd, tads, supadn, phip : np.ndarray
        Arrays for surface complex concentrations and adsorption properties.
    cec2, cec, cx, x, dcx : np.ndarray
        Arrays for cation exchange capacities and concentrations.
    porosity : np.ndarray
        Porosity values for each node.
    special_elements_dict : dict
        Mapping of special species names to their indices.
    nmat, nsat, nbim, nbig, amat, bmat : np.ndarray
        Arrays for Jacobian matrix construction and constraints.
    Other attributes as needed for internal state and calculations.
    Methods
    update_u0(u)
        Update the reference primary concentrations.
    update_utem(utem)
        Update the temporary primary concentrations.
    get_u0()
        Get the reference primary concentrations.
    get_u()
        Get the current primary concentrations.
    set_u(u)
        Set the current primary concentrations.
    show_info()
        Print all attributes and methods of the class.
    set_porosity(porosity_values)
        Set porosity values for all nodes.
    set_c(c_values)
        Set concentrations for all nodes.
    initializing_mineral_conc(mineral_zones)
        Initialize mineral concentrations at each node.
    initializing_gas_conc(gas_zones)
        Initialize gas concentrations at each node.
    initializing_exchanger(exchange_zones)
        Initialize exchanger concentrations at each node.
    initializing_adsorption(adsorption_zones)
        Initialize adsorption concentrations at each node.
    get_constraints(water_type)
        Update constraint indices for minerals and gases.
    initalization_water_zones(waters)
        Initialize water chemistry for all water zones.
    water_speciation_initialization(water_type)
        Perform water speciation using Newton-Raphson method.
    jacobianinit(water_type)
        Construct Jacobian matrix for water speciation.
    chemical_init()
        Initialize chemical system state for equilibrium calculations.
    calc_cm_cp_init()
        Calculate mineral concentrations and derivatives for initialization.
    calc_cg_cp_init()
        Calculate gas concentrations and derivatives for initialization.
    calc_ddh_dcp(debye_huckel_dict)
        Calculate derivatives of activity coefficients.
    calc_dcs_dcp()
        Calculate derivatives of secondary species concentrations.
    calc_activity()
        Calculate activity coefficients using Debye-Hückel model.
    calc_aquspecies_conc()
        Calculate concentrations of aqueous species.
    calc_db_parameters(a, y)
        Static method to evaluate Debye-Hückel polynomial parameters.
    dhparam()
        Static method to provide Debye-Hückel parameter sets.
    fek(t, b)
        Static method to calculate equilibrium constant at temperature t.
    calc_transport_chem(...)
        Perform coupled transport and chemical calculations.
    solve_chemical_equilibrium(maxitpch, tolch, i_node=0)
        Solve chemical equilibrium using Newton-Raphson method.
    calc_chemical_equilibrium(i_node=0)
        Calculate chemical equilibrium state for a node.
    calc_jacobian_matrix()
        Construct Jacobian matrix and right-hand side for nonlinear solver.
    calc_cm_cp()
        Calculate mineral concentrations and derivatives.
    calc_cg_cp()
        Calculate gas concentrations and derivatives.
    calc_adsorption(maxitpad=1000, tolads=1.0e-4)
        Calculate adsorption equilibrium.
    calc_dcd_dcp()
        Calculate derivatives of adsorption concentrations.
    calc_cd_cp(adfactor)
        Calculate adsorption concentrations and update surface potential.
    calc_cx_ct(i_node=0)
        Calculate exchanger concentrations for a node.
    calc_dcx_dcp(i_node=0)
        Calculate derivatives of exchanger concentrations.
    calc_select_coef(inddd, ccc, aekx)
        Calculate selectivity coefficients for exchangers.
    calculate_cubic(a, b, c)
        Static method to solve cubic equations.
    - This class is designed for use in geochemical and reactive transport simulations.
    - It assumes input data is provided in the correct format and that all dependencies (e.g., numpy, pandas, scipy) are available.
    - Many methods rely on internal state and should be called in the correct sequence.
    - Error handling is provided for convergence and data consistency issues.
    """

    def __init__(
        self, nodes_df, element_df, chem_input, database_path, chemicals_reactions=None
    ):
        """
        Optimized initialization for ChemicalSystem.
        Vectorizes array assignments and reduces redundant copies.
        """
        super().__init__(nodes_df, element_df)

        # Extract chemical input
        self.name_primary_species = chem_input["primary aqueous species"]
        self.name_aqu_complexes = chem_input["aqueous complexes"]
        self.name_minerals = chem_input["minerals"]
        self.name_gases = chem_input["gases"]
        self.name_surface_complexes = chem_input["surface complexes"]
        self.exchange_reactions = chem_input["exchangeable cations"]
        self.tc2 = chem_input["temperature"]
        self.database_path = database_path
        self.npri = len(self.name_primary_species)
        self.naqx = len(self.name_aqu_complexes)
        self.nmin = len(self.name_minerals)
        self.ngas = len(self.name_gases)
        self.nads = len(self.name_surface_complexes)

        # Load or assign chemical reactions
        if chemicals_reactions is not None:
            self.chemicals_reactions = chemicals_reactions
        else:
            numbs = [self.npri, self.naqx, self.nmin, self.ngas, self.nads]
            name_species = (
                self.name_primary_species
                + self.name_aqu_complexes
                + self.name_minerals
                + self.name_gases
                + self.name_surface_complexes
            )
            self.chemicals_reactions = get_database(
                name_species, numbs, self.tc2, self.database_path
            )

        # Initialize stoichiometric coefficients and equilibrium constants
        if not self.chemicals_reactions[1].empty:
            self.stqt = (
                self.chemicals_reactions[1].loc[:, self.name_primary_species].values
            )
            if self.tc2 != 25.0:
                self.logK_coeffs = (
                    self.chemicals_reactions[1]
                    .loc[:, ["b1", "b2", "b3", "b4", "b5"]]
                    .values
                )
                self.ekt = np.zeros(
                    self.stqt.shape[0]
                )  # Placeholder, will be set as needed
            else:
                self.ekt = self.chemicals_reactions[1].loc[:, "logK"].values * np.log(
                    10.0
                )
                self.logK_coeffs = np.zeros((self.stqt.shape[0], 5))
        else:
            self.stqt = np.zeros((0, self.npri))
            self.ekt = np.zeros(0)
            self.logK_coeffs = np.zeros((0, 5))

        # Vectorized assignments for secondary species
        self.eks = (
            self.ekt[: self.naqx] if self.ekt.size >= self.naqx else np.zeros(self.naqx)
        )
        self.stqs = (
            self.stqt[: self.naqx, :]
            if self.stqt.shape[0] >= self.naqx
            else np.zeros((self.naqx, self.npri))
        )

        # Vectorized assignments for minerals
        self.nsec = self.naqx
        self.ekm = (
            self.ekt[self.nsec : self.nsec + self.nmin]
            if self.ekt.size >= self.nsec + self.nmin
            else np.zeros(self.nmin)
        )
        self.stqm = (
            self.stqt[self.nsec : self.nsec + self.nmin, :]
            if self.stqt.shape[0] >= self.nsec + self.nmin
            else np.zeros((self.nmin, self.npri))
        )
        self.nsec += self.nmin

        # Vectorized assignments for gases
        self.ekg = (
            self.ekt[self.nsec : self.nsec + self.ngas]
            if self.ekt.size >= self.nsec + self.ngas
            else np.zeros(self.ngas)
        )
        self.stqg = (
            self.stqt[self.nsec : self.nsec + self.ngas, :]
            if self.stqt.shape[0] >= self.nsec + self.ngas
            else np.zeros((self.ngas, self.npri))
        )
        self.nsec += self.ngas

        # Vectorized assignments for surface complexes
        self.ekd = (
            self.ekt[self.nsec : self.nsec + self.nads]
            if self.ekt.size >= self.nsec + self.nads
            else np.zeros(self.nads)
        )
        self.stqd = (
            self.stqt[self.nsec : self.nsec + self.nads, :]
            if self.stqt.shape[0] >= self.nsec + self.nads
            else np.zeros((self.nads, self.npri))
        )
        self.nsec += self.nads

        # ...existing code...

        self.nsec = self.nsec + self.ngas
        self.ekd = np.zeros(self.nads)
        self.stqd = np.zeros((self.nads, self.npri))
        for i in range(self.nads):
            self.ekd[i] = self.ekt[self.nsec + i]
            for j in range(self.npri):
                self.stqd[i, j] = self.stqt[self.nsec + i, j]

        # create a permanent order for the names of aq. species
        self.naaqt = self.name_primary_species + self.name_aqu_complexes

        # indexing  h2o, h, oh, xoh, and e - species:
        self.special_elements_dict = {}
        special_names = [
            "'h2o'",
            "'h+'",
            "'oh-'",
            "'e-'",
            "'o2(aq)'",
            "'co2(aq)'",
            "'h2(aq)'",
            "'xoh'",
            "'xx-'",
        ]
        self.special_elements_dict = {
            name: i
            for i, elem in enumerate(self.naaqt)
            if (name := elem.lower()) in special_names
        }
        # Note that only primiary species can be considered in cation exchange reachtions
        self.nsec = self.nsec + self.nads

        # Vectorized exchanger initialization
        self.name_exchangers = []
        if len(self.exchange_reactions) > 0:
            self.name_exchangers = self.exchange_reactions["exchanger"].tolist()
            self.nexc = len(self.name_exchangers)
            self.nbx = np.zeros(self.nexc, dtype=int)
            self.stqx = np.zeros((self.nexc, self.npri))
            self.naexc = self.exchange_reactions["exchanger"].tolist()
            self.ekx = self.exchange_reactions["aekx1"].astype(float).values
            idum1 = self.exchange_reactions["ims"].astype(int).values
            idum2 = self.exchange_reactions["iex"].astype(int).values
            self.nx = 0
            self.iex = idum2[0] if len(idum2) > 0 else 0
            self.ekxx = np.zeros(self.nexc)
            # Vectorized mapping of primary species to exchangers
            primary_species_map = {
                name: idx for idx, name in enumerate(self.name_primary_species)
            }
            for i in range(self.nexc):
                if idum1[i] == 1 and self.nx == 0:
                    self.nx = i
                    self.iex = idum2[i]
                j = primary_species_map.get(self.naexc[i], -1)
                if j >= 0:
                    self.nbx[i] = j
                    self.stqx[i, :] = 0.0
                    self.stqx[i, j] = 1.0
        else:
            self.nexc = 0
            self.stqx = np.zeros((self.nexc, self.npri))
            self.naexc = []
            self.ekx = np.zeros(self.nexc)

        if self.nexc > 0:
            self.ekt = np.concatenate([self.ekt, self.ekx])
            self.stqt = np.vstack([self.stqt, self.stqx])

        self.nsec += self.nexc

        # Vectorized charge and ion size assignments
        zp = self.chemicals_reactions[0]["charge"].values
        ion_sizes_primary = self.chemicals_reactions[0]["ionSize"].values
        temp_df = self.chemicals_reactions[1]
        zs = (
            temp_df[temp_df["reaction"] == "aquComplexes"]["charge"].values
            if not temp_df.empty
            else np.array([])
        )
        ion_sizes_aqu = (
            temp_df[temp_df["reaction"] == "aquComplexes"]["ionSize"].values
            if not temp_df.empty
            else np.array([])
        )
        zd = (
            temp_df[temp_df["reaction"] == "surfaceComplexes"]["charge"].values
            if not temp_df.empty
            else np.array([])
        )
        self.z = np.concatenate([zp, zs]) if zs.size > 0 else zp
        self.ion_sizes = (
            np.concatenate([ion_sizes_primary, ion_sizes_aqu])
            if ion_sizes_aqu.size > 0
            else ion_sizes_primary
        )
        self.zd = zd
        self.nmat = self.npri
        self.nsat = 0

        ## the following variables are used to store chemical system state at single node
        # self.cp = np.zeros(self.npri)  # concentration of primary species
        # self.cs = np.zeros(self.naqx)  # concentration of aqueous complexes

        # Vectorized and clarified array initializations
        self.ct = np.zeros(self.npri + self.naqx)
        self.dct = np.zeros((self.npri + self.naqx, self.npri))
        self.cginit = np.zeros(self.ngas)
        self.gamt = np.zeros(self.npri + self.naqx)
        self.dgamt = np.zeros((self.npri + self.naqx, self.npri))
        self.u2 = np.zeros(self.npri)
        self.tt = np.zeros(self.npri)
        self.du2 = np.zeros((self.npri, self.npri))
        self.si2 = np.zeros(self.nmin)
        self.dsi2 = np.zeros((self.nmin, self.npri))
        self.sig2 = np.zeros(self.ngas)
        self.dsig2 = np.zeros((self.ngas, self.npri))
        self.nbim = np.zeros(self.npri, dtype=int)
        self.nbig = np.zeros(self.npri, dtype=int)
        self.amat = np.zeros((self.npri, self.npri))
        self.bmat = np.zeros(self.npri)

        ## The following variables are used to store chemical system state for all nodes,

        ## initialize porosity at each node with a default value of 0.3
        ## can be updated later by set_porosity function

        waters = chem_input.get("initial and boundary water types", -1)
        self.u = np.zeros((self.nnod, self.npri))

        self.c = np.zeros((self.nnod, self.npri + self.naqx))
        self.r = np.zeros((self.nnod, self.npri))
        boundary_waters = waters[waters["waterType"] == "boundary"]
        zones = boundary_waters["zone"].unique()
        self.nbwtype = len(zones)
        self.ub = np.zeros((self.nbwtype, self.npri))
        self.iub = np.zeros((self.nbwtype, self.npri))
        zones = waters[waters["waterType"] == "recharge"]["zone"].unique()
        self.nrwtype = len(zones)
        self.ur = np.zeros((self.nrwtype, self.npri))
        self.iur = np.zeros((self.nrwtype, self.npri))
        self.initalization_water_zones(waters)
        self.utem = np.copy(self.u)
        self.u0 = np.copy(self.u)

        self.ubv = np.copy(self.ub)
        self.urv = np.copy(self.ur)

        ## initialize mineral concentrations at each node
        self.cm = np.zeros(self.nmin)
        self.isat = np.zeros(self.nmin, dtype=int)
        self.mout = np.zeros(self.nmin)
        self.p = np.zeros((self.nnod, self.nmin))
        self.si = np.zeros((self.nnod, self.nmin))
        self.pold = np.copy(self.p)
        minerals_zones = chem_input["initial mineral zones"]
        if not minerals_zones.empty:
            self.initializing_mineral_conc(minerals_zones)
        ## the two varaibles, area, vfm are not used yet for kinetic mineral dissolution
        self.aream = np.zeros((self.nnod, self.nmin))
        self.vfm = np.zeros((self.nnod, self.nmin))

        ## Initalize gas concentrations at each node
        self.cg = np.zeros(self.ngas)
        self.g = np.zeros((self.nnod, self.ngas))
        self.cgnode = np.zeros(self.ngas)
        self.cgpres = np.zeros(
            self.ngas
        )  # partial pressure of gases at current conditions
        gases_zones = chem_input["initial gas zones"]
        if not gases_zones.empty:
            self.initializing_gas_conc(gases_zones)

        ## initialize surface complex concentrations at each node
        ## not implement yet
        self.supadn2 = 0.0
        self.tads2 = 0.0
        self.phip2 = 0.0
        self.phip2new = 0.0
        self.cd = np.zeros(self.nads)
        self.d = np.zeros((self.nnod, self.nads))
        self.dcd = np.zeros((self.nads, self.npri))
        self.tads = np.zeros(self.nnod)
        self.supadn = np.zeros(self.nnod)
        self.phip = np.zeros(self.nnod)

        adsorption_zones = chem_input["initial adsorption zones"]
        if not adsorption_zones.empty:
            self.initializing_adsorption(adsorption_zones)
        ## not implement yet
        ## initialize exchangeable cation concentrations at each node
        self.cec2 = 0.0
        self.cec = np.zeros(self.nnod)
        self.cx = np.zeros(self.nexc)
        self.x = np.zeros((self.nnod, self.nexc))
        exchange_zones = chem_input["initial cation exchange zones"]
        self.dcx = np.zeros((self.nexc, self.npri))
        if not exchange_zones.empty:
            self.initializing_exchanger(exchange_zones)

    def update_u0(self, u):
        """
        Update the initial state vector (u0) with a copy of the provided vector.
        Parameters
        ----------
        u : array-like
            The new state vector to be copied and assigned to u0.
        """

        self.u0 = u.copy()

    def update_utem(self, utem):
        """
        Update the 'utem' attribute with a copy of the provided utem object.
        Parameters:
            utem: The object to copy and assign to the 'utem' attribute.
                  It should support the .copy() method.
        Returns:
            None
        """

        self.utem = utem.copy()

    def get_u0(self):
        """
        Returns the standard internal energy (u0) of the chemical system.
        Returns:
            float: The standard internal energy value.
        """

        return self.u0

    def get_u(self):
        """
        Returns the value of the attribute 'u'.
        Returns:
            Any: The current value of the 'u' attribute.
        """

        return self.u

    def set_u(self, u):
        """
        Set the value of the attribute 'u'.
        Parameters:
            u: The value to assign to the attribute 'u'.
        """

        self.u = u

    def show_info(self):
        """
        Displays the names of all attributes and methods of the instance.
        Prints a list of attribute names (excluding special and callable attributes)
        under "Attributes:", and a list of method names (excluding special methods)
        under "Methods:".
        """

        print("Attributes:")
        for attr in dir(self):
            if not attr.startswith("__") and not callable(getattr(self, attr)):
                print(f"  {attr}")
        print("\nMethods:")
        for method in dir(self):
            if not method.startswith("__") and callable(getattr(self, method)):
                print(f"  {method}")

    def set_porosity(self, porosity_values):
        """
        Set the porosity values for each node in the chemical system.
        Parameters
        ----------
        porosity_values : array-like
            A sequence of porosity values to assign to each node. The length of this
            sequence must match the number of nodes (`self.nnod`).
        Raises
        ------
        ValueError
            If the length of `porosity_values` does not match the number of nodes.
        """

        if len(porosity_values) != self.nnod:
            raise ValueError(
                "Length of porosity_values must match number of nodes (nnod)."
            )
        self.porosity = np.array(porosity_values)

    def set_c(self, c_values):
        """
        Set the concentration values for the chemical system.
        Parameters
        ----------
        c_values : numpy.ndarray
            A 2D array of shape (nnod, npri + naqx) containing the concentration values
            to be set. Each row corresponds to a node, and each column corresponds to
            a primary or auxiliary quantity.
        Raises
        ------
        ValueError
            If `c_values` does not have the shape (nnod, npri + naqx).
        """

        if c_values.shape != (self.nnod, self.npri + self.naqx):
            raise ValueError("c_values must have shape (nnod, npri + naqx).")
        self.c = c_values.copy()

    def initializing_mineral_conc(self, mineral_zones):
        """
        Initialize mineral concentrations at each node based on zone assignments.
        For each zone, precompute mineral concentrations and assign to all nodes in that zone.
        Args:
            mineral_zones (pd.DataFrame): DataFrame with columns ['zone', 'mineral', 'initial vol'].
        """
        minerals_df = self.chemicals_reactions[1]
        minerals_df = minerals_df[minerals_df["reaction"] == "mineral"]
        mineral_molar_volumes = dict(zip(minerals_df.index, minerals_df["molarVolum"]))

        # Precompute mineral concentrations for each zone
        zone_mineral_conc = {}
        for izone in mineral_zones["zone"].unique():
            mineral_zone = mineral_zones[mineral_zones["zone"] == izone]
            mineral_initial = dict(zip(mineral_zone.index, mineral_zone["initial vol"]))
            zone_mineral_conc[izone] = [
                (
                    mineral_initial.get(mineral, 0.0)
                    / mineral_molar_volumes.get(mineral, 1.0)
                    if mineral_molar_volumes.get(mineral, 1.0)
                    else 0.0
                )
                for mineral in self.name_minerals
            ]

        # Assign concentrations to nodes
        for n in range(self.nnod):
            node_zone = self.izonem[n]  # zone index (assuming zone starts at 1)
            if node_zone in zone_mineral_conc:
                mineral_conc = zone_mineral_conc[node_zone]
                for m in range(self.nmin):
                    val = (
                        mineral_conc[m] / self.porosity[n] if self.porosity[n] else 0.0
                    )
                    self.p[n, m] = val
                    self.pold[n, m] = val
            else:
                # Optionally handle nodes with no matching zone
                self.p[n, :] = 0
                self.pold[n, :] = 0

    def initializing_gas_conc(self, gas_zones):
        """
        Initialize gas concentrations at each node based on zone assignments.

        For each zone in gas_zones, assign the initial gas concentrations to all nodes
        belonging to that zone. If a gas concentration is nonzero, set self.g[n, m] = 100,
        otherwise use the original value.

        Args:
            gas_zones (pd.DataFrame): DataFrame with columns ['zone', 'gas', 'initial vol'].
        """
        # Precompute gas concentrations for each zone
        zone_gas_conc = {}
        for izone in gas_zones["zone"].unique():
            gas_zone = gas_zones[gas_zones["zone"] == izone]
            gas_initial = dict(zip(gas_zone["gas"], gas_zone["initial vol"]))
            zone_gas_conc[izone] = [
                gas_initial.get(gas, 0.0) for gas in self.name_gases
            ]

        # Assign concentrations to nodes
        for n in range(self.nnod):
            node_zone = self.izoneg[n]  # zone index (assuming zone starts at 1)
            if node_zone in zone_gas_conc:
                gas_conc = zone_gas_conc[node_zone]
                for m in range(self.ngas):
                    val = 100 if gas_conc[m] != 0 else gas_conc[m]
                    self.g[n, m] = val
                    self.cgnode[n, m] = gas_conc[m]
            else:
                # Optionally handle nodes with no matching zone
                self.g[n, :] = 0
                self.cgnode[n, :] = 0

    def initializing_exchanger(self, exchange_zones):
        """
        Initializes the ion exchanger properties for each node based on the provided exchange zones.
        This method iterates over unique exchange zones, normalizes the exchange capacity if required,
        and assigns the corresponding values to each node. For each node, it sets the cation exchange
        capacity (CEC) and initializes the exchanger composition. If the exchange capacity is zero,
        the exchanger composition is set to zero; otherwise, it is calculated using the `calc_cx_ct` method.
        Parameters:
            exchange_zones (pandas.DataFrame): DataFrame containing information about exchange zones.
                Must include columns "zone" and "ex capacity".
        Attributes used:
            self.iex (int): Flag indicating whether to normalize exchange capacity.
            self.nnod (int): Number of nodes.
            self.izonex (array-like): Array mapping each node to its exchange zone.
            self.c (ndarray): Concentration array for each node.
            self.ceca (ndarray): Array to store normalized exchange capacities.
            self.cec (ndarray): Array to store cation exchange capacities for each node.
            self.cec2 (float): Stores the current zone's total exchange capacity.
            self.nexc (int): Number of exchanger components.
            self.x (ndarray): Exchanger composition array for each node.
            self.cx (ndarray): Temporary array for exchanger composition.
        Notes:
            - Assumes that zone indices in `izonex` correspond to the "zone" values in `exchange_zones`.
            - The method modifies several instance attributes in-place.
        """

        for zone in exchange_zones["zone"].unique():
            exchange_zone = exchange_zones[exchange_zones["zone"] == zone]
            if self.iex == 1:
                cec2 = exchange_zone["ex capacity"].sum()
                exchange_zone["ex capacity"] = exchange_zone["ex capacity"] / cec2
            self.ceca = exchange_zone["ex capacity"].values
            for n in range(self.nnod):
                node_zone = self.izonex[n]  # zone index (assuming zone starts at 1)
                self.ct = np.copy(self.c[n, :])
                # Removed unused variable debyeHuckelDict

                if node_zone == zone:
                    self.cec[n] = cec2
                    self.cec2 = cec2
                    if cec2 == 0:
                        for i in range(self.nexc):
                            self.x[n, i] = 0.0
                    else:
                        self.calc_cx_ct(n)
                        for i in range(self.nexc):
                            self.x[n, i] = self.cx[i]

    def initializing_adsorption(self, adsorption_zones):
        """
        Initializes adsorption-related properties for each node in the chemical system based on provided adsorption zones.
        This method sets up the initial adsorption data for each node by:
          - Extracting the special element index for 'xoh' from the primary species.
          - Mapping adsorption zone data to each node based on its zone assignment.
          - Initializing adsorption potential, surface area, and related properties for each node.
          - Calculating adsorption coefficients and updating concentration arrays as needed.
        Parameters:
            adsorption_zones (dict or DataFrame): A mapping or table containing adsorption zone information.
                Expected keys/columns:
                    - "zone": Zone identifier for each adsorption region.
                    - "sadsdum": Surface area or adsorption capacity parameter for the zone.
                    - "tads2": Initial adsorption value for the zone.
        Raises:
            ValueError: If the special element 'xoh' is not found in the primary species.
        Side Effects:
            Modifies several instance attributes related to adsorption, including:
                - self.tads, self.supadn, self.c, self.u, self.d, self.phip, etc.
        """

        ## extract the initial adsorption data for each zone
        nd = self.special_elements_dict.get("'xoh'", -1)
        if nd == -1:
            raise ValueError("Special element 'xoh' not found in primary species.")

        adsorption_initial_dict = dict(
            zip(
                adsorption_zones["zone"],
                zip(adsorption_zones["sadsdum"], adsorption_zones["tads2"]),
            )
        )
        for n in range(self.nnod):
            node_zone = self.izoned[n]
            if node_zone in adsorption_initial_dict:
                adsorption_potential = adsorption_initial_dict[node_zone]
                self.tads2 = adsorption_potential[1]
                self.tads[n] = self.tads2
                self.supadn2 = (
                    adsorption_potential[0]
                    * 100.0
                    * 2.65
                    * (1.0 - self.porosity[n])
                    / self.porosity[n]
                )
                self.ct = np.copy(self.c[n, :])
                if self.tads2 == 0:
                    self.d[n, :] = 0.0
                else:
                    self.phip2 = 0.0
                    sumcd = 0.0
                    # Only define cp, gamp, dgamp if needed for calculations
                    for m in range(self.nads):
                        self.cd[m] = -self.ekd[m]
                        sumcd += self.cd[m]
                    self.ct[nd] = self.tads[n] / (1.0 + sumcd)
                    self.calc_adsorption()
                    for m in range(self.nads):
                        self.d[n, m] = self.cd[m]
                    self.c[n, nd] = self.ct[nd]
                    self.u[n, nd] = self.ct[nd]
                    self.phip[n] = self.phip2new
                    self.supadn[n] = self.supadn2
            else:
                self.tads[n] = 0
                self.supadn[n] = 0

    def __repr__(self):
        """
        Return a string representation of the ChemicalSystem instance, displaying all its attributes.
        Returns:
            str: A string showing the class name and a dictionary of the instance's attributes.
        """

        return f"ChemicalSystem(attributes={vars(self)})"

    def get_constraints(self, water_type):
        """
        Updates internal constraint indices for minerals and gases based on the provided water type.
        Args:
            water_type (dict or pandas.DataFrame):
                A mapping or DataFrame containing keys:
                    - 'icon': List or array of integer codes indicating constraint type for each primary species.
                    - 'constrain': List or array of names corresponding to minerals or gases.
                    - 'guess': List or array of initial guess values for each primary species.
        Side Effects:
            - Updates self.ct with initial guess values.
            - Updates self.nbim with mineral indices for species where icon == 4.
            - Updates self.nbig with gas indices for species where icon == 5.
        Notes:
            - Assumes self.npri, self.nmin, self.ngas, self.name_minerals, self.name_gases, self.ct, self.nbim, and self.nbig are defined.
            - The function matches constraint names to minerals or gases and sets the corresponding index.
        """
        # subroutine to get the indexes of minerals and gases for initial condition
        icon = water_type["icon"].tolist()
        nadum = water_type["constrain"].tolist()
        for i in range(self.npri):
            self.ct[i] = water_type["guess"][i]

            imin = 0
            igi = 0
            if icon[i] == 4:
                for jj in range(self.nmin):
                    if nadum[i] == self.name_minerals[jj]:
                        imin = jj  # here cbyang modified Jan 25 2004

                self.nbim[i] = imin

            if icon[i] == 5:

                for jj in range(0, self.ngas):
                    if nadum[i] == self.name_gases[jj]:
                        igi = jj
                self.nbig[i] = igi

    def initalization_water_zones(self, waters):
        """
        Initializes water chemistry parameters for different water zones in the system.
        This method processes the input DataFrame `waters` to initialize chemical properties
        for three types of water zones: initial, boundary, and recharge. For each zone type,
        it identifies unique zones, performs water speciation initialization, and sets the
        corresponding chemical state variables for each zone.
        Parameters:
            waters (pd.DataFrame): A DataFrame containing water information with at least the following columns:
                - "waterType": Specifies the type of water ("initial", "boundary", or "recharge").
                - "zone": Identifies the zone for each water entry.
                - "ictot2": (For boundary and recharge waters) Total ion concentrations.
        Side Effects:
            Updates the following instance attributes:
                - self.u, self.c: Chemical state arrays for initial waters.
                - self.ub, self.iub: Chemical state arrays for boundary waters.
                - self.ur, self.iur: Chemical state arrays for recharge waters.
                - self.nbwtype: Number of unique boundary water zones.
                - self.nrwtype: Number of unique recharge water zones.
        Notes:
            - Assumes that `self.izoneiw` and `self.izonebw` are lists of zone indices (1-based) for initial and boundary waters, respectively.
            - Relies on the method `self.water_speciation_initialization` to perform water chemistry calculations for each zone.
            - The method modifies internal state arrays to reflect the initialized chemical conditions for each zone type.
        """

        ## initializing water chemistry for initial waters

        initial_waters = waters[waters["waterType"] == "initial"]
        zones = initial_waters["zone"].unique()
        izoneiw = self.izoneiw
        izoneiw = [x - 1 for x in izoneiw]  # make it zero based index
        izonebw = self.izonebw
        izonebw = [x - 1 for x in izonebw]  # make it zero based index
        ## 1: first boundary condition, 2: second boundary condition
        for iz, zone in enumerate(zones):
            water_zone = initial_waters[initial_waters["zone"] == zone]
            self.water_speciation_initialization(water_zone)
            node_indices = np.where(np.array(izoneiw) == iz)[0]
            self.u[node_indices, :] = self.u2
            self.c[node_indices, :] = self.ct
        ## initializing water chemistry for boundary waters
        boundary_waters = waters[waters["waterType"] == "boundary"]
        zones = boundary_waters["zone"].unique()
        self.nbwtype = len(zones)
        if self.nbwtype > 0:
            for idx, zone in enumerate(zones):
                water_zone = boundary_waters[boundary_waters["zone"] == zone]
                self.water_speciation_initialization(water_zone)
                self.ub[idx, :] = self.u2
                self.iub[idx, :] = water_zone["ictot2"].to_list()
        rech_waters = waters[waters["waterType"] == "recharge"]
        zones = rech_waters["zone"].unique()
        self.nrwtype = len(zones)
        if self.nrwtype > 0:
            for idx, zone in enumerate(zones):
                water_zone = rech_waters[rech_waters["zone"] == zone]
                self.water_speciation_initialization(water_zone)
                self.ur[idx, :] = self.u2
                self.iur[idx, :] = water_zone["ictot2"].to_list()

    def water_speciation_initialization(self, water_type):
        """
        Initializes the water speciation concentrations using the Newton-Raphson method.
        This method iteratively solves for the initial concentrations of primary species in water,
        given an initial guess, by updating the concentrations until convergence is achieved or
        the maximum number of iterations is reached. The Jacobian matrix is recalculated at each
        iteration, and the solution is updated using a damping factor to ensure stability.
        Parameters
        ----------
        water_type : dict
            Dictionary containing the initial guess for the primary species concentrations.
            Must include the key "guess" with a list or array of initial values.
        Notes
        -----
        - The method updates self.ct with the converged concentrations.
        - Uses a maximum of 10 iterations and a convergence tolerance of 1e-6.
        - Relies on self.chemical_init() and self.jacobianinit() to update system matrices.
        - Uses scipy.linalg.solve to solve the linear system at each iteration.
        """

        # Use newton-Raphson method
        # water_zones = project_chem['initial and boundary water types']
        # naaqt = [nam.replace("'", "").lower() for nam in naaqt]
        facmax = 0.5
        tolch = 1.0e-4
        # for water_types in water_zones:
        # dgamt = np.zeros((self.npri + self.naqx, self.npri))
        maxitpch = 10
        self.ct[: self.npri] = water_type["guess"].tolist()
        cp = self.ct[: self.npri].copy()
        for _ in range(maxitpch):
            tolch = 1e-6
            self.chemical_init()
            self.jacobianinit(water_type)
            c = scipy.linalg.solve(self.amat, self.bmat)
            self.bmat = c.copy()
            errmax = max(self.bmat / cp)
            if errmax > facmax:
                self.bmat = self.bmat * facmax / errmax
            cp = cp + self.bmat
            self.ct[: self.npri] = cp.copy()
            if errmax < tolch:
                break

    def jacobianinit(self, water_type):
        """
        Initializes the Jacobian matrix and right-hand side vector for the chemical system
        based on the provided water type configuration.
        This method sets up the system of equations required for solving the chemical
        equilibrium problem. It handles different types of constraints for each primary
        species, including fixed total solute concentration, charge balance, fixed activity,
        mineral equilibrium, and gas equilibrium. The method also applies special handling
        for certain elements if specified.
        Parameters
        ----------
        water_type : dict
            Dictionary containing water composition and constraint information. Must include:
                - "icon": list or array indicating the type of constraint for each primary species
                - "ctot": list or array of total concentrations for each primary species
        Side Effects
        ------------
        Updates the following instance attributes:
            - self.amat : 2D array
                The Jacobian matrix for the system.
            - self.bmat : 1D array
                The right-hand side vector for the system.
            - self.tt : list
                The total concentrations for each primary species.
        Raises
        ------
        SystemExit
            If the charge balance constraint is violated for any primary species.
        Notes
        -----
        The method assumes that several instance attributes (such as self.gamt, self.dgamt,
        self.ct, self.z, self.dct, self.npri, self.naqx, self.du2, self.u2, self.dsi2,
        self.nbim, self.si2, self.dsig2, self.nbig, self.sig2, self.special_elements_dict)
        are already initialized and have appropriate shapes and values.
        """

        gamp = np.copy(self.gamt[: self.npri])
        dgamp = np.copy(self.dgamt[: self.npri, :])
        cp = np.copy(self.ct[: self.npri])
        zp = np.copy(self.z[: self.npri])
        zs = np.copy(self.z[self.npri :])
        dcs = np.copy(self.dct[self.npri :, :])
        icon = water_type["icon"].tolist()
        self.tt = water_type["ctot"].tolist()
        for i in range(self.npri):
            # for fixed total solute concentration
            if icon[i] == 1:
                for j in range(self.npri):
                    self.amat[i, j] = self.du2[i, j]
                self.bmat[i] = self.tt[i] - self.u2[i]
            # concentration of primary species fixed by charge balance
            if icon[i] == 2:
                for j in range(self.npri):
                    self.amat[i, j] = zp[j]
                    for k in range(self.naqx):
                        self.amat[i, j] = self.amat[i, j] + zs[k] * dcs[k, j]
                for j in range(self.npri + self.naqx):
                    self.bmat[i] = self.bmat[i] - self.z[j] * self.ct[j]
                if (-self.bmat[i] - zp[i] * cp[i]) / zp[i] > 0:
                    print("Something wrong with the charge balance!")
                    sys.exit()

            # fixed activity
            if icon[i] == 3:
                for j in range(self.npri):
                    self.amat[i, j] = cp[i] * dgamp[i, j]
                    if i == j:
                        self.amat[i, j] = self.amat[i, j] + gamp[i]
                self.bmat[i] = self.tt[i] - cp[i] * gamp[i]

            # mineral equilibrium constraint
            if icon[i] == 4:
                for j in range(self.npri):
                    self.amat[i, j] = self.dsi2[self.nbim[i], j]
                self.bmat[i] = -self.si2[self.nbim[i]] + 1.0

            # gas equilibrium constraint
            if icon[i] == 5:
                for j in range(self.npri):
                    self.amat[i, j] = self.dsig2[self.nbig[i], j]
                self.bmat[i] = -self.sig2[self.nbig[i]] + 1.0

            nd = self.special_elements_dict.get("'xoh'", -1)
            if nd > 0:
                self.amat[nd, nd] = 1.0
                self.bmat[nd] = 0.0

    def chemical_init(self):
        """
        Initializes the chemical system by performing the following steps:
        1. Calculates the activity coefficients of aqueous species using the Debye-Hückel equation.
        2. Calculates the concentrations of aqueous species.
        3. Computes the derivatives of the concentrations of aqueous species with respect to primary species.
        4. Computes the derivatives of the activity coefficients of aqueous species with respect to primary species.
        5. If minerals are present (`self.nmin > 0`), calculates the saturation indices of minerals for the initial condition and their derivatives.
        6. If gases are present (`self.ngas > 0`), calculates the saturation indices of gases for the initial condition and their derivatives.
        This method prepares the chemical system for further calculations by ensuring all relevant properties and their sensitivities are initialized.
        """

        # calculate activity
        debyeHuckelDict = self.calc_activity()

        ## Calculate concentration of aqueous species
        self.calc_aquspecies_conc()

        # Calcualte derivatives of concentration of aqueous species to primary species
        self.calc_dcs_dcp()

        # Calcualte derivatives of activity coefficient of aqueous species to primary species
        self.calc_ddh_dcp(debyeHuckelDict)

        if self.nmin > 0:
            # Calcualte saturation indices of minerals for the inital condition
            #  and derivatives of saturation indices
            self.calc_cm_cp_init()

        if self.ngas > 0:
            # Calcualte saturation indices of gases for the inital condition
            #  and derivatives of saturation indices
            self.calc_cg_cp_init()

    def calc_cm_cp_init(self):
        """
        Calculates and initializes the concentration and related derivatives for the chemical system.
        This method performs the following steps:
        1. Copies the primary concentrations (`ct`), activity coefficients (`gamt`), and their derivatives (`dgamt`) for use in calculations.
        2. For each mineral phase (`nmin`), computes an intermediate value (`si2`) based on stoichiometric coefficients (`stqm`), concentrations, and activity coefficients, then exponentiates the result.
        3. Calculates the derivatives of `si2` with respect to primary concentrations and activity coefficients, storing the results in `dsi2`.
        The method updates the following instance attributes:
        - `self.si2`: Array of computed values for each mineral phase.
        - `self.dsi2`: Array of derivatives for each mineral phase and primary component.
        Assumes the following instance attributes are defined:
        - `self.ct`: Array of concentrations.
        - `self.gamt`: Array of activity coefficients.
        - `self.dgamt`: Array of derivatives of activity coefficients.
        - `self.npri`: Number of primary components.
        - `self.nmin`: Number of mineral phases.
        - `self.stqm`: Stoichiometric matrix.
        - `self.ekm`: Array of equilibrium constants.
        """
        cp = np.copy(self.ct[: self.npri])
        gamp = np.copy(self.gamt[: self.npri])
        dgamp = np.copy(self.dgamt[: self.npri, :])

        for m in range(self.nmin):
            paim = 0.0
            for i in range(self.npri):
                paim = paim + self.stqm[m, i] * (np.log(cp[i]) + np.log(gamp[i]))
            self.si2[m] = paim - self.ekm[m]
            self.si2[m] = np.exp(self.si2[m])

        for m in range(self.nmin):
            for i in range(self.npri):
                self.dsi2[m, i] = self.si2[m] * self.stqm[m, i] / cp[i]
                for k in range(self.npri):
                    self.dsi2[m, i] = (
                        self.dsi2[m, i]
                        + self.si2[m] * self.stqm[m, k] * dgamp[k, i] / gamp[k]
                    )

    def calc_cg_cp_init(self):
        """
        Calculates and initializes the concentration and pressure-related variables for the chemical system.
        This method performs the following steps:
        - Copies initial concentration (`ct`), activity coefficient (`gamt`), and their derivatives (`dgamt`) for primary species.
        - For each gas species:
            - Computes intermediate values (`paig`) based on stoichiometric coefficients (`stqg`), concentrations, and activity coefficients.
            - Updates `sig2` and `cgpres` arrays using exponential and logarithmic transformations, considering initial gas concentrations (`cginit`) and equilibrium constants (`ekg`).
        - For each gas species with positive initial concentration:
            - Calculates derivatives of `sig2` with respect to primary species concentrations, updating the `dsig2` array.
        Attributes used:
            ct (np.ndarray): Concentrations of primary species.
            gamt (np.ndarray): Activity coefficients of primary species.
            dgamt (np.ndarray): Derivatives of activity coefficients.
            npri (int): Number of primary species.
            ngas (int): Number of gas species.
            stqg (np.ndarray): Stoichiometric coefficients for gas reactions.
            ekg (np.ndarray): Equilibrium constants for gas reactions.
            cginit (np.ndarray): Initial concentrations of gas species.
            sig2 (np.ndarray): Computed intermediate variable for each gas species.
            cgpres (np.ndarray): Computed pressure for each gas species.
            dsig2 (np.ndarray): Derivatives of `sig2` with respect to primary species concentrations.
        Returns:
            None
        """
        cp = np.copy(self.ct[: self.npri])
        gamp = np.copy(self.gamt[: self.npri])
        dgamp = np.copy(self.dgamt[: self.npri, :])
        for m in range(self.ngas):
            paig = 0.0
            for i in range(self.npri):
                paig = paig + self.stqg[m, i] * (np.log(cp[i]) + np.log(gamp[i]))
            self.sig2[m] = paig - self.ekg[m]
            self.sig2[m] = np.exp(self.sig2[m])

            if self.cginit[m] <= 0.0:
                self.sig2[m] = 1.0
            else:
                self.sig2[m] = paig - np.log(self.cginit[m]) - self.ekg[m]
            self.cgpres[m] = np.exp(paig - self.ekg[m])

        for m in range(self.ngas):
            if self.cginit[m] > 0.0:
                for i in range(self.npri):
                    self.dsig2[m, i] = self.sig2[m] * self.stqg[m, i] / cp[i]
                    for k in range(self.npri):
                        self.dsig2[m, i] = (
                            self.dsig2[m, i]
                            + self.sig2[m] * self.stqg[m, k] * dgamp[k, i] / gamp[k]
                        )

    def calc_ddh_dcp(self, debye_huckel_dict):
        """
        Calculates the derivatives of activity coefficients (gamma) with respect to changes in primary species concentrations
        using the Debye-Hückel model.
        Parameters
        ----------
        debyeHuckelDict : dict
            Dictionary containing Debye-Hückel parameters:
                - 'ionStrength': float, ionic strength of the solution
                - 'a': float, Debye-Hückel constant a
                - 'b': float, Debye-Hückel constant b
                - 'bdot': float, additional Debye-Hückel parameter
        Updates
        -------
        self.dgamt : ndarray
            Matrix of derivatives of activity coefficients with respect to primary species concentrations.
        Notes
        -----
        - Uses charge and stoichiometry information from self.z and self.dct.
        - Excludes special elements (e.g., electrons, water, xoh) from certain calculations.
        - Relies on precomputed arrays for ion sizes and activity coefficients.
        """
        # subroutine calculates the derivative of activity coefficients
        # as a function of the change in primary species
        zp = np.copy(self.z[: self.npri])
        zs = np.copy(self.z[self.npri :])
        dcs = np.copy(self.dct[self.npri :, :])
        ion_strength = debye_huckel_dict["ionStrength"]
        relstr = np.sqrt(ion_strength)
        a = debye_huckel_dict["a"]
        b = debye_huckel_dict["b"]
        bdot = debye_huckel_dict["bdot"]
        # The derivative of the ionic strenght with regards to primary species
        nw = self.special_elements_dict.get("'h2o'", -1)
        nd = self.special_elements_dict.get("'xoh'", -1)
        dstr = np.zeros(self.npri)
        for i in range(self.npri):
            if i != nw:
                dstr[i] = 0.5 * zp[i] * zp[i]
                for j in range(self.naqx):
                    dstr[i] = dstr[i] + zs[j] * zs[j] * dcs[j, i]

        for i in range(self.npri + self.naqx):
            if i not in [nw, nd]:
                den = 1.0 + b * self.ion_sizes[i] * relstr
                den = den * den * 2 * relstr
                dum = a * self.z[i] * self.z[i] / den + bdot
                dum = -np.log(10.0) * self.gamt[i] * dum
                for j in range(self.npri):
                    self.dgamt[i, j] = dum * dstr[j]

            # Subroutine to get the indexes of minerals and gases for initial condition

    def calc_dcs_dcp(self):
        """
        Calculates the derivatives of concentrations of secondary species (dcs) and primary species (dcp)
        with respect to the concentrations of primary species in a chemical system.
        The method performs the following steps:
        - Copies relevant arrays for concentrations and activity coefficients of primary and secondary species.
        - Initializes derivative matrices for primary (dcp) and secondary (dcs) species.
        - Computes the derivatives of secondary species concentrations with respect to primary species concentrations,
          considering stoichiometric coefficients and activity coefficient derivatives.
        - Concatenates the derivative matrices to form the total derivative matrix (dct).
        - Calculates the derivative of the total amount of solute with respect to primary species (du2),
          incorporating contributions from both primary and secondary species.
        Updates:
            self.dct (np.ndarray): Concatenated derivative matrix of concentrations.
            self.du2 (np.ndarray): Derivative of total solute amount with respect to primary species.
        Assumes:
            - self.ct, self.gamt, self.dgamt, self.stqs, self.npri, self.naqx are defined and properly shaped.
        """
        cp = np.copy(self.ct[: self.npri])
        cs = np.copy(self.ct[self.npri :])
        gamp = np.copy(self.gamt[: self.npri])
        gams = np.copy(self.gamt[self.npri :])
        dgamp = np.copy(self.dgamt[: self.npri, :])
        dgams = np.copy(self.dgamt[self.npri :, :])

        dcp = np.zeros((self.npri, self.npri))
        np.fill_diagonal(dcp, 1)
        dcs = np.zeros((self.naqx, self.npri))

        for j in range(self.naqx):
            for i in range(self.npri):
                dcs[j, i] = (
                    cs[j] * self.stqs[j, i] / cp[i] - cs[j] * dgams[j, i] / gams[j]
                )
                for k in range(self.npri):
                    dcs[j, i] = (
                        dcs[j, i] + cs[j] * self.stqs[j, k] * dgamp[k, i] / gamp[k]
                    )

        self.dct = np.concatenate((dcp, dcs))

        #  the derivative of total amount of solute with regards to prim. sp.
        self.du2 = np.zeros((self.npri, self.npri))
        for k in range(self.npri):
            for i in range(self.npri):
                self.du2[i, k] = self.dct[i, k]
                for j in range(self.naqx):
                    self.du2[i, k] = self.du2[i, k] + self.stqs[j, i] * dcs[j, k]

    def calc_activity(self):
        """
        Calculates the activity coefficients for all species in the chemical system using the Debye-Hückel equation.
        The method computes the ionic strength of the solution, determines the Debye-Hückel parameters (A, B, B-dot)
        based on the temperature, and calculates the activity coefficients for each ion and special elements
        (e.g., H2O, e-, O2(aq), xOH). The results are stored in `self.gamt` and a dictionary containing the
        Debye-Hückel parameters and ionic strength is returned.
        Returns:
            dict: A dictionary containing the Debye-Hückel parameters ('a', 'b', 'bdot') and the calculated ionic strength ('ionStrength').
        """
        dh_param_dict = self.dhparam()
        summ = 0

        no2 = self.special_elements_dict.get("'o2(aq)'", -1)
        nd = self.special_elements_dict.get("'xoh'", -1)
        nw = self.special_elements_dict.get("'h2o'", -1)
        debye_huckel_dict = {}
        # ne: the order of e-
        # nw: position of water (h2o)
        for i in range(self.npri + self.naqx):
            if i != nw:
                summ = summ + self.z[i] * self.z[i] * self.ct[i]
        ion_strength = 0.5 * summ
        if ion_strength < 1.0e-20:
            ion_strength = 1.0e-20
        rel_strength = np.sqrt(ion_strength)
        # Calculate the A, B and B-dot parameters of the D-H equation
        if self.tc2 <= 100.0:
            dummy = dh_param_dict["alt"]
            a = self.calc_db_parameters(dummy, self.tc2)
            dummy = dh_param_dict["blt"]
            b = self.calc_db_parameters(dummy, self.tc2)
            dummy = dh_param_dict["dlt"]
            bdot = self.calc_db_parameters(dummy, self.tc2)
        else:
            dummy = dh_param_dict["aht"]
            a = self.calc_db_parameters(dummy, self.tc2)
            dummy = dh_param_dict["bht"]
            b = self.calc_db_parameters(dummy, self.tc2)
            dummy = dh_param_dict["dht"]
            bdot = self.calc_db_parameters(dummy, self.tc2)

        debye_huckel_dict["a"] = a
        debye_huckel_dict["b"] = b
        debye_huckel_dict["bdot"] = bdot
        debye_huckel_dict["ionStrength"] = ion_strength

        # Activity coeficients: D-H bdot equation
        # gamt = np.zeros(self.npri + self.naqx)
        for i in range(self.npri + self.naqx):
            if i not in [nw, nd, no2]:
                gam = 1.0 + b * self.ion_sizes[i] * rel_strength
                gam = -a * self.z[i] * self.z[i] * rel_strength / gam
                gam = gam + bdot * ion_strength
                self.gamt[i] = pow(10.0, gam)

        # activity coefficent for H2O
        if nw >= 0:
            tots = 0.0
            for i in range(self.npri + self.naqx):
                if i not in [nw, nd, no2]:
                    tots = tots + self.ct[i]
            self.gamt[nw] = 1.0 - 0.018 * tots
        if no2 >= 0:
            self.gamt[no2] = 1.0
        if nd >= 0:
            self.gamt[nd] = 1.0

        return debye_huckel_dict

    def calc_aquspecies_conc(self):  # npri, naqx, cp, gamt, eks, stqs):
        """
        Calculates the concentrations of aqueous species and updates the total solute in solution.

        This method performs the following steps:
        1. Splits the total concentration array (`self.ct`) into primary (`cp`) and secondary (`cs`) species.
        2. Calculates the concentrations of secondary aqueous species using activity coefficients (`self.gamt`),
            equilibrium constants (`self.eks`), and stoichiometric coefficients (`self.stqs`).
        3. Updates the total concentration array (`self.ct`) with the new values.
        4. Computes the total solute in solution for each primary species and stores it in `self.u2`.

        Attributes used:
            self.npri (int): Number of primary species.
            self.naqx (int): Number of secondary aqueous species.
            self.ct (np.ndarray): Concentrations of all species.
            self.gamt (np.ndarray): Activity coefficients for all species.
            self.eks (np.ndarray): Equilibrium constants for secondary species.
            self.stqs (np.ndarray): Stoichiometric coefficients (secondary species x primary species).
            self.u2 (np.ndarray): Total solute in solution for each primary species.

        Returns:
            None
        """
        gamp = np.copy(self.gamt[: self.npri])
        gams = np.copy(self.gamt[self.npri :])
        cs = self.ct[self.npri :]
        cp = self.ct[: self.npri]
        for j in range(self.naqx):
            cs[j] = -np.log(gams[j]) - self.eks[j]
            for i in range(self.npri):
                cs[j] = cs[j] + self.stqs[j, i] * (np.log(cp[i]) + np.log(gamp[i]))
            cs[j] = np.exp(cs[j])
        self.ct = np.concatenate([cp, cs])
        # Update the total solute in solution
        self.u2 = np.zeros(self.npri)
        for i in range(self.npri):
            self.u2[i] = self.ct[i]
            for j in range(self.naqx):
                self.u2[i] = self.u2[i] + self.stqt[j, i] * self.ct[self.npri + j]

    @staticmethod
    def calc_db_parameters(a, y):
        """
        Calculates database parameters using a 4th-degree polynomial in y.

        Args:
            a (list or tuple of float): Coefficients [a0, a1, a2, a3, a4] for the polynomial.
            y (float): The variable to evaluate the polynomial at.

        Returns:
            float: The result of the polynomial calculation.
        """
        return a[0] + (a[1] + (a[2] + (a[3] + a[4] * y) * y) * y) * y

    @staticmethod
    def dhparam():
        dh_param_dict = {}
        alt = np.array(
            [
                4.913000000e-01,
                5.808571429e-04,
                5.527142857e-06,
                -4.857142857e-09,
                0.000000000e00,
            ]
        )
        dh_param_dict["alt"] = alt

        blt = np.array(
            [
                3.247000000e-01,
                1.309285714e-04,
                5.502380952e-07,
                -1.095238095e-09,
                0.000000000e00,
            ]
        )
        dh_param_dict["blt"] = blt

        dlt = np.array(
            [
                1.740000000e-02,
                1.509047619e-03,
                -2.605904762e-05,
                1.382857143e-07,
                0.000000000e00,
            ]
        )
        dh_param_dict["dlt"] = dlt

        aht = np.array(
            [
                6.440000000e-01,
                -3.436166667e-03,
                4.408833333e-05,
                -1.691333333e-07,
                2.766666667e-10,
            ]
        )
        dh_param_dict["aht"] = aht

        bht = np.array(
            [
                3.302000000e-01,
                -1.650000000e-05,
                1.991666667e-06,
                -7.400000000e-09,
                1.133333333e-11,
            ]
        )
        dh_param_dict["bht"] = bht

        dht = np.array(
            [
                1.090000000e-01,
                -1.483333333e-03,
                1.173333333e-05,
                -3.466666667e-08,
                2.666666667e-11,
            ]
        )
        dh_param_dict["dht"] = dht
        # to calculate the activity coefficient of CO2, as well as
        # those of neutral nonpolar species, according to EQ3/6
        # Data from Drummond (1981), as given by Wolery (1992)
        cco2 = np.array([-1.031200, 0.012806, 255.900000, 0.444500, -0.001606])
        dh_param_dict["cco2"] = cco2

        return dh_param_dict

    @staticmethod
    def fek(t, b):
        # calculate the equilibrium constant at give temperature
        temp = t + 273.15

        fek = (
            b[0] * np.log(temp)
            + b[1]
            + b[2] * temp
            + b[3] / temp
            + b[4] / (temp * temp)
        )
        fek = fek * np.log(10.0)
        return fek

    def calc_transport_chem(
        self,
        dt,
        ptra,
        btras1,
        gptflw,
        w,
        flow_control,
        chemical_calc_controls,
        converge_tolerance,
    ):

        itertr = 0
        xita2 = flow_control.loc["val", "xita2"]

        icall = np.ones(self.nnod, dtype=int)
        ispia = chemical_calc_controls.loc["val", "ispia"]
        toltr = converge_tolerance.loc["val", "toltr"]
        maxitptr = converge_tolerance.loc["val", "maxitptr"]
        maxitpch = converge_tolerance.loc["val", "maxitpch"]
        tolch = converge_tolerance.loc["val", "tolch"]
        # will add the conditions later
        errumax = toltr + 1.0
        self.r = np.zeros((self.nnod, self.npri))
        while errumax > toltr:
            itertr += 1
            ut = np.copy(btras1)
            for k in range(self.npri):
                for i in range(self.nnod):
                    if self.idboc[i] != 1:
                        ut[i, k] = ut[i, k] + self.r[i, k]

            for k in range(self.npri):
                cc = np.copy(ut[:, k])
                if xita2 == 0.0:
                    for i in range(self.nnod):
                        if self.idboc[i] != 1:
                            cc[i] = cc[i] * dt / ptra[i]
                else:
                    cc = SoluteTransport.lu_subs(gptflw, self.nnod, self.nbands, cc, w)

                ut[:, k] = np.copy(cc)

            # The following is to loop each node for chemical calculation
            errumax = 0.0
            for i in range(self.nnod):
                # assign temperature to the node
                # tc2 = self.tc2
                erru = 0.0

                if (ispia == 1 and icall[i] == 0) or (self.idboc[i] == 1):
                    continue
                else:
                    # InitializingChemicalSystem
                    # for n in range(npri):
                    self.tt = ut[i, :]
                    for m in range(self.nmin):
                        self.tt = self.tt + self.stqm[m, :] * self.p[i, m]
                    for m in range(self.ngas):
                        self.tt = self.tt + self.stqg[m, :] * self.g[i, m]
                    for m in range(self.nads):
                        self.tt = self.tt + self.stqd[m, :] * self.d[i, m]
                    for m in range(self.nexc):
                        self.tt = self.tt + self.stqx[m, :] * self.x[i, m]

                    self.ct = np.copy(self.c[i, :])

                    self.cm = np.copy(self.p[i, :])
                    self.cg = np.copy(self.g[i, :])
                    self.cx = np.copy(self.x[i, :])
                    self.cec2 = self.cec[i]
                    self.phi2 = self.porosity[i]  # porosity, should be renamed

                    self.cd = np.copy(self.d[i, :])  # the amount of surface complex
                    self.phip2 = self.phip[
                        i
                    ]  # surface potential node wise should be updated late
                    self.tads2 = self.tads[i]  # adsorption capacity,
                    self.supadn2 = self.supadn[i]  # surface area for the adsorption
                    # Solve the chemical equations
                    self.solve_chemical_equilibrium(maxitpch, tolch, i)

                    for n in range(self.npri):
                        for m in range(self.nmin):
                            dum = (self.cm[m] - self.p[i, m]) * self.volum[i]
                            self.r[i, n] = self.r[i, n] - self.stqm[m, n] * dum / dt
                        for m in range(self.ngas):
                            dum = (self.cg[m] - self.g[i, m]) * self.volum[i]
                            self.r[i, n] = self.r[i, n] - self.stqg[m, n] * dum / dt
                        for m in range(self.nads):
                            dum = (self.cd[m] - self.d[i, m]) * self.volum[i]
                            self.r[i, n] = self.r[i, n] - self.stqd[m, n] * dum / dt
                        for m in range(self.nexc):
                            dum = (self.cx[m] - self.x[i, m]) * self.volum[i]
                            self.r[i, n] = self.r[i, n] - self.stqx[m, n] * dum / dt

                    for n in range(self.npri):
                        diff = abs(self.u2[n] - self.utem[i, n])
                        dum = abs(self.u2[n] + self.utem[i, n]) / 2.0

                        if dum > 1.0e-25:
                            diff = diff / dum

                        erru = max(diff, erru)
                        errumax = max(diff, errumax)

                    if erru <= toltr:
                        icall[i] = 0

                    self.c[i, :] = np.copy(self.ct)
                    self.utem[i, :] = np.copy(self.u2)

                    self.si[i, :] = self.si2
                    self.p[i, :] = self.cm
                    self.g[i, :] = self.cg
                    self.x[i, :] = self.cx
                    self.d[i, :] = self.cd
                    self.phip[i] = self.phip2

            # end loop for each node

            # Here check condition for while loop
            if itertr > maxitptr:
                raise RuntimeError("The transport convergence problems!")

        return

    # NEWTONEQ
    def solve_chemical_equilibrium(self, maxitpch, tolch, i_node=0):
        """
        Solves the chemical equilibrium for the current chemical system using an iterative Newton-Raphson approach.
        This method updates the concentrations of primary, secondary, and gas species to achieve chemical equilibrium
        within a specified tolerance. The Jacobian matrix is recalculated at each iteration, and the solution is
        updated until convergence or until the maximum number of iterations is reached.
        Parameters
        ----------
        maxitpch : int
            Maximum number of iterations allowed for the chemical equilibrium solver.
        tolch : float
            Convergence tolerance for the relative error in the primary species concentrations.
        i_node : int, optional
            Index of the node for which the chemical equilibrium is being solved (default is 0).
        Raises
        ------
        RuntimeError
            If the solver fails to converge within the specified maximum number of iterations.
        Notes
        -----
        - The method updates the concentrations in-place.
        - The function assumes that all necessary system matrices and vectors (e.g., amat, bmat, ct, cm, cg) are properly initialized.
        - After convergence, the concentrations of aqueous species are recalculated.
        """

        if self.naqx == 0 and self.nmin == 0 and self.nexc == 0 and self.nads == 0:
            facmax = 1000.0
        else:
            facmax = 0.5
        kjacob = 0
        # cpold = np.copy(self.ct[:self.npri])
        # csold = np.copy(self.ct[self.npri:])

        # errmax = tolch + 1.0
        iterch = 0

        for _ in range(maxitpch):
            iterch += 1
            kjacob += 1
            self.calc_chemical_equilibrium(i_node)
            self.calc_jacobian_matrix()
            cp = self.ct[: self.npri]
            for i in range(self.npri):
                for j in range(self.npri):
                    self.amat[i, j] = self.amat[i, j] * cp[j]
            cc = scipy.linalg.solve(self.amat, self.bmat)
            for i in range(self.npri):
                cc[i] = cc[i] * cp[i]
            errmax = 0.0
            for i in range(self.npri):
                errx = abs(cc[i] / self.ct[i])
                errmax = max(errx, errmax)
            if errmax > facmax:
                cc = cc * facmax / errmax
            self.ct[: self.npri] = self.ct[: self.npri] + cc[: self.npri]
            errmaxp = 0.0
            for m in range(self.nsat):
                self.cm[self.isat[m]] = self.cm[self.isat[m]] + cc[self.npri + m]
                errmaxp = max(abs(cc[self.npri + m]), errmaxp)
            for m in range(self.ngas):
                self.cg[m] = self.cg[m] + cc[self.npri + self.nsat + m]
            if errmax < tolch:
                break

        if iterch > maxitpch:
            raise RuntimeError("Convergence problem for chemical calculation!")

        ## SHould update ct
        self.calc_aquspecies_conc()
        return

        # chemeq

    def calc_chemical_equilibrium(self, i_node=0):
        """
        Calculates the chemical equilibrium state for the system at a given node.
        This method performs a sequence of calculations to determine the equilibrium concentrations
        and related properties for aqueous species, minerals, gases, exchange sites, and adsorbed species.
        It updates the system's state by computing activities, concentrations, and their derivatives,
        as well as saturation indices for minerals and gases, and handles special cases for exchange
        and adsorption processes.
        Parameters:
            i_node (int, optional): Index of the node for which to calculate equilibrium. Defaults to 0.
        Side Effects:
            Updates internal state variables related to activities, concentrations, and their derivatives
            for aqueous species, minerals, gases, exchange sites, and adsorbed species.
        """

        debye_huckel_dict = self.calc_activity()
        self.calc_ddh_dcp(debye_huckel_dict)

        self.calc_aquspecies_conc()
        self.calc_dcs_dcp()

        self.calc_ddh_dcp(debye_huckel_dict)

        if self.nmin > 0:
            # Calcualte saturation indices of minerals for the initial condition
            #  and derivatives of saturation indices
            self.calc_cm_cp()

        if self.ngas > 0:
            # Calcualte saturation indices of gases for the inital condition
            #  and derivatives of saturation indices
            self.calc_cg_cp()

        if self.nexc > 0:
            if self.cec2 == 0.0:
                self.cx = np.zeros(self.nexc)
            else:
                self.calc_cx_ct(i_node)
                self.calc_dcx_dcp(i_node)
        if self.nads > 0:
            if self.tads2 == 0.0:
                self.cd = np.zeros(self.nads)
                self.dcd = np.zeros((self.nads, self.npri))
            else:
                self.calc_adsorption()

    # Jacobeq
    def calc_jacobian_matrix(self):
        """
        Calculates the Jacobian matrix and the corresponding right-hand side vector (bmat) for the chemical system.
        This method constructs the Jacobian matrix (`amat`) and the vector (`bmat`) required for solving the system of nonlinear equations
        that describe the chemical equilibrium of the system, including aqueous, mineral, gas, exchange, and adsorption phases.
        The procedure includes:
            - Checking the saturation status of minerals and updating relevant counters and indices.
            - Initializing the Jacobian matrix (`amat`) and the right-hand side vector (`bmat`) with appropriate dimensions.
            - Filling in the Jacobian matrix with derivatives from aqueous, exchange, and adsorption reactions.
            - Populating the right-hand side vector with the difference between current and target values, including contributions from all phases.
            - Adding terms for saturated minerals and gases.
            - Handling special cases, such as adsorption sites, if present.
        Attributes Modified:
            self.nmat (int): Updated number of matrix rows/columns for the Jacobian.
            self.nsat (int): Number of saturated minerals.
            self.isat (np.ndarray): Indices of saturated minerals.
            self.amat (np.ndarray): The Jacobian matrix.
            self.bmat (np.ndarray): The right-hand side vector.
        Notes:
            - Assumes all required attributes (such as `npri`, `nmin`, `ngas`, `du2`, `stqx`, etc.) are already initialized.
            - The function is designed for internal use within the chemical system solver.
        """

        # Check mineral status
        self.nmat = np.copy(self.npri)
        self.nsat = 0
        isat = np.zeros(self.nmin, dtype=int)
        for m in range(self.nmin):
            if self.si2[m] <= 1.0 and self.cm[m] < 1.0e-15 or self.mout[m] == 1:
                self.cm[m] = 0.0
            else:
                self.isat[self.nsat] = m
                self.nsat += 1
                self.nmat += 1

        nmat = self.nmat + self.ngas
        ntot = self.npri + self.nmin + self.ngas
        self.amat = np.zeros((ntot, ntot))
        self.bmat = np.zeros(ntot)

        for i in range(self.npri):
            for j in range(self.npri):
                self.amat[i, j] = self.du2[i, j]
                for k in range(self.nexc):
                    self.amat[i, j] = self.amat[i, j] + self.stqx[k, i] * self.dcx[k, j]
                for k in range(self.nads):
                    self.amat[i, j] = self.amat[i, j] + self.stqd[k, i] * self.dcd[k, j]

        ## The term bmat
        for i in range(self.npri):
            self.bmat[i] = self.u2[i] - self.tt[i]
            for m in range(self.nmin):
                self.bmat[i] = self.bmat[i] + self.stqm[m, i] * self.cm[m]
            for m in range(self.ngas):
                self.bmat[i] = self.bmat[i] + self.stqg[m, i] * self.cg[m]
            for m in range(self.nexc):
                self.bmat[i] = self.bmat[i] + self.stqx[m, i] * self.cx[m]
            for m in range(self.nads):
                self.bmat[i] = self.bmat[i] + self.stqd[m, i] * self.cd[m]
            self.bmat[i] = -1.0 * self.bmat[i]

        # The alfa term (nsat)
        for i in range(self.npri, self.npri + self.nsat):
            m = self.isat[i - self.npri]
            for j in range(self.npri):
                self.amat[i, j] = self.stqm[m, j]

        for i in range(self.npri):
            for j in range(self.npri, self.npri + self.nsat):
                m = self.isat[j - self.npri]
                self.amat[i, j] = self.stqm[m, i]

        # The alfa term (ngas)
        for i in range(self.npri + self.nsat, nmat):
            m = i - (self.npri + self.nsat)
            for j in range(self.npri):
                self.amat[i, j] = self.stqg[j, j]
        for i in range(self.npri):
            for j in range(self.npri + self.nsat, nmat):
                self.amat[i, j] = self.stqg[j, i]

        # The independent term for(nsat)
        for i in range(self.npri, self.npri + self.nsat):
            m = isat[i - self.npri]
            self.bmat[i] = -(self.si2[m] - 1.0)

        # The independent term (ngas)
        for i in range(self.npri + self.nsat, nmat):
            m = i - (self.npri + self.nsat)
            self.bmat[i] = -(self.sig2[m] - 1.0)

        # If the adsorption is included
        nd = self.special_elements_dict.get("'xoh'", -1)
        if nd > 0:
            for j in range(nmat):
                self.amat[nd, j] = 0.0
            self.amat[nd, nd] = 1.0
            self.bmat[nd] = 0.0

    def calc_cm_cp(self):
        """
        Calculates the secondary species concentrations (`si2`) and their derivatives (`dsi2`)
        with respect to the primary species concentrations in a chemical system.
        This method performs the following steps:
        1. Initializes the secondary species concentration array (`si2`) to zeros.
        2. Copies the current primary species concentrations (`ct`), activity coefficients (`gamt`),
           and their derivatives (`dgamt`) for computation.
        3. For each secondary species:
            - Computes the logarithmic sum of the primary concentrations and activity coefficients,
              weighted by the stoichiometric coefficients (`stqm`).
            - Adjusts by the equilibrium constant (`ekm`) and exponentiates to obtain `si2`.
        4. Initializes the derivative array (`dsi2`) to zeros.
        5. For each secondary species and primary species:
            - Computes the partial derivatives of `si2` with respect to each primary concentration,
              considering both direct and activity coefficient contributions.
        Assumes the following instance attributes are defined:
            - nmin: Number of secondary species.
            - npri: Number of primary species.
            - ct: Array of total concentrations for primary species.
            - gamt: Array of activity coefficients for primary species.
            - dgamt: 2D array of derivatives of activity coefficients.
            - stqm: Stoichiometric matrix (secondary x primary).
            - ekm: Array of equilibrium constants for secondary species.
        Updates:
            - self.si2: Array of calculated secondary species concentrations.
            - self.dsi2: Array of derivatives of secondary concentrations with respect to primary concentrations.
        """

        self.si2 = np.zeros(self.nmin)
        cp = np.copy(self.ct[: self.npri])
        gamp = np.copy(self.gamt[: self.npri])
        dgamp = np.copy(self.dgamt[: self.npri, :])

        for m in range(self.nmin):
            paim = 0.0
            for i in range(self.npri):
                paim = paim + self.stqm[m, i] * (np.log(cp[i]) + np.log(gamp[i]))
            self.si2[m] = paim - self.ekm[m]
            self.si2[m] = np.exp(self.si2[m])

        self.dsi2 = np.zeros((self.nmin, self.npri))
        for m in range(self.nmin):
            for i in range(self.npri):
                self.dsi2[m, i] = self.si2[m] * self.stqm[m, i] / cp[i]
                for k in range(self.npri):
                    self.dsi2[m, i] += (
                        self.si2[m] * self.stqm[m, k] * dgamp[k, i] / gamp[k]
                    )

    def calc_cg_cp(self):
        """
        Calculates the chemical potential and its derivatives for each gas component.
        This method computes the following:
        - `self.sig2`: An array representing the chemical potential (or related property) for each gas.
        - `self.cgpres`: An array representing the pressure contribution for each gas.
        - `self.dsig2`: The derivatives of `sig2` with respect to the primary components.
        The calculations use the current state of the system, including concentrations (`ct`),
        activity coefficients (`gamt`), their derivatives (`dgamt`), and stoichiometric coefficients (`stqg`).
        The method also accounts for special cases where the node concentration (`cgnode`) is zero or negative.
        Assumes the following instance attributes are defined:
            - ngas: Number of gas components.
            - npri: Number of primary components.
            - ct: Array of concentrations of primary components.
            - gamt: Array of activity coefficients for primary components.
            - dgamt: Matrix of derivatives of activity coefficients.
            - stqg: Stoichiometric coefficients matrix for gases and primary components.
            - ekg: Array of energy constants for each gas.
            - cgnode: Array of node concentrations for each gas.
        Returns:
            None. Updates instance attributes in-place.
        """

        self.sig2 = np.zeros(self.ngas)
        self.cgpres = np.zeros(self.ngas)
        cp = np.copy(self.ct[: self.npri])
        gamp = np.copy(self.gamt[: self.npri])
        dgamp = np.copy(self.dgamt[: self.npri, :])

        for m in range(self.ngas):
            paig = 0.0
            for i in range(self.npri):
                paig = paig + self.stqg[m, i] * (np.log(cp[i]) + np.log(gamp[i]))
            self.sig2[m] = paig - self.ekg[m]
            self.sig2[m] = np.exp(self.sig2[m])

            if self.cgnode[m] <= 0.0:
                self.sig2[m] = 1.0
            else:
                self.sig2[m] = paig - np.log(self.cgnode[m]) - self.ekg[m]
            self.cgpres[m] = np.exp(paig - self.ekg[m])

        self.dsig2 = np.zeros((self.ngas, self.npri))
        for m in range(self.ngas):
            if self.cgnode[m] > 0.0:
                for i in range(self.npri):
                    self.dsig2[m, i] = self.sig2[m] * self.stqg[m, i] / cp[i]
                    for k in range(self.npri):
                        self.dsig2[m, i] += (
                            self.sig2[m] * self.stqg[m, k] * dgamp[k, i] / gamp[k]
                        )

    def calc_adsorption(self, maxitpad=1000, tolads=1.0e-4):
        """
        Calculates the adsorption equilibrium using an iterative approach.
        This method computes the adsorption of ions onto a surface by iteratively solving
        for the surface concentration and potential, considering electrostatic effects and
        mass balance constraints. The calculation uses the Debye-Hückel theory for activity
        corrections and updates the surface charge and potential until convergence.
        Parameters
        ----------
        maxitpad : int, optional
            Maximum number of iterations for the adsorption calculation (default is 1000).
        tolads : float, optional
            Tolerance for convergence of the adsorption calculation (default is 1.0e-4).
        Raises
        ------
        SystemExit
            If the adsorption site index is not found or if the calculation does not converge
            within the maximum number of iterations.
        Notes
        -----
        - Updates internal state variables such as surface concentration and potential.
        - Relies on several instance attributes and methods, including `calc_activity`,
          `calc_cd_cp`, and `calc_dcd_dcp`.
        - Prints error messages and exits if critical errors are encountered.
        """

        t = self.tc2 + 273.15
        # double layer thickness (dm)
        cp = np.copy(self.ct[: self.npri])
        debye_huckel_dict = self.calc_activity()

        ion_strength = debye_huckel_dict["ionStrength"]
        cappainv = 3.05 * 1.0e-9 / np.sqrt(ion_strength)
        # Calculate alpha term
        FARADAY = 96485.3090
        RGAS = 8.314510
        EPSI = 7.08e-11
        adfactor = cappainv * FARADAY / (EPSI * self.supadn2 * RGAS * t)
        nd = self.special_elements_dict.get("'xoh'", -1)

        if nd < 0:
            print("Something wrong with adsorption calculation!")
            raise RuntimeError("Something wrong with adsorption calculation!")
        else:
            s = self.ct[nd]

        iterad = 0
        dphip2 = 1.0
        while iterad < maxitpad:
            iterad += 1
            self.calc_cd_cp(adfactor)
            if iterad == 1:
                dphip2 = self.phip2new - self.phip2
            sumy = 0.0
            sumy = sumy + np.sum(self.cd)

            fna2 = sumy + s - self.tads2

            sumzy = 0.0
            for k in range(self.nads):
                sumzy = sumzy + self.zd[k] * self.cd[k]

            sumnuy = 0.0
            for k in range(self.nads):
                sumnuy = sumnuy + self.stqd[k, nd] * self.cd[k]

            ds = -(sumzy * dphip2 + fna2) / (sumnuy / s + 1.0)
            s2 = s / 2.0
            if ds < 0 and abs(ds) >= s2:
                ds = -s2
            s = s + ds
            dsre = ds / s

            fna1 = self.phip2new + adfactor * sumzy
            sumzhzy = 0
            for k in range(self.nads):
                sumzhzy = sumzhzy + self.zd[k] * self.zd[k] * self.cd[k]

            sumznuy = 0
            for k in range(self.nads):
                sumznuy = sumznuy + self.zd[k] * self.stqd[k, nd] * self.cd[k]
            dphip2 = -(adfactor * sumznuy * ds / s + fna1) / (adfactor * sumzhzy + 1.0)
            self.phip2new = self.phip2new + dphip2
            cp[nd] = s
            self.phip2 = np.copy(self.phip2new)
            if iterad > maxitpad:
                print("No convergence for adsorption calculation!")
                raise RuntimeError("No convergence for adsorption calculation!")
            if abs(dphip2) <= tolads and abs(dsre) <= tolads:
                break

        self.calc_cd_cp(adfactor)
        self.calc_dcd_dcp()

    def calc_dcd_dcp(self):
        """
        Calculates the partial derivatives of the concentration differences (dcd) with respect to the primary component concentrations (dcp).
        This method updates the `self.dcd` array, where each element [k, i] represents the derivative of the concentration difference for adsorbed species `k` with respect to the primary component `i`. The calculation uses the current values of `cd`, `stqd`, `ct`, `gamt`, and `dgamt` attributes.
        The computation involves:
            - A direct term proportional to the ratio of the adsorbed concentration and stoichiometric coefficient to the primary component concentration.
            - A correction term involving the derivative of the activity coefficient matrix.
        Assumes that the following attributes are defined and properly shaped:
            - self.nads: Number of adsorbed species.
            - self.npri: Number of primary components.
            - self.cd: Array of adsorbed concentrations.
            - self.stqd: Stoichiometric coefficient matrix.
            - self.ct: Array of total concentrations.
            - self.gamt: Array of activity coefficients.
            - self.dgamt: Matrix of derivatives of activity coefficients.
            - self.dcd: Output array for the computed derivatives.
        Returns:
            None. The results are stored in `self.dcd`.
        """

        # self.dcd = np.zeros((self.nads, self.npri))
        gamp = np.copy(self.gamt[: self.npri])
        dgamp = np.copy(self.dgamt[: self.npri, :])
        cp = np.copy(self.ct[: self.npri])
        for k in range(self.nads):
            for i in range(self.npri):
                self.dcd[k, i] = self.cd[k] * self.stqd[k, i] / cp[i]
                for j in range(self.npri):
                    self.dcd[k, i] = (
                        self.dcd[k, i]
                        + self.cd[k] * self.stqd[k, j] * dgamp[j, i] / gamp[j]
                    )

    def calc_cd_cp(self, adfactor):
        """
        Calculates the adsorption concentrations (`cd`) and updates the electrostatic potential (`phip2new`)
        for the chemical system based on the provided adsorption factor.
        Parameters
        ----------
        adfactor : float
            Adsorption factor used in the calculation of the new electrostatic potential.
        Updates
        -------
        self.cd : np.ndarray
            Updated adsorption concentrations for each adsorbed species.
        self.phip2new : float
            Updated electrostatic potential based on the new adsorption concentrations.
        Notes
        -----
        - Uses current values of `gamt`, `ct`, `ekd`, `stqd`, `zd`, and `phip2` from the instance.
        - The calculation involves logarithmic and exponential transformations for each adsorbed species.
        """

        gamp = np.copy(self.gamt[: self.npri])
        cp = np.copy(self.ct[: self.npri])
        for k in range(self.nads):
            self.cd[k] = self.ekd[k] * -1.0
            for i in range(self.npri):
                self.cd[k] = self.cd[k] + self.stqd[k, i] * (
                    np.log(cp[i]) + np.log(gamp[i])
                )
            self.cd[k] = self.cd[k] + self.zd[k] * self.phip2
            self.cd[k] = np.exp(self.cd[k])

        self.phip2new = 0.0
        for k in range(self.nads):
            self.phip2new = self.phip2new - adfactor * self.zd[k] * self.cd[k]

    def calc_cx_ct(self, i_node=0):
        """
        Calculates the equivalent fractions (bx) and adsorbed concentrations (cx) of exchangeable ions
        for a given node in a chemical system, based on the current state of the system and the selected
        ion exchange convention (Gaines-Thomas, Vanselow, or Gapon).
        The function iteratively solves for the equivalent fraction of the reference cation exchanger,
        then computes the fractions and concentrations for all exchangers. It checks for convergence
        based on changes in selectivity coefficients.
        Parameters
        ----------
        i_node : int, optional
            Index of the node for which the calculation is performed (default is 0).
        Notes
        -----
        - The function updates self.cx with the calculated adsorbed concentrations.
        - The function assumes that the system attributes (such as self.nx, self.nbx, self.z, self.ekx,
          self.ct, self.gamt, self.cec2, self.porosity, etc.) are properly initialized.
        - The function will terminate the program if invalid exchanger charges or fractions are detected.
        - The calculation method depends on the ion exchange convention specified by self.iex:
            1: Gaines-Thomas
            2: Vanselow
            3: Gapon
        Returns
        -------
        None
            The function updates the object's state in-place.
        """

        # the first exchanger will be the reference cation for nx
        nx = self.nx
        nbx = np.copy(self.nbx)
        for j in range(self.nexc):
            if self.z[self.nbx[j]] < 0:
                print("Charge of exchangers can not be negative!")
                sys.exit()
            # the exchange coeficient for primary adsorbate should be 1.0

        #    if ind_c == 1:
        # ekx = Calc_SelectCoef(indicator, nexc, aekx, ceca)
        # else:
        # ekx = calc_select_coef(indicator, self.nexc, self.aekx, ceca)

        # the terms of addition of total eq. fraction as a funtion of bx(nx)
        bx = np.zeros(self.nexc)
        # cx = np.zeros(self.nexc)  # Unused variable
        # cx removed (unused)

        tol_xchanger = 0.5
        check_xchanger = 0.6
        while check_xchanger > tol_xchanger:

            a1 = 0.0
            a2 = 0.0
            a3 = 0.0
            #       Gaines-Thomas and Vanselow conventions
            dum = np.zeros(self.nexc)
            if self.iex in [1, 2]:
                for j in range(self.nexc):
                    z_ratio = self.z[nbx[j]] / self.z[nbx[nx]]
                    idx_j = nbx[j]
                    idx_nx = nbx[nx]

                    dum[j] = self.ekx[j] ** (-self.z[idx_j]) * (
                        self.ct[idx_j]
                        * self.gamt[idx_j]
                        * (self.ct[idx_nx] * self.gamt[idx_nx]) ** (-z_ratio)
                    )
                    if z_ratio == 1.0:
                        a1 += dum[j]
                    if z_ratio == 2.0:
                        a2 += dum[j]
                    if z_ratio == 3.0:
                        a3 += dum[j]
                #   resolution of: a1*bx(nx) + a2*bx(nx)**2 + a3*bx(nx)**3 - 1.0 = 0
                if a3 == 0.0:
                    if a2 == 0.0:
                        if a1 != 0.0:
                            bx[nx] = 1.0 / a1
                    else:
                        bx[nx] = (-a1 + np.sqrt(a1 * a1 + 4.0 * a2)) / 2.0 / a2
                else:
                    if a1 == 0.0 and a2 == 0.0:
                        bx[nx] = (1.0 / a3) ** (1.0 / 3.0)
                    else:
                        p1 = a1 / a3
                        p2 = a2 / a3
                        p0 = -1.0 / a3
                        z1, z2, z3 = ChemicalSystem.calculate_cubic(p2, p1, p0)
                        if (
                            0.0 < z1 < 1.0
                            and 0.0 < z2 < 1.0
                            and abs(z1 - z2) / z1 > 1.0e-3
                        ):
                            print("something wrong with exchanger!")
                            sys.exit()
                        if (
                            0.0 < z1 < 1.0
                            and 0.0 < z3 < 1.0
                            and abs(z1 - z3) / z1 > 1.0e-3
                        ):
                            print("something wrong with exchanger!")
                            sys.exit()
                        if (
                            0.0 < z3 < 1.0
                            and 0.0 < z2 < 1.0
                            and abs(z3 - z2) / z3 > 1.0e-3
                        ):
                            print("something wrong with exchanger!")
                            sys.exit()

                        bx[nx] = z1
                        if 0 < z2 < 1.0:
                            bx[nx] = z2
                        if 0.0 < z3 < 1.0:
                            bx[nx] = z3
            else:
                # Gapon convention
                for j in range(self.nexc):
                    dum[j] = self.ekx[j] ** (-1.0) + (
                        self.ct[nbx[j]] * self.gamt[nbx[j]]
                    ) ** (1.0 / self.z[nbx[j]]) * (
                        self.ct[nbx[nx]] * self.gamt[nbx[nx]]
                    ) ** (
                        -1.0 / self.z[nbx[nx]]
                    )
                    a1 = a1 + dum[j]
                bx[nx] = 1.0 / a1

            if bx[nx] > 1.0 or bx[nx] < 0.0:
                print("something wrong with exchanger!")
                sys.exit()
            # the rest of eq. fractions as function of bx(nx)

            for j in range(self.nexc):
                if self.iex == 1 or self.iex == 2:
                    bx[j] = dum[j] * bx[nx] ** (self.z[nbx[j]] / self.z[nbx[nx]])
                else:
                    bx[j] = dum[j] * bx[nx]

            #       conversion of bx (eq. fraction) into cx (mol solute ads/dm3 sol)

            cecmol = (
                self.cec2
                * 2.65
                * (1 - self.porosity[i_node])
                / (self.porosity[i_node] * 100.0)
            )

            for j in range(self.nexc):
                # Gaines - Thomas and Gapon conventions
                if self.iex == 1 or self.iex == 3:
                    self.cx[j] = bx[j] * cecmol / self.z[nbx[j]]
                elif self.iex == 2:
                    self.cx[j] = bx[j] * cecmol

            ekxold = np.copy(self.ekx)

            # ekx = calc_select_coef(indicator, nexc, aekx, bx)
            check_xchanger = 0.0
            for k in range(self.nexc):
                aaa = 2.0 * abs(ekxold[k] - self.ekx[k]) / (ekxold[k] + self.ekx[k])
                check_xchanger = max(aaa, check_xchanger)

        return

    def calc_dcx_dcp(self, i_node=0):
        """
        Calculates the numerical derivatives of the concentrations (cx) with respect to the primary concentrations (cp)
        using finite differences, and stores the results in the dcx array.
        Args:
            i_node (int, optional): Index of the node for which the calculation is performed. Defaults to 0.
        Notes:
            - The method perturbs each primary concentration by a small amount (1.0e-7), recalculates the dependent
              concentrations, and computes the derivative as the difference quotient.
            - The results are stored in self.dcx, where dcx[j, i] represents the derivative of cx[j] with respect to cp[i].
            - The method assumes that self.calc_cx_ct(i_node) updates self.cx based on the current self.ct.
            - The original concentrations are restored after each perturbation.
        """

        cxold = np.copy(self.cx)
        ct = np.copy(self.ct)
        cp = np.copy(ct[: self.npri])
        nexc = self.nexc
        for i in range(self.npri):
            dd = cp[i] * 1.0e-7
            cp[i] = cp[i] + dd
            self.ct[i] = cp[i]

            self.calc_cx_ct(i_node)

            for j in range(nexc):
                self.dcx[j, i] = (self.cx[j] - cxold[j]) / dd
                self.cx[j] = cxold[j]

            cp[i] = cp[i] - dd
            self.ct[i] = cp[i]

    def calc_select_coef(self, inddd, ccc, aekx):
        """
        Calculates the selectivity coefficients for each exchange site.
        Parameters:
            inddd (int): Index indicator used to determine whether to exponentiate the result.
            ccc (array-like): Array of concentration values for each exchange site.
            aekx (ndarray): 2D array of coefficients with shape (nexc, 4), where nexc is the number of exchange sites.
        Returns:
            np.ndarray: Array of calculated selectivity coefficients for each exchange site.
        Notes:
            - For each exchange site j, the selectivity coefficient is calculated as:
                ekx[j] = aekx[j, 0] + aekx[j, 1] * ccc[j] + aekx[j, 2] * ccc[j]**2 + aekx[j, 3] * ccc[j]**3
            - If inddd is not equal to self.nexc, the result is exponentiated.
        """

        ekx = np.zeros(self.nexc)
        for j in range(self.nexc):
            ekx[j] = aekx[j, 0] + (
                aekx[j, 1] * ccc[j]
                + aekx[j, 2] * ccc[j] * ccc[j]
                + aekx[j, 3] * ccc[j] * ccc[j] * ccc[j]
            )
            if inddd != self.nexc:
                ekx[j] = np.exp(ekx[j])
        return ekx

    @staticmethod
    def calculate_cubic(a, b, c):
        """
        Solves the cubic equation z^3 + a*z^2 + b*z + c = 0 for its three roots using an iterative method.
        Args:
            a (float): Coefficient of z^2.
            b (float): Coefficient of z.
            c (float): Constant term.
        Returns:
            tuple: A tuple (z1, z2, z3) containing the three roots of the cubic equation.
        Note:
            This function uses a Newton-Raphson iterative approach to approximate two roots (z1 and z2),
            and computes the third root (z3) using the relationship between the roots and coefficients.
        """

        z = 1
        while True:
            f = z * z * z + a * z * z + b * z + c
            h = f / (3 * z * z + 2 * a * z + b)
            if abs(h / z) < 1.0e-4:
                z = z - h
                break
            z = z - h
        z1 = z
        z = 0.01
        while True:
            f = z * z * z + a * z * z + b * z + c
            h = f / (3 * z * z + 2 * a * z + b)
            if abs(h / z) <= 1.0e-4:
                z = z - h
                break
            z = z - h
        z2 = z
        z3 = -a - z1 - z2
        return z1, z2, z3

    # End of file. (No additional code needed here.)
