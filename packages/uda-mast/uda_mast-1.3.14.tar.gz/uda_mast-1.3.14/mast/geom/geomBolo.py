from .geometry import GeometryData
from .geometryUtils import (cartesian_cylindrical, cylindrical_cartesian, find_intersection_rz,
                            find_intersection_xy, calculate_tangency_radius,
                            unit_vector_to_poloidal_angle)
from collections import namedtuple
import numpy as np
from shapely.geometry import LineString, Polygon, Point
from shapely.geometry.polygon import orient


class GeomBolo(GeometryData):
    """
    Sub-class for bolometry system

    Implements:
    - plot: Plot bolometry system in 2D R-Z and x-y. If limiter can be retrieved plots lines of sight.
    - derive_coordinates: Calculate derived LOS coordinates.
    - get_slit_by_id: return the slit object corresponding to the slit_id attribute of a foil
    - _convert_coords_loop: Converts bolometry co-ordinates cartesian <=> cylindrical
    """

    def _get_dependencies(self, limiter_signal='/limiter/efit', limiter_shot=None):
        """
        Retrieve bolo dependencies, needed for calculating lines-of-sight.
        :param limiter_signal: Geometry limiter signal to use
        :param limiter_shot: Shot to retrieve limiter data for
        :return:
        """

        from .geomEfitLimiter import GeomEfitLimiter

        self.limiter = None

        if limiter_shot is None and self.shot is None:
            self._logger.warning("Bolo shot unknown so limiter could not be loaded. Specify limiter shot using limiter_shot keyword")
            return
        elif self.shot is not None:
            limiter_shot = self.shot

        limiter = GeomEfitLimiter(self._uda_client)
        limiter.get(limiter_signal, limiter_shot)

        self.limiter = limiter.data


    def plot(self, ax_2d=None, ax_2d_xy=None, show=True, color="green",
             limiter='/limiter/efit', limiter_shot=None):
        """
        Plot bolometry data
        :param ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param ax_2d_xy: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param show: display plot
        :param color: color for bolometry lines of sight
        :param limiter: signal for limiter. Defaults to /limiter/efit
        :param limiter_shot: Shot for limiter. Defaults to bolometry shot if known.
                             If bolometry data was read directly from file must be specified to plot lines-of-sight
        :return:
        """

        import matplotlib.pyplot as plt

        self._get_dependencies(limiter_signal=limiter, limiter_shot=limiter_shot)

        data = self.data

        # Create axes if necessary
        if ax_2d is None:
            fig = plt.figure()
            if ax_2d is None:
                ax_2d = fig.add_subplot(121)
                ax_2d_xy = fig.add_subplot(122)

        # Plot
        if ax_2d is not None:
            self._walk_tree_plot_2d(data, ax_2d, ax_2d_xy, color=color, limiter=self.limiter)

            ax_2d.set_xlabel('R [m]')
            ax_2d.set_ylabel('Z [m]')

        if ax_2d_xy is not None:
            ax_2d_xy.set_xlabel('x [m]')
            ax_2d_xy.set_ylabel('y [m]')

        if show:
            plt.show()


    def _walk_tree_plot_2d(self, data, ax_2d, ax_2d_xy, color="green", limiter=None):
        """
        Walk bolometry data tree and plot slit and foil locations in R-Z and top-down x-y.
        If limiter data is passed then lines of sight are plotted.
        :param data: bolometry data structure
        :param ax_2d: ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param ax_2d_xy: ax_2d_xy: matplotlib.axes._subplots.AxesSubplot for top down x-y plot
        :param color: color for bolometry
        :param limiter: limiter data structure
        :return:
        """

        import matplotlib.pyplot as plt

        Point3DCart = namedtuple('Point3DCart', ['x', 'y', 'z'])
        Point3DCyl = namedtuple('Point3DCyl', ['r', 'z', 'phi'])
        Point2DCyl = namedtuple('Point2DCyl', ['r', 'z'])

        child_names = [child.name for child in data.children]

        if "foils" in child_names and "slits" in child_names:
            # Loop over foils
            for foil in data["foils/data"]:
                foil_centre = foil["centre_point"]
                slit_centre = data["slits/data"][foil.slit_no]["centre_point"]

                # Get x,y,z and r,phi,z coordinates
                try:
                    foil_xyz = Point3DCart(x=foil_centre.x, y=foil_centre.y, z=foil_centre.z)
                    slit_xyz = Point3DCart(x=slit_centre.x, y=slit_centre.y, z=slit_centre.z)
                    foil_rphiz = cartesian_cylindrical(foil_xyz, phi_degrees=True)
                    slit_rphiz = cartesian_cylindrical(slit_xyz, phi_degrees=True)
                    foil_rphiz = Point3DCyl(r=foil_rphiz[0], phi=foil_rphiz[2], z=foil_rphiz[1])
                    slit_rphiz = Point3DCyl(r=slit_rphiz[0], phi=slit_rphiz[2], z=slit_rphiz[1])
                except AttributeError:
                    foil_rphiz = Point3DCyl(r=foil_centre.r, phi=foil_centre.phi, z=foil_centre.z)
                    slit_rphiz = Point3DCyl(r=slit_centre.r, phi=slit_centre.phi, z=slit_centre.z)
                    foil_xyz = cylindrical_cartesian(foil_rphiz, phi_degrees=True)
                    slit_xyz = cylindrical_cartesian(slit_rphiz, phi_degrees=True)
                    foil_xyz = Point3DCart(x=foil_xyz[0], y=foil_xyz[1], z=foil_xyz[2])
                    slit_xyz = Point3DCart(x=slit_xyz[0], y=slit_xyz[1], z=slit_xyz[2])

                intersect_points_rz = None
                intersect_points_xy = None

                # If the limiting surface has been given we can plot LOS
                if limiter is not None:

                    ##########################################
                    # R-Z intersection with limiting surface
                    ##########################################

                    # Take the end of the line to be really far away so we definitely catch the intersections.
                    # This isn't actually correct for some of the tangential LOS's, which don't intersect the centre column
                    line_end = Point2DCyl(r=foil_rphiz.r + (slit_rphiz.r - foil_rphiz.r) * 100.0,
                                          z=foil_rphiz.z + (slit_rphiz.z - foil_rphiz.z) * 100.0)

                    intersect_points_rz = find_intersection_rz(foil_rphiz, line_end, limiter)


                    ##########################################
                    # x-y intersection with inner & outer limiting surface
                    ##########################################
                    line_end = Point3DCart(x=foil_xyz.x + (slit_xyz.x - foil_xyz.x) * 100.0,
                                           y=foil_xyz.y + (slit_xyz.y - foil_xyz.y) * 100.0,
                                           z=foil_xyz.z + (slit_xyz.z - foil_xyz.z * 100.0))

                    # Work out the boundary to intersect with
                    # We want the outer limiter boundary - inner boundary to give us the 'ring' that excludes the centre column
                    if np.isclose(foil_xyz.z, line_end.z, atol=0.0005):

                        try:
                            coordTuple = list(zip(limiter.R, limiter.Z))
                        except AttributeError:
                            coordTuple = list(zip(limiter.r, limiter.z))
                        polygonBoundary = Polygon(coordTuple)

                        # If the los is in the same plane, we only need to check the boundary at this height
                        # At this z-value find intersect with boundary of horizontal line at z=line_start.z
                        line_z = LineString([(0.0, line_end.z), (100.0, line_end.z)])
                        intersect = polygonBoundary.intersection(line_z)
                        boundR_inner = intersect.coords[0][0]
                        boundR_outer = intersect.coords[1][0]
                    else:
                        # Otherwise, we need to work out where the intersection is in the x-y plane at the appropriate Z-height
                        if intersect_points_rz[0][0] < intersect_points_rz[1][0]:
                            boundR_outer = intersect_points_rz[1][0]
                            boundR_inner = intersect_points_rz[0][0]
                        else:
                            boundR_outer = intersect_points_rz[0][0]
                            boundR_inner = intersect_points_rz[1][0]

                    intersect_points_xy = find_intersection_xy(foil_xyz, line_end, boundR_outer, bound_r_inner=boundR_inner)

                # Plots
                if ax_2d is not None:

                    # R,Z plot
                    ax_2d.plot(foil_rphiz.r, foil_rphiz.z, marker=".", color=color)

                    if intersect_points_rz is not None:
                        if len(intersect_points_rz) == 1:
                            color_plot = "black"
                        else:
                            color_plot = color

                        rcoords = [foil_rphiz.r]
                        [rcoords.append(x[0]) for x in intersect_points_rz]
                        zcoords = [foil_rphiz.z]
                        [zcoords.append(x[1]) for x in intersect_points_rz]

                        ax_2d.plot(rcoords, zcoords, linestyle="-", color=color_plot)

                if ax_2d_xy is not None:
                    # x,y plot
                    ax_2d_xy.plot(foil_xyz.x, foil_xyz.y, marker=".", color=color)

                    if intersect_points_xy is not None:
                        xcoords = [foil_xyz.x]
                        [xcoords.append(x[0]) for x in intersect_points_xy]

                        ycoords = [foil_xyz.y]
                        [ycoords.append(x[1]) for x in intersect_points_xy]

                        ax_2d_xy.plot(xcoords, ycoords, linestyle="-", color=color)

        else:
            # Continue down the tree
            for child in data.children:
                self._walk_tree_plot_2d(child, ax_2d, ax_2d_xy, color=color, limiter=limiter)


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

    def derive_coordinates(self, limiter_signal='/limiter/efit', limiter_shot=None):
        """
        Calculate tangency radius, LOS angle and divertor s coordinate.

        The tangency radius is calculated for tangential channels.

        For poloidal channels, in both the core and divertor, the s
        coordinate of the intersection of the line of sight with the
        limiter is calculated, as is the angle the line of sight vector
        makes with the outward radial unit vector (increasing clockwise).

        This function walks the data tree and calculates the
        values for all foils. New attributes containing the derived
        data are added to each foil, overwriting existing attributes if
        present.

        :param limiter_signal: the name of the signal to use as the limiting surface.
        :param limiter_shot: the shot at which to read the limiter signal.
        """
        self._get_dependencies(limiter_signal, limiter_shot)

        limiter = LineString(zip(self.limiter.R, self.limiter.Z))
        # Ensure limiter is anti-clockwise.
        limiter = orient(Polygon(limiter), sign=1).exterior
        # s is defined to be zero at the inboard midplane.
        midplane = LineString([(0, 0), (10, 0)])
        s0_point = min(midplane.intersection(limiter).geoms, key=midplane.project)
        s0 = limiter.project(s0_point)


        def recursive_derive(data):
            for child in data.children:
                if getattr(child, 'object_type', None) == 'BolometerFoil':
                    foil_centre = child['centre_point']
                    slit = self.get_slit_by_id(child.slit_id)
                    slit_centre = slit['centre_point']
                    if 'tangential' in child.id.lower():
                        # Add tangency radius.
                        try:
                            rtan = calculate_tangency_radius(foil_centre, slit_centre)
                        except AttributeError:  # Data must be in Cartesian coordinates.
                            foil_centre = Point(cylindrical_cartesian(foil_centre))
                            slit_centre = Point(cylindrical_cartesian(slit_centre))
                            rtan = calculate_tangency_radius(foil_centre, slit_centre)
                        child.delete_attr('rtan')
                        child.add_attr('rtan', rtan)
                    else:
                        # Add poloidal angle.
                        try:
                            dr = slit_centre.r - foil_centre.r
                            dz = slit_centre.z - foil_centre.z
                            foil_centre = np.asarray([foil_centre.r, foil_centre.z])
                            sightline_vector = np.asarray([dr, dz])
                        except AttributeError:  # Data must be in cylindical coordinates.
                            foil_centre = np.asarray(cartesian_cylindrical(foil_centre))[:2]
                            slit_centre = np.asarray(cartesian_cylindrical(slit_centre))[:2]
                            sightline_vector = slit_centre - foil_centre
                        unit_vector = sightline_vector / np.linalg.norm(sightline_vector)
                        angle = unit_vector_to_poloidal_angle(*unit_vector, convention='anticlockwise')
                        child.delete_attr('angle')
                        child.add_attr('angle', angle)
                        # Add s coordinate.
                        line_end = foil_centre + 100 * unit_vector
                        # Extend LOS so it's guaranteed to intersect the limiter.
                        long_los = LineString([foil_centre, line_end])
                        intersections = limiter.intersection(long_los)
                        # LOS end is furthest intersection from foil, to account for
                        # entering the limiting surface as well.
                        los_end = max(intersections.geoms, key=long_los.project)
                        srel = limiter.project(los_end)
                        # s increases clockwise and is relative to the midplane.
                        s = s0 - srel
                        child.delete_attr('s')
                        child.add_attr('s', s)
                else:
                    recursive_derive(child)

        recursive_derive(self.data)


    def get_slit_by_id(self, slit_id):
        """
        Return the slit object with id <slit_id>.
        """
        def walk_tree_find_slit(data):
            for child in data.children:
                if getattr(child, 'object_type', None) == 'BolometerSlit':
                    if child.id == slit_id:
                        return child
                ret = walk_tree_find_slit(child)
                if ret is not None:
                    return ret
            return None

        return walk_tree_find_slit(self.data)
