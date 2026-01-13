import numpy as np
from collections import namedtuple

from .geometryUtils import cartesian_cylindrical, cylindrical_cartesian
from .geometry import GeometryData


class GeomElm(GeometryData):
    """
    Manipulation class for ELM coils.

    Manipulation:
    No manipulations are implemented for the ELM coils

    Plotting:
    The plot method will plot the ELM coil locations
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

        if not cartesian and hasattr(data, 'turns_x') and hasattr(data, 'turns_y') and hasattr(data, 'turns_z'):
            all_r = np.zeros(len(data.turns_x))
            all_r[:] = np.nan
            all_phi = np.zeros(len(data.turns_x))
            all_phi[:] = np.nan

            for i, (x, y, z) in enumerate(zip(data.turns_x, data.turns_y, data.turns_z)):
                coord_cylindrical = cartesian_cylindrical(Point3DCart(x=x, y=y, z=z), phi_degrees=True)
                all_r[i] = coord_cylindrical[0]
                all_phi[i] = coord_cylindrical[2]

            data.delete_attr('turns_x')
            data.delete_attr('turns_y')

            data.add_attr('turns_r', all_r)
            data.add_attr('turns_phi', all_phi)
        elif cartesian and ( hasattr(data, 'turns_r') and hasattr(data, 'turns_z') and hasattr(data, 'turns_phi') ):
            coord_cartesian = cylindrical_cartesian(Point3DCyl(r=data.turns_r, phi=data.turns_phi, z=data.turns_z))

            data.delete_attr('turns_r')
            data.delete_attr('turns_phi')

            data.add_attr('turns_x', coord_cartesian[0])
            data.add_attr('turns_y', coord_cartesian[1])
        else:
            for child in data.children:
                self._convert_coords_loop(child, cartesian=cartesian)


    def _walk_tree_plot(self, data, ax_2d, ax_3d, ax_2d_xy_upper, ax_2d_xy_lower, color="green"):
        """
        Walk tree to plot all ELM coils
        :param data: data structure to walk
        :param ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param ax_3d: ax_2d: matplotlib.axes._subplots.Axes3DSubplot for 3D plot
        :param color: colour of loops for plotting
        :return:

        """
        Point3DCart = namedtuple('Point3DCart', ['x', 'y', 'z'])
        Point3DCyl = namedtuple('Point3DCyl', ['r', 'z', 'phi'])

        coords_retrieved = False

        try:
            x_coords = data['geometry'].turns_x
            y_coords = data['geometry'].turns_y
            z_coords = data['geometry'].turns_z

            r_coords = np.zeros(len(x_coords))
            r_coords[:] = np.nan
            phi_coords = np.zeros(len(x_coords))
            phi_coords[:] = np.nan

            for i, (x, y, z) in enumerate(zip(x_coords, y_coords, z_coords)):
                rzphi = cartesian_cylindrical(Point3DCart(x=x, y=y, z=z), phi_degrees=True)
                r_coords[i] = rzphi[0]
                phi_coords[i] = rzphi[2]

            coords_retrieved = True
        except AttributeError:
            r_coords = data['geometry'].turns_r
            phi_coords = data['geometry'].turns_phi
            z_coords = data['geometry'].turns_z

            x_coords = np.zeros(len(r_coords))
            x_coords[:] = np.nan
            y_coords = np.zeros(len(r_coords))
            y_coords[:] = np.nan

            for i, (r, z, phi) in enumerate(zip(r_coords, z_coords, phi_coords)):
                xyz = cylindrical_cartesian(Point3DCyl(r=r, z=z, phi=phi), phi_degrees=True)
                x_coords[i] = xyz[0]
                y_coords[i] = xyz[1]

            coords_retrieved = True
        except KeyError:
            for child in data.children:
                self._walk_tree_plot(child, ax_2d, ax_3d, ax_2d_xy_upper, ax_2d_xy_lower, color=color)

        if coords_retrieved and ax_2d_xy_upper is not None and np.min(z_coords) > 0:
            ax_2d_xy_upper.plot(x_coords, y_coords, color=color)

        if coords_retrieved and ax_2d_xy_lower is not None and np.min(z_coords) < 0:
            ax_2d_xy_lower.plot(x_coords, y_coords, color=color)

        if coords_retrieved and ax_2d is not None:
            ax_2d.plot(r_coords, z_coords, color=color)

        if coords_retrieved and ax_3d is not None:
            ax_3d.plot(x_coords, y_coords, z_coords, color=color)


    def plot(self, ax_2d=None, ax_3d=None, ax_2d_xy_upper=None, ax_2d_xy_lower=None, show=True, color="green"):
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        data = self.data

        # Create axes if necessary
        if ax_2d is None and ax_3d is None and ax_2d_xy_upper is None and ax_2d_xy_lower is None:
            fig = plt.figure()
            if ax_2d_xy_upper is None:
                ax_2d_xy_upper = fig.add_subplot(141)
            if ax_2d_xy_lower is None:
                ax_2d_xy_lower = fig.add_subplot(142)
            if ax_2d is None:
                ax_2d = fig.add_subplot(143)
            if ax_3d is None:
                ax_3d = fig.add_subplot(144, projection='3d')

        self._walk_tree_plot(data, ax_2d, ax_3d, ax_2d_xy_upper, ax_2d_xy_lower, color=color)

        if ax_2d is not None:
            ax_2d.set_xlabel("R [m]")
            ax_2d.set_ylabel("Z [m]")
            ax_2d.set_aspect('equal', 'datalim')
            ax_2d.set_title("All coils R-Z")
        if ax_2d_xy_upper is not None:
            ax_2d_xy_upper.set_xlabel("x [m]")
            ax_2d_xy_upper.set_ylabel("y [m]")
            ax_2d_xy_upper.set_aspect('equal', 'datalim')
            ax_2d_xy_upper.set_title("Upper coils x-y")
        if ax_2d_xy_lower is not None:
            ax_2d_xy_lower.set_xlabel("x [m]")
            ax_2d_xy_lower.set_ylabel("y [m]")
            ax_2d_xy_lower.set_aspect('equal', 'datalim')
            ax_2d_xy_lower.set_title("Lower coils x-y")
        if ax_3d is not None:
            ax_3d.set_xlabel('x [m]')
            ax_3d.set_ylabel('y [m]')
            ax_3d.set_zlabel('z [m]')

        if show:
            plt.tight_layout()
            plt.show()