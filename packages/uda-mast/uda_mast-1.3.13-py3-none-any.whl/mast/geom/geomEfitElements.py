import math
import numpy as np

from .geometry import GeometryData


class GeomEfitElements(GeometryData):
    """
    Manipulation class for efit elements (ie. rectangles and parallelograms!).

    Implements:
    - plot: Plot EFIT elements in 2D R-Z plane
    - convert_to_vertices: Convert EFIT parallelogram/rectangle description to vertices
    """

    def get_element_vertices(self, centreR, centreZ, dR, dZ, a1, a2, version=0.0, close_shape=False):
        """
        Convert EFIT description of rectangles / parallelograms to vertices.

                    xxxx     ---             xxxxxxxxxxx
                xxxx   x      |            xx        xx
        --- xxxx       x      |          xx        xx
         |  x          x      dZ       xx        xx
         dZ x       xxxx      |      xx        xx
         |  x   xxxx   ^      |    xx        xx   ^
        --- xxxx    A1 )     --- xxxxxxxxxxxx A2 )
            |----dR----|         |-----dR---|

        :param centreR: R-position of centre of shape
        :param centreZ: Z-position of centre of shape
        :param dR: Width
        :param dZ: Height
        :param a1: angle1 as defined above. zero for rectangles
        :param a2: angle2 as defined above. zero for rectangles.
        :param version: geometry version (backwards compatibilty for bug in < V0.1
        :param close_shape: Repeat first vertex to close the shape if set to True
        :return:
        """
        if a1 == 0.0 and a2 == 0.0:
            # Rectangle
            rr = [centreR - dR / 2.0, centreR - dR / 2.0, centreR + dR / 2.0, centreR + dR / 2.0]
            zz = [centreZ - dZ / 2.0, centreZ + dZ / 2.0, centreZ + dZ / 2.0, centreZ - dZ / 2.0]
        elif version == 0.1:
            # Parallelogram
            Lx1 = (math.cos(math.radians(a1)) * dR)
            Lx2 = (math.sin(math.radians(a2)) * dZ)
            Lx = Lx1 + Lx2

            Lz1 = (math.sin(math.radians(a1)) * dR)
            Lz2 = (math.cos(math.radians(a2)) * dZ)
            Lz = Lz1 + Lz2

            rr = [centreR - Lx / 2,        # A
                  centreR - Lx / 2 + Lx2,  # B
                  centreR + Lx / 2,        # C
                  centreR - Lx / 2 + Lx1]  # D

            zz = [centreZ - Lz / 2,
                  centreZ - Lz / 2 + Lz2,
                  centreZ + Lz / 2,
                  centreZ - Lz / 2 + Lz1]
        else:
            # Parallelogram (different definitions of dR, dZ, angle1 and angle2)
            a1_tan = 0.0
            a2_tan = 0.0
            if a1 > 0.0:
                a1_tan = np.tan(a1 * np.pi / 180.0)

            if a2 > 0.0:
                a2_tan = 1.0 / np.tan(a2 * np.pi / 180.0)

            rr = [centreR - dR/2.0 - dZ/2.0 * a2_tan,
                  centreR + dR/2.0 - dZ/2.0 * a2_tan,
                  centreR + dR/2.0 + dZ/2.0 * a2_tan,
                  centreR - dR/2.0 + dZ/2.0 * a2_tan]

            zz = [centreZ - dZ/2.0 - dR/2.0 * a1_tan,
                  centreZ - dZ/2.0 + dR/2.0 * a1_tan,
                  centreZ + dZ/2.0 + dR/2.0 * a1_tan,
                  centreZ + dZ/2.0 - dR/2.0 * a1_tan]

        if close_shape:
            rr.append(rr[0])
            zz.append(zz[0])

        return (rr, zz)

    def convert_to_vertices(self, data=None, version=0.0, close_shapes=False):
        """
        Convert EFIT++ parallelograms and rectangles to vertices
        vertices added to data structure as 'vertices' attribute with shape (with close_shapes=False)
              (n_els, 4, 2) where (n_els, 4, 0) are R-coordinates
                                  (n_els, 4, 1) are Z-coordinates
        :param data: data structure for geomEfitElements
        :param version: machine description version. For backwards compatibility with <=V0.1
        :param close_shapes: Repeat first vertex to close the shape if set to True
        :return:
        """

        if data is None:
            data = self.data

        if hasattr(data, "version"):
            version = data.version

        if hasattr(data, 'centreR') and hasattr(data, 'centreZ'):

            centreRall = data.centreR
            centreZall = data.centreZ
            dRall = data.dR
            dZall = data.dZ

            try:
                angle1all = data.shapeAngle1
                angle2all = data.shapeAngle2
            except AttributeError:
                if hasattr(centreRall, "__len__"):
                    angle1all = np.zeros(len(centreRall))
                    angle2all = np.zeros(len(centreRall))
                else:
                    angle1all = 0.0
                    angle2all = 0.0

            try:
                n_els = len(centreRall)
            except TypeError:
                n_els = 1
                centreRall = [centreRall]
                centreZall = [centreZall]
                dRall = [dRall]
                dZall = [dZall]
                angle1all = [angle1all]
                angle2all = [angle2all]

            if close_shapes:
                vertices = np.zeros((n_els, 5, 2))
            else:
                vertices = np.zeros((n_els, 4, 2))

            for ind_el, (centreR, centreZ, dR, dZ, a1, a2) in enumerate(zip(centreRall, centreZall, dRall, dZall, angle1all, angle2all)):
                rr, zz = self.get_element_vertices(centreR, centreZ, dR, dZ, a1, a2, version=version)

                vertices[ind_el, 0:4, 0] = rr
                if close_shapes:
                    vertices[ind_el, 4, 0] = rr[0]
                vertices[ind_el, 0:4, 1] = zz
                if close_shapes:
                    vertices[ind_el, 4, 1] = zz[0]

            if hasattr(data, 'vertices'):
                data.vertices = vertices
            else:
                data.add_attr('vertices', vertices)
        else:
            for child in data.children:
                self.convert_to_vertices(version=version, data=child, close_shapes=close_shapes)

    def _plot_elements(self, data, ax_2d, color=None, version=0.0):
        """
        Recursively loop over tree, and retrieve element geometries.
        :param data: data tree (instance of StructuredWritable, with EFIT element tree structure)
        :return:
        """

        if color is None:
            color = "red"

        if hasattr(data, "version"):
            version = data.version

        if hasattr(data, "centreR"):
            centreRall = data.centreR
            centreZall = data.centreZ
            dRall = data.dR
            dZall = data.dZ

            # Try to retrieve angles (only parallelogram elements have this!)
            try:
                angle1all = data.shapeAngle1
                angle2all = data.shapeAngle2
            except AttributeError:
                if hasattr(centreRall, "__len__"):
                    angle1all = np.zeros(len(centreRall))
                    angle2all = np.zeros(len(centreRall))
                else:
                    angle1all = 0.0
                    angle2all = 0.0

            try:
                for centreR, centreZ, dR, dZ, a1, a2 in zip(centreRall, centreZall, dRall, dZall, angle1all, angle2all):
                    rr, zz = self.get_element_vertices(centreR, centreZ, dR, dZ, a1, a2, version=version, close_shape=True)
                    ax_2d.plot(rr, zz, color=color, linewidth=0.5)
                    ax_2d.plot(centreR, centreZ, marker="+", color=color, linewidth=0, markersize=1)

            except TypeError:
                rr, zz = self.get_element_vertices(centreRall, centreZall, dRall, dZall, angle1all, angle2all,
                                                       version=version, close_shape=True)
                ax_2d.plot(rr, zz, color=color, linewidth=0.5)
                ax_2d.plot(centreRall, centreZall, marker="+", color=color, linewidth=0, markersize=1)
        else:
            for child in data.children:
                self._plot_elements(child, ax_2d, color=color, version=version)

    def plot(self, ax_2d=None, show=True, color=None):
        """
        Plot the elements
        :param data: data tree (instance of StructuredWritable, with EFIT element tree structure)
        :param ax_2d: Axis on which to plot elements in R-Z (2D) plane.
                      If None, then an axis will be created.
        """
        import matplotlib.pyplot as plt

        data = self.data

        # Create axes if necessary
        if ax_2d is None:
            fig = plt.figure()
            if ax_2d is None:
                ax_2d = fig.add_subplot(111)

        # Plot
        if ax_2d is not None:
            self._plot_elements(data, ax_2d, color=color)

            ax_2d.set_xlabel('R [m]')
            ax_2d.set_ylabel('Z [m]')
            ax_2d.set_aspect('equal', 'datalim')

        if show:
            plt.show()


