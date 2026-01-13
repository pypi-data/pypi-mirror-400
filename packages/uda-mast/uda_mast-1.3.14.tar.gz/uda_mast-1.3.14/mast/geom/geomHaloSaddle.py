import numpy as np

from collections import namedtuple
from .geometry import GeometryData
from .geometryUtils import cartesian_cylindrical, cylindrical_cartesian


class GeomHaloSaddle(GeometryData):
    """
    Manipulation class for Halo and Saddle loops

    Implements:
    - plot: 2D R-Z and 3D plots
    - _convert_coords_loop : Converts halo and saddle loop co-ordinates cartesian <=> cylindrical

    """

    def _convert_coords_loop(self, data, cartesian=True):
        """
         Convert co-ordinates from cylindrical to cartesian or vice-versa.
         Recursive function, walks the tree to find attributes that match them being co-ordinates
         ie. x, y, z OR R,Z,phi OR r,z,phi attributes exist.
         :param data: instance of StructuredWritable to traverse
         :param cartesian: if set to True looks for cylindrical co-ordinates to convert. Otherwise looks for cartesian co-oridnates to convert.
         :return:
         """

        Point3DCart = namedtuple('Point3DCart', ['x', 'y', 'z'])
        Point3DCyl = namedtuple('Point3DCyl', ['r', 'z', 'phi'])

        if not cartesian and hasattr(data, 'x') and hasattr(data, 'y') and hasattr(data, 'z'):

            try:
                all_r = np.zeros(len(data.turns_x))
                all_r[:] = np.nan
                all_phi = np.zeros(len(data.turns_x))
                all_phi[:] = np.nan

                for x,y,z in zip(data.x, data.y, data.z):
                    coord_cylindrical = cartesian_cylindrical(Point3DCart(x=x, y=y, z=z), phi_degrees=True)
                    all_r[i] = coord_cylindrical[0]
                    all_phi[i] = coord_cylindrical[2]
            except TypeError:
                coord_cylindrical = cartesian_cylindrical(data, phi_degrees=True)
                all_r = coord_cylindrical[0]
                all_phi = coord_cylindrical[2]

            data.delete_attr('x')
            data.delete_attr('y')

            data.add_attr('r', all_r)
            data.add_attr('phi', all_phi)
        elif cartesian and ((hasattr(data, 'R') and hasattr(data, 'Z') and hasattr(data, 'phi'))
                            or (hasattr(data, 'r') and hasattr(data, 'z') and hasattr(data, 'phi'))):

            try:
                all_x = np.array([])
                all_y = np.array([])
                all_z = data.z

                for r,z,phi in zip(data.r, data.z, data.phi):
                    coord_cartesian = cylindrical_cartesian(Point3DCyl(r=r,z=z,phi=phi), phi_degrees=True)
                    all_x = np.append(all_x, coord_cartesian[0])
                    all_y = np.append(all_y, coord_cartesian[1])

            except TypeError:
                coord_cartesian = cylindrical_cartesian(data, phi_degrees=True)
                all_x = coord_cartesian[0]
                all_y = coord_cartesian[1]
                all_z = data.z

            data.delete_attr('R')
            data.delete_attr('r')
            data.delete_attr('Z')
            data.delete_attr('z')
            data.delete_attr('phi')

            data.add_attr('x', all_x)
            data.add_attr('y', all_y)
            data.add_attr('z', all_z)
        else:
            for child in data.children:
                self._convert_coords_loop(child, cartesian=cartesian)

    def _walk_tree_plot(self, data, ax_2d, ax_3d, color="green"):
        """
        Walk tree to plot all halo and saddle loops in tree
        :param data: data structure to walk
        :param ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param ax_3d: ax_2d: matplotlib.axes._subplots.Axes3DSubplot for 3D plot
        :param color: colour of loops for plotting
        :return:
        """

        Point3DCart = namedtuple('Point3DCart', ['x', 'y', 'z'])
        Point3DCyl = namedtuple('Point3DCyl', ['r', 'z', 'phi'])

        halo_type = None
        saddle_type = None

        try:
            halo_type = data.haloType
        except AttributeError:
            try:
                saddle_type = data.saddleType
            except:
                for child in data.children:
                    self._walk_tree_plot(child, ax_2d, ax_3d, color=color)

        if halo_type is not None or saddle_type is not None:

            try:
                coil_r = data["coilPath"].r
                coil_z = data["coilPath"].z
                coil_phi = data["coilPath"].phi
                coil_x = np.array([])
                coil_y = np.array([])

                for r, z, phi in zip(coil_r, coil_z, coil_phi):
                    xyz = cylindrical_cartesian(Point3DCyl(r=r,z=z,phi=phi), phi_degrees=True)
                    coil_x = np.append(coil_x, xyz[0])
                    coil_y = np.append(coil_y, xyz[1])

            except AttributeError:
                coil_x = data["coilPath"].x
                coil_y = data["coilPath"].y
                coil_z = data["coilPath"].z
                coil_r = np.array([])
                coil_phi = np.array([])

                for x, y, z in zip(coil_x, coil_y, coil_z):
                    rzphi = cartesian_cylindrical(Point3DCart(x=x, y=y, z=z), phi_degrees=True)
                    coil_r = np.append(coil_r, rzphi[0])
                    coil_phi = np.append(coil_phi, rzphi[2])

            # PLOTTING
            if halo_type is not None and ax_2d is not None:

                if halo_type == "LOOP":
                    marker = None
                else:
                    marker = 'o'

                ax_2d.plot(coil_r, coil_z, color=color, marker=marker)

            elif saddle_type is not None and ax_2d is not None:
                if data.saddleType == "CURVED":
                    ax_2d.plot(coil_r, coil_z, color=color)
                else:
                    # bother
                    min_z = np.min(coil_z)
                    max_z = np.max(coil_z)
                    plot_z = [min_z, max_z]
                    plot_r = [np.max(coil_r[np.isclose(coil_z, min_z)]),
                              np.min(coil_r[np.isclose(coil_z, max_z)])]


                    ax_2d.plot(plot_r, plot_z, color=color)

            if halo_type is not None and ax_3d is not None:
                if halo_type == "LOOP":
                    # Add start point to end to draw complete loop
                    coil_x = np.append(coil_x, coil_x[0])
                    coil_y = np.append(coil_y, coil_y[0])
                    coil_z = np.append(coil_z, coil_z[0])

                ax_3d.plot(coil_x, coil_y, coil_z, color=color)

            elif saddle_type is not None and ax_3d is not None:

                coil_x = np.append(coil_x, coil_x[0])
                coil_y = np.append(coil_y, coil_y[0])
                coil_z = np.append(coil_z, coil_z[0])

                ax_3d.plot(coil_x, coil_y, coil_z, color=color)


    def plot(self, ax_2d=None, ax_3d=None, show=True, color="magenta"):
        """
        Plot in R-Z and 3D
        :param ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param ax_3d: ax_2d: matplotlib.axes._subplots.Axes3DSubplot for 3D plot
        :param show: display plots
        :param color: color of loops
        :return:
        """

        data = self.data

        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        # Create axes if necessary
        if ax_2d is None:
            fig = plt.figure()
            if ax_2d is None:
                ax_2d = fig.add_subplot(121)

        if ax_3d is None:
            fig2 = plt.figure()
            ax_3d = fig2.add_subplot(111, projection='3d')

        self._walk_tree_plot(data, ax_2d, ax_3d, color=color)

        if show:
            plt.show()