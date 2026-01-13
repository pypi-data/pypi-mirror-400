import pandas as pd

import numpy as np


from ..grids.grid import Elements


class SoluteTransport(Elements):
    """
    Handles solute transport calculations for groundwater systems, including advection, dispersion,
    boundary conditions, and transport matrix assembly. Inherits mesh and geometry from Elements.
    """

    def __init__(
        self,
        nodes_df: pd.DataFrame,
        elements_df: pd.DataFrame,
        aqu_parameters: pd.DataFrame,
        converge_tolerance: pd.DataFrame,
        flow_controls: pd.DataFrame,
        boundary_functions: dict,
    ):
        """
        Initialize the SoluteTransport object with mesh, aquifer, and control parameters.

        Parameters:
            nodes_df (pd.DataFrame): Node data.
            elements_df (pd.DataFrame): Element data.
            aqu_parameters (pd.DataFrame): Aquifer parameters.
            converge_tolerance (pd.DataFrame): Convergence criteria.
            flow_controls (pd.DataFrame): Flow and transport controls.
            boundary_functions (dict): Piecewise boundary functions.
        """
        super().__init__(nodes_df, elements_df)
        self.aqu_parameters = aqu_parameters
        self.converge_tolerance = converge_tolerance
        self.flow_controls = flow_controls
        self.boundary_functions = boundary_functions
        self.dispmatrix = None

    def decompose_transport_matrix(self, dt, gtra, ptra, btras, u):
        """
        Decompose the solute transport matrix for time-stepping.

        Parameters:
            dt (float): Time step size.
            gtra (np.ndarray): Transport matrix.
            ptra (np.ndarray): Diagonal transport terms.
            btras (np.ndarray): Source/sink terms.
            u (np.ndarray): Current solution vector.
        Returns:
            tuple: (gptflw, btras1, w) - updated transport matrix, right-hand side, and LU factors.
        """

        nbands = self.nbands
        nbandt = nbands * 2 + 1
        nnod = self.nnod
        npri = btras.shape[1]
        gptflw = gtra.copy()
        xita2 = self.flow_controls.loc["val", "xita2"]
        idboc = self.idboc

        # Vectorized scaling for xita2 < 1
        if xita2 < 1.0:
            mask = idboc != 1
            gptflw[mask, :] *= xita2

        # Vectorized update for ptra
        mask = idboc != 1
        gptflw[mask, nbands] += ptra[mask] / dt

        w = np.zeros((nnod, nbands + 1))
        gptflw, w = SoluteTransport.lu_disc(gptflw, nnod, nbands)

        btras1 = btras.copy()

        if xita2 < 1.0:
            xita21 = 1.0 - xita2
            for k in range(npri):
                for i in range(nnod):
                    if idboc[i] != 1:
                        for j in range(nbandt):
                            j1 = j + i - nbandt
                            btras1[i, k] -= xita21 * gtra[i, j] * u[j1, k]

        for k in range(npri):
            for i in range(nnod):
                if idboc[i] != 1:
                    btras1[i, k] += u[i, k] * ptra[i] / dt

        return gptflw, btras1, w

    def __repr__(self):
        """
        Return a string representation of the SoluteTransport object.
        """
        return f"SoluteTransport(attributes={vars(self)})"

    def solute_matrix_boundary(self, gtra, q2, caudal, ub, ur):
        """
        Apply boundary conditions and recharge to the solute transport matrix and right-hand side.

        Parameters:
            gtra (np.ndarray): Transport matrix.
            q2 (np.ndarray): Recharge/source terms.
            caudal (np.ndarray): Nodal fluxes.
            ub (np.ndarray): Boundary concentrations.
            ur (np.ndarray): Recharge concentrations.
        Returns:
            tuple: (gtra_updated, btras) - updated matrix and right-hand side.
        """

        nbands = self.nbands
        nbandt = 2 * nbands + 1
        npri = ub.shape[1]
        nnod = self.nnod
        idboc = self.idboc
        gtra_updated = gtra.copy()
        gtra_updated[:, nbands] += q2

        for i in range(nnod):
            if idboc[i] == 1:  # first boundary condition
                for ii in range(nbandt):
                    gtra_updated[i, ii] = 0.0
                gtra_updated[i, nbands] = 1.0
            elif idboc[i] == 2 and caudal[i] > 0.0:
                gtra_updated[i, nbands] = gtra_updated[i, nbands] + caudal[i]

        ## for independent terms
        btras = np.zeros((nnod, npri))

        # recharge
        for k in range(npri):
            for i in range(nnod):
                btras[i, k] = 0.0
                if q2[i] > 0.0:
                    btras[i, k] = q2 * ur[ii, k]
        # for boundary
        for k in range(npri):
            for i in range(nnod):
                ii = self.izonebw[i] - 1
                if ii > -1:

                    if idboc[i] == 1:  # first boundary condition
                        btras[i, k] = ub[ii, k]
                    elif idboc[i] == 3:
                        btras[i, k] = btras[i, k] + ub[ii, k]
                    elif caudal[i] > 0.0:
                        btras[i, k] = btras[i, k] + caudal[i] * ub[ii, k]
        return gtra_updated, btras

    def calc_dispersivity(self, vd):
        """
        Calculate and store the dispersivity matrix for each element based on velocity and aquifer properties.

        Parameters:
            vd (np.ndarray): Darcy velocity for each element.
        """
        # Vectorized dispersivity calculation
        dfm = self.aqu_parameters.loc[:, "dfm"].values
        dsl = self.aqu_parameters.loc[:, "dsl"].values
        dst = self.aqu_parameters.loc[:, "dst"].values
        por = self.aqu_parameters.loc[:, "por"].values
        nele = self.nele
        matl = self.mat.astype(int) - 1
        tortu = np.power(por[matl], 7.0 / 3.0) / (por[matl] * por[matl])
        dfml = tortu * dfm[matl] * por[matl]
        qx2 = vd[:, 0] ** 2
        qy2 = vd[:, 1] ** 2
        qxy = vd[:, 0] * vd[:, 1]
        qsum = qx2 + qy2
        if np.any(qsum < 0):
            raise ValueError("Negative dispersivity encountered!")
        qnor = np.sqrt(qsum)
        mask = qnor > 1.0e-20
        qx2_norm = np.zeros_like(qx2)
        qy2_norm = np.zeros_like(qy2)
        qxy_norm = np.zeros_like(qxy)
        qx2_norm[mask] = qx2[mask] / qnor[mask]
        qy2_norm[mask] = qy2[mask] / qnor[mask]
        qxy_norm[mask] = qxy[mask] / qnor[mask]
        # For zero velocity, leave as zero and optionally warn
        if not np.all(mask):
            print("Warning: zero velocity encountered in some elements.")
        self.dispmatrix = np.zeros((nele, 3))
        self.dispmatrix[:, 0] = dfml + dsl[matl] * qx2_norm + dst[matl] * qy2_norm
        self.dispmatrix[:, 2] = dfml + dst[matl] * qx2_norm + dsl[matl] * qy2_norm
        self.dispmatrix[:, 1] = dfml + (dsl[matl] - dst[matl]) * qxy_norm

    def proc_solute_transport_matrix(self, vd):
        """
        Assemble the global solute transport matrix and diagonal terms for the current mesh and velocity.

        Parameters:
            vd (np.ndarray): Darcy velocity for each element.
        Returns:
            tuple: (ptra, gtra) - diagonal and banded transport matrices.
        """
        # dismatrix[nele,0] -> dxx, dismatrix[nele,1] -> dxy , dismatrix[nele,2] -> dyy
        nbands = self.nbands
        nbandt = 2 * nbands + 1
        nele = self.nele
        nnod = self.nnod
        ptra = np.zeros(nnod)
        gtra = np.zeros((nnod, nbandt))
        por = self.aqu_parameters.loc[:, "por"].tolist()

        for l in range(nele):
            matl = self.mat[l] - 1
            rc = self.thickk[l] * por[matl] * self.area[l]
            i = self.node[l, 0]
            j = self.node[l, 1]
            k = self.node[l, 2]
            bi = self.bc[l, 0]
            bj = self.bc[l, 1]
            bk = self.bc[l, 2]
            ci = self.bc[l, 3]
            cj = self.bc[l, 4]
            ck = self.bc[l, 5]
            ptra[i] = ptra[i] + rc / 3.0
            ptra[j] = ptra[j] + rc / 3.0
            ptra[k] = ptra[k] + rc / 3.0

            disp12 = (
                (
                    self.dispmatrix[l, 0] * bi * bj
                    + self.dispmatrix[l, 2] * ci * cj
                    + self.dispmatrix[l, 1] * (bi * cj + bj * ci)
                )
                * self.area[l]
                * self.thickk[l]
            )

            disp13 = (
                (
                    self.dispmatrix[l, 0] * bi * bk
                    + self.dispmatrix[l, 2] * ci * ck
                    + self.dispmatrix[l, 1] * (bi * ck + bk * ci)
                )
                * self.area[l]
                * self.thickk[l]
            )

            disp23 = (
                (
                    self.dispmatrix[l, 0] * bj * bk
                    + self.dispmatrix[l, 2] * cj * ck
                    + self.dispmatrix[l, 1] * (bj * ck + bk * cj)
                )
                * self.area[l]
                * self.thickk[l]
            )

            vdx = vd[l, 0]
            vdy = vd[l, 1]
            adv1 = (bi * vdx + ci * vdy) * self.area[l] * self.thickk[l] / 3
            adv2 = (bj * vdx + cj * vdy) * self.area[l] * self.thickk[l] / 3
            adv3 = (bk * vdx + ck * vdy) * self.area[l] * self.thickk[l] / 3
            i12 = nbands - i + j
            i21 = nbands - j + i
            i13 = nbands - i + k
            i31 = nbands - k + i
            i23 = nbands - j + k
            i32 = nbands - k + j
            gtra[i, i12] = gtra[i, i12] + disp12 + adv2
            gtra[j, i21] = gtra[j, i21] + disp12 + adv1
            gtra[i, i13] = gtra[i, i13] + disp13 + adv3
            gtra[k, i31] = gtra[k, i31] + disp13 + adv1
            gtra[j, i23] = gtra[j, i23] + disp23 + adv3
            gtra[k, i32] = gtra[k, i32] + disp23 + adv2
            gtra[i, nbands] = gtra[i, nbands] - disp12 - disp13 + adv1
            gtra[j, nbands] = gtra[j, nbands] - disp12 - disp23 + adv2
            gtra[k, nbands] = gtra[k, nbands] - disp13 - disp23 + adv3

        return ptra, gtra

    def calc_darcy_velocity(self, q1, hp, h):
        """
        Calculate Darcy velocity and nodal fluxes for each element and node.

        Parameters:
            q1 (np.ndarray): Initial nodal fluxes.
            hp (np.ndarray): Previous head values.
            h (np.ndarray): Current head values.
        Returns:
            tuple: (vd, caudal) - element velocities and updated nodal fluxes.
        """

        pk1 = self.aqu_parameters.loc[:, "pk1"].tolist()
        pk2 = self.aqu_parameters.loc[:, "pk2"].tolist()
        angle = self.aqu_parameters.loc[:, "angle"].tolist()
        # ss = aqu_parameters.loc[:,'ss'].tolist()
        # por = self.aqu_parameters.loc[:,'por'].tolist()

        nnod = self.nnod
        nele = self.nele
        pkrel = np.zeros(nele)
        for l in range(nele):
            matl = self.mat[l] - 1
            pkrel[l] = 1.0
        # caudal = np.zeros(nnod)
        caudal = np.copy(q1)
        vd = np.zeros((nele, 2))
        for i in range(nnod):

            caudal[i] = caudal[i] + self.alfa[i] * (hp[i] - h[i])

        for l in range(nele):
            matl = self.mat[l] - 1
            ang = angle[matl]
            ang = ang * np.pi / 180.0
            sina = np.sin(ang)
            cosa = np.cos(ang)
            sin2 = sina * sina
            cos2 = cosa * cosa
            pkxx = pkrel[l] * (pk1[matl] * cos2 + pk2[matl] * sin2)
            pkyy = pkrel[l] * (pk1[matl] * sin2 + pk2[matl] * cos2)
            pkxy = pkrel[l] * (pk1[matl] - pk2[matl]) * sina * cosa
            i = self.node[l, 0]
            j = self.node[l, 1]
            k = self.node[l, 2]
            bi = self.bc[l, 0]
            bj = self.bc[l, 1]
            bk = self.bc[l, 2]
            ci = self.bc[l, 3]
            cj = self.bc[l, 4]
            ck = self.bc[l, 5]
            v1 = bi * h[i] + bj * h[j] + bk * h[k]
            v2 = ci * h[i] + cj * h[j] + ck * h[k]
            vd[l, 0] = -(pkxx * v1 + pkxy * v2)
            vd[l, 1] = -(pkxy * v1 + pkyy * v2)
            areath = self.area[l] * self.thickk[l]
            emij = (
                pkxx * bi * bj + pkxy * (bi * cj + ci * bj) + pkyy * ci * cj
            ) * areath
            emik = (
                pkxx * bi * bk + pkxy * (bi * ck + ci * bk) + pkyy * ci * ck
            ) * areath
            emjk = (
                pkxx * bj * bk + pkxy * (bj * ck + cj * bk) + pkyy * cj * ck
            ) * areath
            if self.idbh[i] == 1:
                caudal[i] = caudal[i] - emij * (h[i] - h[j]) - emik * (h[i] - h[k])
            if self.idbh[j] == 1:
                caudal[j] = caudal[j] - emij * (h[j] - h[i]) - emjk * (h[j] - h[k])
            if self.idbh[k] == 1:
                caudal[k] = caudal[k] - emjk * (h[k] - h[j]) - emik * (h[k] - h[i])

        return vd, caudal

    def calc_peclect_courant(self, vd, dt):
        """
        Calculate maximum Peclet and Courant numbers for the mesh and time step.

        Parameters:
            vd (np.ndarray): Darcy velocity for each element.
            dt (float): Time step size.
        Returns:
            tuple: (pecl, cour) - maximum Peclet and Courant numbers.
        """
        pecl = 0.0
        cour = 0.0
        pecx = 0.0
        pecy = 0.0
        nele = self.nele
        por = self.aqu_parameters.loc[:, "por"].tolist()

        for n in range(nele):
            i = self.node[n, 0]
            j = self.node[n, 1]
            l = self.node[n, 2]
            c1 = abs(self.xx[l] - self.xx[j])
            c2 = abs(self.xx[i] - self.xx[l])
            c3 = abs(self.xx[j] - self.xx[i])
            b1 = abs(self.y[j] - self.y[l])
            b2 = abs(self.y[l] - self.y[i])
            b3 = abs(self.y[i] - self.y[j])
            delx = max(c1, c2, c3)
            dely = max(b1, b2, b3)
            if self.dispmatrix[n, 0] > 0.0:
                pecx = abs(vd[n, 0]) * delx / self.dispmatrix[n, 0]
            if self.dispmatrix[n, 2] > 0.0:
                pecy = abs(vd[n, 1]) * dely / self.dispmatrix[n, 2]
            pecl = max(pecl, pecx, pecy)
            matl = self.mat[n] - 1
            coux = abs(vd[n, 0]) * dt / (delx * por[matl])
            couy = abs(vd[n, 1]) * dt / (dely * por[matl])
            cour = max(cour, coux, couy)

        return pecl, cour

    def update_boundc(self, nbwtype, nrwtype, itime, ubv, urv, iub, iur):
        """
        Update boundary and recharge concentrations for the current time period.

        Parameters:
            nbwtype (int): Number of boundary types.
            nrwtype (int): Number of recharge types.
            itime (int): Current time index.
            ubv (np.ndarray): Boundary concentration values.
            urv (np.ndarray): Recharge concentration values.
            iub (np.ndarray): Boundary indices.
            iur (np.ndarray): Recharge indices.
        Returns:
            tuple: (ub, ur) - updated boundary and recharge concentrations.
        """
        ##-store the boundary and recharge conce. for permanent use
        ## the following should be moved to the upper level subroutine
        ub = ubv.copy()
        ur = urv.copy()

        nboundfc = self.boundary_functions["numberBoundFunction"].loc["val", "nboundfc"]
        if nboundfc > 0:
            boundfc = self.boundary_functions["BoundFunC"].values
        else:
            boundfc = None
        npri = ubv.shape[1]
        # --update boundary and recharge concentrations at each time period
        for i in range(nbwtype):
            for j in range(npri):
                iubf = iub[i, j]
                if iubf == 0:
                    weight = 1
                else:
                    if nboundfc > 0:
                        weight = boundfc[itime, iubf - 1]
                    else:
                        weight = 1
                ub[i, j] = ubv[i, j] * weight

        for i in range(nrwtype):
            for j in range(npri):
                iurf = iur[i, j]
                if iurf == 0:
                    weight = 1
                else:
                    if nboundfc > 0:
                        weight = boundfc[itime, iurf - 1]
                    else:
                        weight = 1
                ur[i, j] = urv[i, j] * weight  # for areal recharge concentrations

        return ub, ur

    # Transport equation solver
    def calc_transport(self, dt, ptra, btras1, gptflw, w):
        """
        Solve the transport equation for the current time step.

        Parameters:
            dt (float): Time step size.
            ptra (np.ndarray): Diagonal transport terms.
            btras1 (np.ndarray): Right-hand side/source terms.
            gptflw (np.ndarray): Transport matrix.
            w (np.ndarray): LU factors.
        Returns:
            np.ndarray: Updated solution vector for all nodes and species.
        """

        ut = btras1.copy()
        npri = btras1.shape[1]
        nnod = btras1.shape[0]
        nband = self.nbands
        idboc = self.idboc
        xita2 = self.flow_controls.loc["val", "xita2"]
        for k in range(npri):
            cc = np.copy(ut[:, k])
            if xita2 == 0.0:
                for i in range(nnod):
                    if idboc[i] != 1:
                        cc[i] = cc[i] * dt / ptra[i]
            else:
                cc = SoluteTransport.lu_subs(gptflw, nnod, nband, cc, w)

            ut[:, k] = np.copy(cc)
        return ut

    @staticmethod
    def lu_subs(A, N, NB, B, W):
        """
        LU substitution for solving transport equations.
        Parameters:
            A (np.ndarray): LU-decomposed matrix.
            N (int): Number of rows.
            NB (int): Bandwidth.
            B (np.ndarray): Right-hand side vector.
            W (np.ndarray): LU factors.
        Returns:
        """
        NB1 = np.copy(NB)
        B = np.copy(B)
        # Preliminary substitution (forward)
        for I in range(N):
            S = B[I]
            for J in range(max(0, I - NB), I):
                K = J + NB1 - I
                S = S - W[I, K] * B[J]
            B[I] = S

        # Final substitution (backward)
        for I in range(N - 1, -1, -1):
            S = B[I]
            for J in range(I + 1, min(I + NB + 1, N)):
                L = J - I + NB1
                S = S - A[I, L] * B[J]
            B[I] = S / A[I, NB1]
        return B

    @staticmethod
    def lu_disc(A, N, NB):
        """
        LU decomposition for banded matrices used in transport equations.
        Parameters:
            A (np.ndarray): Matrix to decompose.
            N (int): Number of rows.
            NB (int): Bandwidth.
        Returns:
            tuple: (A, W) - LU-decomposed matrix and factors.
        """
        W = np.zeros((N, NB + 1))
        NB1 = np.copy(NB)
        for I in range(N):
            for J in range(NB):
                L = NB + J
                for K in range(I + 1, min(N, I + J + NB1 + 1)):
                    M = I - K + NB1
                    if M < 0:
                        break
                    W[K, M] = A[K, M] / A[I, NB1]
                    A[K, L] = A[K, L] - W[K, M] * A[I, J + NB1 + 1]
                    #    fcc.write(
                    #                f'I={I:3d}, J={J:3d}, K={K:3d}, M={M:3d}, L={L:3d}, '
                    #                f'W[K, M]={W[K, M]:12.5e}, A[K, L]={A[K, L]:12.5e}, '
                    #                f'A[I, J + NB1]={A[I, J + NB1]:12.5e}, A[I, NB1]={A[I, NB1]:12.5e}\n'
                    #            )
                    L = L - 1
                    if L < 0:
                        break
        # No return needed; A and W are modified in place
        return A, W
