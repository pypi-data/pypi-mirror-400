import sys
import os
import numpy as np
import pandas as pd


from ..grids.grid import Elements


class SatFlow(Elements):
    """
    Main class for saturated flow simulation, combining elements and nodes.
    """

    def __init__(
        self,
        nodes_df: pd.DataFrame,
        element_df: pd.DataFrame,
        aqu_parameters: pd.DataFrame,
        converge_tolerance: pd.DataFrame,
        flow_controls: pd.DataFrame,
        boundary_functions: dict,
        gflw: np.array,
        pflw: np.array,
        bflw: np.array,
    ):
        super().__init__(nodes_df, element_df)
        self.aqu_parameters = aqu_parameters
        self.converge_tolerance = converge_tolerance
        self.ioflu = flow_controls.loc["val", "ioflu"]
        self.iotpa = flow_controls.loc["val", "iotpa"]
        self.xita1 = flow_controls.loc["val", "xita1"]
        self.xita2 = flow_controls.loc["val", "xita2"]
        self.nboundfh = boundary_functions["numberBoundFunction"].loc["val", "nboundfh"]
        if self.nboundfh > 0:
            self.boundfh = boundary_functions["BoundFunH"].values
        else:
            self.boundfh = np.array([])

        self.gflw = gflw
        self.pflw = pflw
        self.bflw = bflw
        # self.hp, self.q1, self.rch = self.update_boundh()
        # self.q2 = self.area_recharge()

    def update_boundh(self, itime):
        """
        Updates boundary head, point recharge, and area recharge values for the current time period.
        This method recalculates the hydraulic head (`hp`), point recharge (`q1`), and area recharge (`rch`)
        for each node and element based on the specified boundary factors for the given time index (`itime`).
        The update is performed by applying a weight, which is either 1 (if no boundary/recharge factor is specified)
        or the corresponding value from the `boundfh` array (indexed by `itime` and the factor index minus one).
        Parameters
        ----------
        itime : int
            The current time period index for which to update the boundary and recharge values.
        Notes
        -----
        - The method assumes that boundary and recharge factor indices in `iq` and `irech` start from 1 in the input file.
        - If the index is 0, a default weight of 1 is used (i.e., no modification).
        - The arrays `hp`, `q1`, and `rch` are updated in-place.
        """

        # update boundary and point and area recharge at each time period
        for i in range(self.nnod):
            iqf = self.iq[i]
            if iqf == 0:
                weight = 1
            else:
                weight = self.boundfh[
                    itime, iqf - 1
                ]  # start with 1 in the input file and should subtract 1
            self.hp[i] = self.hpv[i] * weight
            self.q1[i] = self.q1v[i] * weight

        for l in range(self.nele):
            irchf = self.irech[l]
            if irchf == 0:
                weight = 1
            else:
                weight = self.boundfh[
                    itime, irchf - 1
                ]  # start with 1 in the input file and should subtract 1
            self.rch[l] = self.rechv[l] * weight

    def area_recharge(self):
        """
        Distributes recharge values over the nodes of each element.
        For each element in the mesh, this method iterates over its three nodes and adds a portion of the element's recharge,
        weighted by the element's area, to the corresponding node's recharge accumulator (`self.q2`). The recharge for each
        node is calculated as (element area * element recharge) / 3, ensuring the total recharge is evenly distributed among
        the three nodes of the element.
        Assumes:
            - `self.nele`: Number of elements.
            - `self.node`: 2D array mapping elements to their node indices.
            - `self.area`: Array of element areas.
            - `self.rch`: Array of recharge values per element.
            - `self.q2`: Array of recharge accumulators per node.
        """

        for l in range(self.nele):
            for k in range(3):
                i = self.node[l, k]  # subtract 1
                self.q2[i] = self.q2[i] + self.area[l] * self.rch[l] / 3

    def flow_sat(self, it, dt, istep):
        """
        Simulates saturated groundwater flow for a confined aquifer.
        This method updates the hydraulic head and distributes water volume to nodes
        for a single time step in a confined aquifer system. It recalculates conductance
        and storage matrices, applies boundary conditions, solves the groundwater flow
        equations, and updates node volumes based on porosity and aquifer thickness.
        Parameters
        ----------
        it : int
            Current iteration number.
        dt : float
            Time step size.
        istep : int
            Current time step index.
        Returns
        -------
        h : numpy.ndarray
            Updated hydraulic head values for all nodes.
        """

        # update thickness for unconfined aquifer
        # tolfl = self.converge_tolerance.loc['val','tolfl']
        # maxitpfl = self.converge_tolerance.loc['val','maxitpfl']
        por = self.aqu_parameters.loc[:, "por"].tolist()

        h = np.copy(self.h0)
        # thickk = np.copy(self.thick)

        if self.iotpa == 0:  # for confined aquifer
            if (self.nboundfh > 0.0 and istep == 0) or it == 1:
                ## calcualte conductance and storage matrices
                self.hh_matrix()
                ## count boundary conditions
                gflw_udpated = self.hh_bound()
                self.gflw = np.copy(gflw_udpated)

                # count storage and initial condition, solve equations
        h = self.hh_solve(dt)
        # self.h0 = h.copy()

        ## distribute water volume to nodes
        volum = np.zeros(self.nnod)

        for l in range(self.nele):
            matl = self.mat[l] - 1
            voluml = self.area[l] * self.thickk[l] * por[matl]
            for l1 in range(3):
                mm = self.node[l, l1]
                volum[mm] = volum[mm] + voluml / 3.0

        return h

    def __repr__(self):
        return f"SatFlow(attributes={vars(self)})"

    def hh_matrix(self):
        """
        Constructs the storage and conductance matrices for a confined groundwater flow model.
        This method computes and populates the storage matrix (`self.pflw`) and the conductance matrix (`self.gflw`)
        based on the aquifer parameters, geometry, and material properties for each element in the model domain.
        The calculations account for anisotropic hydraulic conductivity, element orientation, and storage coefficients.
        The method uses the following attributes:
            - self.aqu_parameters: DataFrame containing aquifer parameters ('pk1', 'pk2', 'angle', 'ss').
            - self.nbands: Number of bands for the banded matrix storage.
            - self.nnod: Number of nodes in the model.
            - self.nele: Number of elements in the model.
            - self.area: Array of element areas.
            - self.thickk: Array of element thicknesses.
            - self.mat: Array of material indices for each element.
            - self.iotpa: Integer flag indicating area calculation mode.
            - self.bc: Boundary condition coefficients for each element.
            - self.node: Node indices for each element.
        Side Effects:
            - Updates self.pflw (1D array): Storage matrix for each node.
            - Updates self.gflw (2D array): Conductance matrix in banded storage format.
        Returns:
            None
        """

        pk1 = self.aqu_parameters.loc[:, "pk1"].tolist()
        pk2 = self.aqu_parameters.loc[:, "pk2"].tolist()
        angle = self.aqu_parameters.loc[:, "angle"].tolist()
        ss = self.aqu_parameters.loc[:, "ss"].tolist()

        nbands = self.nbands
        nbandt = 2 * self.nbands + 1
        # set initial values of matrice
        self.pflw = np.zeros(self.nnod)
        self.gflw = np.zeros((self.nnod, nbandt))

        for l in range(self.nele):
            areath = self.area[l] * self.thickk[l]
            matl = self.mat[l] - 1  # start from 1 and should be subtracted 1
            areas = self.area[l] * ss[matl]
            if self.iotpa == 0:
                areas = areas * self.thickk[l]
            ang = angle[matl] * np.pi / 180.0
            sina = np.sin(ang)
            cosa = np.cos(ang)
            sin2 = sina * sina
            cos2 = cosa * cosa
            pkxx = pk1[matl] * cos2 + pk2[matl] * sin2
            pkyy = pk1[matl] * sin2 + pk2[matl] * cos2
            pkxy = (pk1[matl] - pk2[matl]) * sina * cosa

            for l1 in range(3):
                b1 = self.bc[l, l1]
                ll1 = l1 + 3
                c1 = self.bc[l, ll1]
                mm = self.node[l, l1]
                ## construct storage matrix
                self.pflw[mm] = self.pflw[mm] + areas / 3
                for l2 in range(3):
                    b2 = self.bc[l, l2]
                    ll2 = l2 + 3
                    c2 = self.bc[l, ll2]
                    nn = self.node[l, l2]
                    nn1 = nbands + nn - mm
                    ## build conductance matrix
                    self.gflw[mm, nn1] = self.gflw[mm, nn1] + (
                        areath
                        * (pkxx * b1 * b2 + pkxy * (b1 * c2 + b2 * c1) + pkyy * c1 * c2)
                    )

    def hh_bound(self):
        """
        Updates the banded flow matrix and right-hand side vector for boundary conditions.
        This method modifies the banded flow matrix (`gflw`) and the right-hand side vector (`bflw`)
        based on the type of boundary condition specified for each node. The boundary conditions are
        determined by the `idbh` array:
            - If `idbh[i] == 1`: Dirichlet (fixed head) boundary condition is applied at node `i`.
            - If `idbh[i] == 3`: Cauchy (third-type) boundary condition is applied at node `i`.
            - Otherwise: Internal or Neumann (flux) condition is applied.
        The method updates:
            - `gflw_updated`: The banded flow matrix with boundary conditions applied.
            - `bflw`: The right-hand side vector for the linear system.
        Returns:
            np.ndarray: The updated banded flow matrix (`gflw_updated`) with boundary conditions applied.
        """

        nbands = self.nbands
        nbandt = 2 * nbands + 1
        self.bflw = np.copy(self.q2)
        gflw_updated = self.gflw.copy()
        for i in range(self.nnod):
            if self.idbh[i] == 1:
                for j in range(nbandt):
                    gflw_updated[i, j] = 0.0
                gflw_updated[i, nbands] = 1.0
                self.bflw[i] = self.hp[i]
            elif self.idbh[i] == 3:
                gflw_updated[i, nbands] = gflw_updated[i, nbands] + self.alfa[i]
                self.bflw[i] = self.alfa[i] * self.hp[i]
            else:
                self.bflw[i] = self.bflw[i] + self.q1[i]

        return gflw_updated

    def hh_solve(self, dt):
        """
        Solves the groundwater head for a confined flow system using a banded matrix approach.
        This method updates the hydraulic head values (`self.h0`) for the current time step
        by assembling and solving a system of linear equations that represent the groundwater
        flow in a confined aquifer. The method supports different numerical schemes and
        accounts for storage and boundary conditions.
        Parameters
        ----------
        dt : float
            The time step size for the simulation.
        Returns
        -------
        h : numpy.ndarray
            The computed hydraulic head values at the current time step.
        Notes
        -----
        - The method modifies internal state variables such as `self.h0`.
        - The solution approach depends on the values of `self.ioflu` and `self.xita1`.
        - Uses a banded matrix solver (`SatFlow.solver`) for efficient computation.
        - Handles both explicit and implicit numerical schemes.
        """

        nbands = self.nbands
        nbandt = 2 * self.nbands
        gptflw = np.copy(self.gflw)
        # multiple numerical scheme factor for coefficient matrix
        if self.ioflu == 1 and self.xita1 < 1.0:
            for i in range(self.nnod):
                if self.idbh[i] != 1:
                    for j in range(nbandt):
                        gptflw[i, j] = self.xita1 * gptflw[i, j]
        ## add storage term to coefficient matrix
        if self.ioflu == 1:
            for i in range(self.nnod):
                if self.idbh[i] != 1:
                    gptflw[i, nbands] = gptflw[i, nbands] + self.pflw[i] / dt
        # get values from hh_bound for independent term
        h = np.copy(self.bflw)

        # count numerical scheme for independnet term
        if self.ioflu == 1 and self.xita1 < 1.0:
            for i in range(self.nnod):
                if self.idbh[i] != 1:
                    for j in range(nbandt):
                        j1 = j + i - nbands - 1
                        h[i] = h[i] - self.xita1 * gptflw[i, j] * self.h0[j1]
        # count initial head for independent term of linear equations
        if self.ioflu == 1:
            for i in range(self.nnod):
                if self.idbh[i] != 1:
                    h[i] = h[i] + self.pflw[i] * self.h0[i] / dt
        # solve linear equations of flow
        if self.ioflu == 1 and self.xita1 == 0:
            for i in range(self.nnod):
                if self.idbh[i] != 1:
                    h[i] = h[i] / self.pflw[i]

            return h

        h = SatFlow.solver(self.nnod, self.nbands, gptflw, h)
        self.h0 = h.copy()

        return h

    @staticmethod
    def solver(n, nb, a, b):
        """
        Solves a banded linear system using LU decomposition and forward/backward substitution.
        Parameters:
            n (int): The size of the system (number of equations).
            nb (int): The half-bandwidth of the banded matrix (number of sub-diagonals or super-diagonals).
            a (np.ndarray): The banded coefficient matrix of shape (n, 2*nb+1) or similar, where each row contains the relevant banded entries.
            b (np.ndarray): The right-hand side vector of length n.
        Returns:
            np.ndarray: The solution vector to the linear system.
        Notes:
            - The function modifies the input arrays `a` and `b` in place.
            - The matrix `a` is assumed to be stored in a banded format.
            - This implementation is specialized for banded matrices and may not work for general dense matrices.
        """

        nb1 = nb + 1
        ## lu decomposition
        w = np.zeros((n, nb1))
        # nb1 = nb + 1
        for i in range(n):
            for j in range(nb):
                l = nb + j
                mink = min(n - 1, i + j + nb1)
                for k in range(i + 1, mink):
                    m = i - k + nb1 - 1
                    if m == -1:
                        break
                    w[k, m] = a[k, m] / a[i, nb]
                    a[k, l] = a[k, l] - w[k, m] * a[i, j + nb1]
                    l = l - 1
                    if l == -1:
                        break
        ##preliminary substitution
        for i in range(n):
            s = b[i]
            maxj = max(0, i - nb)
            for j in range(maxj, i):
                k = j + nb1 - i - 1
                s = s - w[i, k] * b[j]
            b[i] = s
        ## final substitution
        for i in range(n - 1, -1, -1):
            s = b[i]
            minj = min(i + nb, n - 1)
            for j in range(i + 1, minj + 1):
                l = j - i + nb1 - 1
                s = s - a[i, l] * b[j]
            b[i] = s / a[i, nb]

        return b

    @staticmethod
    def lu_disc(a, n, nb):
        """
        Performs LU decomposition for solving banded equations.
        This static method decomposes a given banded matrix `a` into its LU components,
        specifically tailored for banded matrices, and returns the modified matrix `a`
        along with the computed lower triangular matrix `w`.
        Args:
            a (np.ndarray): The banded matrix to decompose, expected to be a 2D NumPy array.
            n (int): The size of the matrix (number of rows/columns).
            nb (int): The bandwidth of the matrix.
        Returns:
            Tuple[np.ndarray, np.ndarray]: A tuple containing:
                - The modified matrix `a` after LU decomposition.
                - The lower triangular matrix `w` containing multipliers used during decomposition.
        Note:
            This function modifies the input matrix `a` in place.
        """
        # lu discomposition(only) for solving banded equations

        nb1 = nb + 1
        w = np.zeros((n, nb))
        for i in range(n):
            for j in range(nb):
                l = nb + j
                upk = min(n, i + j + nb1 - 1)
                for k in range(i + 1, upk):
                    m = i - k + nb1
                    if m != 0:
                        w[k, m] = a[k, m] / a[i, nb1]
                        a[k, l] = a[k, l] - w[k, m] * a[i, j + nb1]
                        l = l - 1
                        if l == 0:
                            break

        return a, w

    @staticmethod
    def lu_subs(a, n, nb, b, w):
        """
        Performs LU substitution to solve a system of linear equations, typically arising from banded matrices in transport equations.
        Parameters:
            a (np.ndarray): The upper triangular matrix (or banded matrix) from LU decomposition.
            n (int): The size of the system (number of equations).
            nb (int): The bandwidth of the matrix.
            b (np.ndarray): The right-hand side vector, which will be overwritten with the solution.
            w (np.ndarray): The lower triangular matrix (or banded matrix) from LU decomposition.
        Returns:
            np.ndarray: The solution vector, with the same shape as `b`.
        """

        # lu substitution for solving transport equations

        nb1 = np.copy(nb)
        for i in range(n):
            s = b[i]
            maxj = max(1, i - nb)
            for j in range(maxj, i - 1):
                k = j + nb1 - i
                s = s - w[i, k] * b[j]
            b[i] = s
        for i in range(n - 1, -1, -1):
            s = b[i]
            minj = min(i + nb, n)
            for j in range(i + 1, minj):
                l = j - i + nb1
                s = s - a[i, l] * b[j]
            b[i] = s / a[i, nb1]

        return b


## End of module
