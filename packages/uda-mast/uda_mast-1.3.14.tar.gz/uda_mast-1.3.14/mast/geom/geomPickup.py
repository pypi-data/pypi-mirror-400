import math
import numpy as np

from .geometryUtils import length_poloidal_projection
from .geometryUtils import vector_to_bR_bZ_bPhi
from .geometryUtils import unit_vector_to_poloidal_angle
from .geometryUtils import cylindrical_cartesian
from .geometryUtils import cartesian_cylindrical
from .geometry import GeometryData


class GeomPickup(GeometryData):
    """
    Manipulation class for pickup coils.

    Manipulation:
    The do_manip method will take the pickup coil StructuredData
    object and look for geometry and orientation information.

    It will then:
    - Project the length onto the poloidal plane
    - Calculate the angle of the coils in the poloidal plane
    - Calculate the fraction in which the coils measure in the R, Z & Phi directions

    Plotting:
    The plot method will plot the pickup coil locations (in the R-Z plane and in (x,y,z)).
    Pickup coils that measure only toroidally are coloured red.
    """

    def _pickup_poloidal(self, geometry, orientation, pol_type="anticlockwise"):
        """
        Calculate poloidal projections.
        Adds length_poloidal to geometry node.
        Adds poloidal_angle, bRFraction, bZFraction, bPhiFraction to orientation node.
        Deletes unit_vector node from orientation node.
        :param geometry: geometry node
        :param orientation: orientation node
        :return:
        """
        # Length projected to poloidal plane
        length_poloidal = length_poloidal_projection(geometry.length, orientation)
        geometry.add_attr("length_poloidal", length_poloidal)

        # Angle in poloidal plane
        poloidal_angle = unit_vector_to_poloidal_angle(orientation["unit_vector"].r, orientation["unit_vector"].z, convention=pol_type)
        orientation.add_attr("poloidal_angle", poloidal_angle)
        orientation.add_attr("poloidal_convention", pol_type)

        # Fraction measured in bR, bZ and bPhi directions
        bRFraction, bZFraction, bPhiFraction = vector_to_bR_bZ_bPhi(orientation)

        orientation.add_attr("bRFraction", bRFraction)
        orientation.add_attr("bZFraction", bZFraction)
        orientation.add_attr("bPhiFraction", bPhiFraction)

        orientation.delete_child(child_name="unit_vector")


    def _pickup_loop(self, data, pol_type="anticlockwise"):
        """
        Recursively loops over tree nodes, looking for
        level where there is geometry and orientation information,
        where the poloidal projections can be applied
        :param data: data tree (instance of StructuredWritable, with pickup coil tree structure)
        :return:
        """
        child_names = [child.name for child in data.children]

        if "orientation" in child_names and "geometry" in child_names:
            # Poloidal projection
            self._pickup_poloidal(data["geometry"], data["orientation"], pol_type=pol_type)
        else:
            for child in data.children:
                self._pickup_loop(child, pol_type=pol_type)


    def _do_manip(self, data, **kwargs):
        """
        Apply manipulations to data.
        :param data: data tree (instance of StructuredWritable, with pickup coil tree structure)
        :param kwargs: If poloidal keyword is set, then maniuplation is done, otherwise nothing is done.
        :return:
        """
        # Otherwise, perform manipulations
        calc_poloidal = False
        if "poloidal" in kwargs.keys():
            calc_poloidal = kwargs["poloidal"]
            self.pol_type = kwargs["poloidal"].lower()

        if not calc_poloidal:
            return
        
        if self.pol_type != "clockwise" and self.pol_type != "anticlockwise":
            self.pol_type = ""
            return

        # loop over nodes and find pickup coil node to manipulate
        self._pickup_loop(data, pol_type=self.pol_type)


    def _convert_coords_loop(self, data, cartesian=True):
        """
        Convert co-ordinates from cylindrical to cartesian or vice-versa.
        Recursive function, walks the tree to find attributes that match them being co-ordinates
        ie. x, y, z OR R,Z,phi OR r,z,phi attributes exist.
        :param data: instance of StructuredWritable to traverse
        :param cartesian: if set to True looks for cylindrical co-ordinates to convert. Otherwise looks for cartesian co-oridnates to convert.
        :return:
        """

        if not cartesian and hasattr(data, 'x') and hasattr(data, 'y') and hasattr(data, 'z'):
            coord_cylindrical = cartesian_cylindrical(data, phi_degrees=True)

            data.delete_attr('x')
            data.delete_attr('y')
            data.delete_attr('z')

            data.add_attr('r', coord_cylindrical[0])
            data.add_attr('z', coord_cylindrical[1])
            data.add_attr('phi', coord_cylindrical[2])
        elif cartesian and ( (hasattr(data, 'R') and hasattr(data, 'Z') and hasattr(data, 'phi'))
                          or (hasattr(data, 'r') and hasattr(data, 'z') and hasattr(data, 'phi')) ):
            coord_cartesian = cylindrical_cartesian(data)

            data.delete_attr('R')
            data.delete_attr('r')
            data.delete_attr('Z')
            data.delete_attr('z')
            data.delete_attr('phi')

            data.add_attr('x', coord_cartesian[0])
            data.add_attr('y', coord_cartesian[1])
            data.add_attr('z', coord_cartesian[2])
        else:
            for child in data.children:
                self._convert_coords_loop(child, cartesian=cartesian)


    def plot(self, ax_2d=None, ax_3d=None, ax_2d_xy=None, show=True, color=None):
        """
        Plot the pickup coils.
        :param data: data tree (instance of StructuredWritable, with pickup coil tree structure)
        :param ax_2d: Axis on which to plot location of pickup coils in R-Z (2D) plane.
                      If None, then an axis will be created.
        :param ax_3d: Axis on which to plot location of pickup coils in x-y-z (3D) plane.
                      If None, then an axis will be created.
        :return:
        """
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        data = self.data

        # Get coordinates
        r_z_to_plot = []
        x_y_z_to_plot = []
        unit_r = []
        unit_z = []
        colours = []
        markers = []
        self._get_all_coords(data, r_z_to_plot, x_y_z_to_plot, unit_r, unit_z, colours, markers)

        if color is not None:
            colours = [color]*len(colours)

        if len(r_z_to_plot) == 0 or len(x_y_z_to_plot) == 0:
            return

        # Create axes if necessary
        if ax_2d is None and ax_3d is None:
            fig = plt.figure()
            if ax_2d is None:
                ax_2d = fig.add_subplot(121)
            if ax_3d is None:
                ax_3d = fig.add_subplot(122, projection='3d')

        # Plot
        if ax_2d is not None:
            all_R = r_z_to_plot[::2]
            all_Z = r_z_to_plot[1::2]

            marker_size = np.zeros(len(colours)) + 20

            markers_unique = set(markers)

            for marker in markers_unique:
                r_here = [all_R[i] for i in range(len(all_R)) if markers[i] == marker]
                z_here = [all_Z[i] for i in range(len(all_Z)) if markers[i] == marker]
                c_here = [colours[i] for i in range(len(colours)) if markers[i] == marker]
                s_here = [marker_size[i] for i in range(len(marker_size)) if markers[i] == marker]

                ax_2d.scatter(r_here, z_here, c=c_here, marker=marker, s=s_here, edgecolors='face')

            ax_2d.set_xlabel('R [m]')
            ax_2d.set_ylabel('Z [m]')
            ax_2d.set_aspect('equal', 'datalim')

            if len(unit_r) == len(r_z_to_plot[::2]):
                for ur, uz, r, z in zip(unit_r, unit_z, r_z_to_plot[::2], r_z_to_plot[1::2]):
                    if abs(ur) > 1e-6 or abs(uz) > 1e-6:
                        ax_2d.arrow(r, z, ur*0.05, uz*0.05, fc="k", ec="k", head_width=0.01, head_length=0.01)

        if ax_2d_xy is not None:
            ax_2d_xy.scatter(x_y_z_to_plot[::3], x_y_z_to_plot[1::3], c=colours)

        if ax_3d is not None:
            ax_3d.scatter(x_y_z_to_plot[::3], x_y_z_to_plot[1::3], x_y_z_to_plot[2::3], c=colours)
            ax_3d.set_xlabel('x [m]')
            ax_3d.set_ylabel('y [m]')
            ax_3d.set_zlabel('z [m]')

        if show:
            plt.show()


    def _get_all_coords(self, data, r_z_coord, x_y_z_coord, unit_r, unit_z, colours, markers):
        """
        Recursively loop over tree, and retrieve pickup coil co-ordinates.
        :param data: data tree (instance of StructuredWritable, with pickup coil tree structure)
        :param r_z_coord: R,Z coordinates will be appended to this list
        :param x_y_z_coord: x,y,z coordinates will be appended to this list
        :param colours: colours will be appended to this list. Red if the pickup coil measures
                        toroidally, blue if it measures poloidally
        :return:
        """
        child_names = [child.name for child in data.children]

        if "coordinate" in child_names:

            try:
                r_z_coord.append(data["coordinate"].r)
                r_z_coord.append(data["coordinate"].z)
                x_y_z_coord.extend(cylindrical_cartesian(data["coordinate"]))
            except AttributeError:
                x_y_z_coord.extend([data["coordinate"].x, data["coordinate"].y, data["coordinate"].z])
                rzphi_coords = cartesian_cylindrical(data["coordinate"], phi_degrees=True)
                r_z_coord.append(rzphi_coords[0])
                r_z_coord.append(rzphi_coords[1])

            direction = data["orientation"].measurement_direction.replace(" ", "")

            if direction == "TOROIDAL":
                colours.append("red")
            elif direction == "POLOIDAL":
                colours.append("blue")
            elif direction == "PARALLEL":
                colours.append("green")
            else:
                colours.append("magenta")

            length = data["geometry"].length
        
            # These shouldn't really be hard-coded
            if np.isclose(length, 0.021, rtol=0.0, atol=0.0009):
                markers.append("o")
            elif np.isclose(length, 0.026, rtol=0.0, atol=0.0009):
                markers.append("v")
            elif np.isclose(length, 0.002, rtol=0.0, atol=0.0009):
                markers.append("s")
            else:
                markers.append("x")

            child_names_orientation = [child.name for child in data["orientation"].children]

            try:
                pol_angle = data["orientation"].poloidal_angle

                if data["orientation"].poloidal_convention == "clockwise":
                    pol_angle = 360 - pol_angle

                direction = data["orientation"].measurement_direction
                if ("POLOIDAL" in direction
                    or "NORMAL" in direction 
                    or "PARALLEL" in direction):
                    unit_r = unit_r.append(math.cos(math.pi * pol_angle / 180.0))
                    unit_z = unit_z.append(math.sin(math.pi * pol_angle / 180.0))
                else:
                    unit_r = unit_r.append(0.0)
                    unit_z = unit_z.append(0.0)
            except AttributeError:
                if "unit_vector" in child_names_orientation:

                    try:
                        unit_r = unit_r.append(data["orientation/unit_vector"].r)
                        unit_z = unit_z.append(data["orientation/unit_vector"].z)
                    except AttributeError:
                        rzphi_coords = cartesian_cylindrical(data["orientation/unit_vector"])
                        unit_r = rzphi_coords[0]
                        unit_z = rzphi_coords[1]
        else:
            for child in data.children:
                self._get_all_coords(child, r_z_coord, x_y_z_coord, unit_r, unit_z, colours, markers)

