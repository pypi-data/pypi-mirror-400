import pandas as pd
import numpy as np


class Nodes:
    """
    Represents mesh nodes for water flow simulation.
    """

    def __init__(self, nodes_df: pd.DataFrame):
        """
        Args:
            nodes_df: DataFrame with columns ['xx', 'y', 'hp', 'q1', ...]
        """
        self.xx = nodes_df["xx"].values
        self.y = nodes_df["y"].values
        self.hpv = nodes_df["hp"].values.copy()
        self.hp = nodes_df["hp"].values.copy()
        self.q1 = nodes_df["q1"].values.copy()
        self.q1v = nodes_df["q1"].values.copy()
        self.iq = nodes_df["iq"].values
        self.idbh = nodes_df["idbh"].values
        self.h0 = nodes_df["h0"].values
        self.alfa = nodes_df["alfa"].values
        self.idboc = nodes_df["idboc"].values
        self.izoneiw = nodes_df["izoneiw"].values
        self.izonebw = nodes_df["izonebw"].values
        self.izonerw = nodes_df["izonerw"].values
        self.izonem = nodes_df["izonem"].values
        self.izoneg = nodes_df["izoneg"].values
        self.izoned = nodes_df["izoned"].values
        self.izonex = nodes_df["izonex"].values
        self.nnod = self.xx.shape[0]
        self.h = self.h0.copy()
        self.volum = np.zeros(self.nnod)
        self.porosity = np.full(self.nnod, 0.3)
        self.phi2 = 0.3  # default value for porosity in chemical calculations
        self.q2 = np.zeros(self.nnod)

    def set_q2(self, q2):
        self.q2 = q2

    def get_h(self):
        return self.h

    def set_h(self, h):
        self.h = h

    def set_h0(self, h0):
        self.h0 = h0

    def get_h0(self):
        return self.h0

    def set_volum(self, volum):
        self.volum = volum

    def __repr__(self):
        return f"Nodes(attributes={vars(self)})"


class Elements(Nodes):
    """
    Represents mesh elements for water flow simulation.
    """

    def __init__(
        self,
        nodes_df: pd.DataFrame,
        element_df: pd.DataFrame,
    ):
        super().__init__(nodes_df)
        self.node = element_df[["node1", "node2", "node3"]].values
        self.thick = element_df["thick"].values
        self.mat = element_df["mat"].values
        self.rechv = element_df["rech"].values
        self.rch = element_df["rech"].values
        self.irech = element_df["irech"].values
        self.nele = self.node.shape[0]
        self.nbands = self.get_ele_bands()
        self.thickk = self.thick.copy()
        self.area = self.get_ele_area()
        self.bc = self.get_ele_matrix()
        self.calc_node_volume()

    def calc_node_volume(self):
        # Vectorized node volume calculation
        matl = self.mat.astype(int) - 1
        voluml = self.area * self.thickk * self.porosity[matl]
        # For each element, distribute 1/3 of its volume to each of its 3 nodes
        node_indices = self.node
        volum_contrib = (voluml / 3.0)[:, np.newaxis]
        np.add.at(self.volum, node_indices, volum_contrib)

    def get_ele_bands(self) -> int:
        """
        Returns the maximum band width among all elements.
        """
        diffs = np.abs(self.node[:, [0, 1, 2]] - self.node[:, [1, 2, 0]])
        return int(np.max(diffs))

    def get_ele_area(self):
        # Vectorized area calculation for all elements
        i = self.node[:, 0]
        j = self.node[:, 1]
        k = self.node[:, 2]
        ele_area = 0.5 * (
            self.xx[i] * self.y[j]
            - self.xx[j] * self.y[i]
            + self.xx[k] * self.y[i]
            - self.xx[i] * self.y[k]
            + self.xx[j] * self.y[k]
            - self.xx[k] * self.y[j]
        )
        if np.any(ele_area < 0):
            raise ValueError("Some area of triangle elements have negative area")
        return ele_area

    def __repr__(self):
        return f"Elements(attributes={vars(self)})"

    def get_ele_matrix(self):
        """
        Compute the element matrix for all elements in the grid.
        This method calculates the coefficients for each element in a vectorized manner,
        based on the coordinates of the nodes and the area of each element. The resulting
        matrix `bc` has shape (nele, 6), where each row corresponds to an element and
        contains the computed coefficients.
        Returns:
            np.ndarray: A (nele, 6) array containing the element matrix coefficients for all elements.
        """

        # Vectorized calculation of element matrix
        i = self.node[:, 0]
        j = self.node[:, 1]
        k = self.node[:, 2]
        area = self.area
        bc = np.empty((self.nele, 6))
        bc[:, 0] = 0.5 * (self.y[j] - self.y[k]) / area
        bc[:, 1] = 0.5 * (self.y[k] - self.y[i]) / area
        bc[:, 2] = 0.5 * (self.y[i] - self.y[j]) / area
        bc[:, 3] = 0.5 * (self.xx[k] - self.xx[j]) / area
        bc[:, 4] = 0.5 * (self.xx[i] - self.xx[k]) / area
        bc[:, 5] = 0.5 * (self.xx[j] - self.xx[i]) / area
        return bc

    def gridplot(self, xscale=1.0, yscale=1.0):
        """
        Plots the mesh grid using matplotlib.
        The plot is stretched by scaling the axis limits, not the node coordinates.
        """
        import matplotlib.pyplot as plt

        for l in range(self.nele):
            i = self.node[l, 0]
            j = self.node[l, 1]
            k = self.node[l, 2]
            x = [
                self.xx[i],
                self.xx[j],
                self.xx[k],
                self.xx[i],
            ]
            y = [
                self.y[i],
                self.y[j],
                self.y[k],
                self.y[i],
            ]
            plt.plot(x, y, "b-")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Mesh Grid")

        # Stretch axes by scaling the axis limits
        x_min, x_max = np.min(self.xx), np.max(self.xx)
        y_min, y_max = np.min(self.y), np.max(self.y)
        plt.xlim(x_min, x_min + (x_max - x_min) * xscale)
        plt.ylim(y_min, y_min + (y_max - y_min) * yscale)

        # plt.axis("equal")  # Commented out to allow stretching
        plt.show()

    def plot_material_zones(self, xscale=1.0, yscale=1.0):
        """
        Plots the mesh grid using matplotlib.
        The plot is stretched by scaling the axis limits, not the node coordinates.
        """
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import matplotlib.colors as mcolors

        # Normalize material values for colormap
        mats = self.mat
        unique_mats = np.unique(mats)
        cmap = plt.get_cmap("tab20", len(unique_mats))
        norm = mcolors.BoundaryNorm(
            boundaries=np.arange(len(unique_mats) + 1) - 0.5, ncolors=len(unique_mats)
        )

        # Map material values to color indices
        mat_to_color = {mat: idx for idx, mat in enumerate(unique_mats)}

        for l in range(self.nele):
            i = self.node[l, 0]
            j = self.node[l, 1]
            k = self.node[l, 2]
            x = [self.xx[i], self.xx[j], self.xx[k]]
            y = [self.y[i], self.y[j], self.y[k]]
            color_idx = mat_to_color[self.mat[l]]
            polygon = patches.Polygon(
                np.column_stack([x, y]),
                closed=True,
                facecolor=cmap(color_idx),
                edgecolor="k",
                linewidth=0.5,
                alpha=0.7,
            )
            plt.gca().add_patch(polygon)

        # Create a legend for material zones
        handles = [
            patches.Patch(color=cmap(mat_to_color[mat]), label=f"Mat {mat}")
            for mat in unique_mats
        ]
        plt.legend(
            handles=handles,
            title="Material Zones",
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
        )
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Mesh Grid")

        # Stretch axes by scaling the axis limits
        x_min, x_max = np.min(self.xx), np.max(self.xx)
        y_min, y_max = np.min(self.y), np.max(self.y)
        plt.xlim(x_min, x_min + (x_max - x_min) * xscale)
        plt.ylim(y_min, y_min + (y_max - y_min) * yscale)

        # plt.axis("equal")  # Commented out to allow stretching
        plt.show()
