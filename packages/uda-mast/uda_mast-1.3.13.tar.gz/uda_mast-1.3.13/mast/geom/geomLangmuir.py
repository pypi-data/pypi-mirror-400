import sys

from .geometry import GeometryData
from .geometryUtils import cylindrical_cartesian
from .geometryUtils import cartesian_cylindrical
from .geomTileSurfaceUtils import get_s_coords_tables_mastu, get_nearest_s_coordinates, get_nearest_s_coordinates_mastu


class GeomLangmuir(GeometryData):
    """
    Sub-class for langmuir probes geometry

    Implements:
    - plot:    Plot langmuir probes in 2D R-Z and 3D.
    - convert_r_z_to_s: Calculate s-coordinate for each R,Z LP position
                        and add "s" attribute to coordinate structure in data tree
    - plot_s_coord: Plot R-Z positions with s-coordinate as colorbar
    - _convert_coords_loop: Converts LP co-ordinates cartesian <=> cylindrical
    """


    def __init__(self, uda_client):
        self._limiter = None
        self.r_z_to_s_map = None

        # Default resolution of s-coordinate
        self.ds = 1e-4

        GeometryData.__init__(self, uda_client)


    @property
    def limiter(self):
        return self._limiter


    @limiter.setter
    def limiter(self, new_limiter):
        if not hasattr(new_limiter.data, 'R') or not hasattr(new_limiter.data, 'Z'):
            raise AttributeError("limiter.data must have R and Z attributes")

        self._logger.debug("Calculating s-coordinate mapping table for new limiting surface data.")
        self._calculate_r_z_to_s_map(new_limiter.data.R, new_limiter.data.Z, ds=self.ds)

        self._limiter = new_limiter


    def _get_all_coords(self, data, r_z_coord, x_y_z_coord):
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
        else:
            for child in data.children:
                self._get_all_coords(child, r_z_coord, x_y_z_coord)


    def _get_rz_coords(self, data, r_coord, z_coord, probe_names=None):
        child_names = [child.name for child in data.children]

        if "coordinate" in child_names:
            if probe_names is not None:
                probe_names.append(data.name_)
            try:
                r_coord.append(data["coordinate"].r)
                z_coord.append(data["coordinate"].z)
            except AttributeError:
                rzphi_coords = cartesian_cylindrical(data["coordinate"], phi_degrees=True)
                r_coord.append(rzphi_coords[0])
                z_coord.append(rzphi_coords[1])
        else:
            for child in data.children:
                self._get_rz_coords(child, r_coord, z_coord, probe_names=probe_names)


    def _get_rzs_coords(self, data, r_coord, z_coord, s_coord):
        """
        Retrieve R, Z, s coordinates from data tree
        :param data: LP data tree
        :param r_coord: list to fill with R-coords
        :param z_coord: list to fill with Z-coords
        :param s_coord: list to fill with s-coords
        :return:
        """

        child_names = [child.name for child in data.children]

        if "coordinate" in child_names:
            if not hasattr(data["coordinate"], 's'):
                self.convert_r_z_to_s()

            try:
                r_coord.append(data["coordinate"].r)
                z_coord.append(data["coordinate"].z)
                s_coord.append(data["coordinate"].s)
            except AttributeError:
                rzphi_coords = cartesian_cylindrical(data["coordinate"], phi_degrees=True)
                r_coord.append(rzphi_coords[0])
                z_coord.append(rzphi_coords[1])
                s_coord.append(data["coordinate"].s)
        else:
            for child in data.children:
                self._get_rzs_coords(child, r_coord, z_coord, s_coord)


    def _calculate_r_z_to_s_map(self, limiter_r, limiter_z, ds=1e-4):
        """
        Calculate R-Z to s mapping
        :param limiter_r: limiter R coords
        :param limiter_z: limiter Z coords
        :param ds: resolution for interpolation of the wall coordianate, in metres
        :return:
        """

        self.r_z_to_s_map = get_s_coords_tables_mastu(limiter_r, limiter_z, ds=ds)


    def _get_dependencies(self, limiter_signal='/limiter/efit', limiter_shot=None, limiter_no_cal=False, ds=1e-4):
        """
        Retrieve LP dependencies: limiter is needed for s-coordinate calculation
        :param limiter_signal: geometry signal for limiter
        :param limiter_shot: shot for limiter geometry
        :param limiter_no_cal: if True then use baseline CAD for limiter with no shifts
        :param ds: resolution for interpolation of the wall coordianate, in metres
        :return:
        """

        if limiter_shot is None and self.shot is None:
            self._logger.warning("Langmuir probe shot unknown so limiter could not be loaded. Specify limiter shot using limiter_shot keyword")
            return
        elif self.shot is not None:
            limiter_shot = self.shot

        if self.limiter is not None:
            if self.limiter.shot == limiter_shot and self.limiter.signal_name == limiter_signal:
                self._logger.info("Limiter {} for shot {} already loaded. Will not re-load.".format(limiter_signal, limiter_shot))
                return

        self.ds = ds

        from .geomEfitLimiter import GeomEfitLimiter

        limiter = GeomEfitLimiter(self._uda_client)
        limiter.get(limiter_signal, limiter_shot, no_cal=limiter_no_cal)

        self.limiter = limiter


    def _walk_tree_set_s(self, data, s_coords, probe_names):
        """
        Walk LP tree to set s-coordinate attributes
        :param data: LP data tree
        :param s_coords: s co-ordinates to set
        :param probe_names: probe names corresponding to s_coords
        :return:
        """
        child_names = [child.name for child in data.children]

        if "coordinate" in child_names and data.name_ in probe_names:

            ind_s = probe_names.index(data.name_)

            data['coordinate'].add_attr('s', s_coords[ind_s])
        elif "coordinate" in child_names:
            self._logger.warning("No s-coordinate found for probe {}".format(data.name_))
        else:
            for child in data.children:
                self._walk_tree_set_s(child, s_coords, probe_names)


    def convert_r_z_to_s(self, limiter='/limiter/efit', limiter_shot=None, ds=1e-4, limiter_no_cal=False):
        """
        For all probes in self.data calculate s-coordinate from (R,Z) coordinates.
        s-coordinate is added to the probe structure as coordinate.s

        :param limiter: limiter signal. default /limiter/efit
        :param limiter_shot: limiter shot. defaults to shot number used to get GeomLanguir geometry data.
        :param ds: resolution for interpolation of the wall coordianate, in metres
        :param limiter_no_cal: set to True for limiting surface geometry to reflect baseline CAD with no shifts.
        :return:
        """

        if sys.version_info[0] < 3:
            raise Exception("s-coordinate calculation only implemented in Python 3")

        # Set limiter. This will also trigger re-calculation of R-Z to s mapping
        self._get_dependencies(limiter_signal=limiter, limiter_shot=limiter_shot, limiter_no_cal=limiter_no_cal, ds=ds)

        assert(self.r_z_to_s_map is not None)

        probe_names = []
        r_coord = []
        z_coord = []
        self._get_rz_coords(self.data, r_coord, z_coord, probe_names=probe_names)

        s_coord, _ = get_nearest_s_coordinates_mastu(r_coord, z_coord, self.r_z_to_s_map)

        self._walk_tree_set_s(self.data, s_coord, probe_names)


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


    def plot_s_coord(self, ax_2d=None, show=True,
                     limiter='/limiter/efit', limiter_shot=None, ds=1e-4, limiter_no_cal=False):
        """
        Plot langmuir probe R-Z positions, and s-coordinate as colorbar
        :param ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param show: display plots interactively
        :return:
        """
        import matplotlib.pyplot as plt

        data = self.data

        self.convert_r_z_to_s(limiter=limiter, limiter_shot=limiter_shot, ds=ds, limiter_no_cal=limiter_no_cal)

        r_coords = []
        z_coords = []
        s_coords = []
        self._get_rzs_coords(data, r_coords, z_coords, s_coords)

        if ax_2d is None:
            fig, ax_2d = plt.subplots()

        sc = ax_2d.scatter(r_coords, z_coords, c=s_coords)

        ax_2d.set_xlabel("R [m]")
        ax_2d.set_ylabel("Z [m]")
        ax_2d.set_aspect("equal")

        plt.colorbar(sc)

        if show:
            plt.show()


    def plot(self, ax_2d=None, ax_3d=None, ax_2d_xy=None, show=True, color=None):
        """
        Plot langmuir probe positions in 2D R-Z, 3D and optionally 2D top down x-y
        :param ax_2d: matplotlib.axes._subplots.AxesSubplot for R-Z plot
        :param ax_3d: matplotlib.axes._subplots.Axes3DSubplot for 3D plot
        :param ax_2d_xy: matplotlib.axes._subplots.AxesSubplot for top-down x-y plot
        :param show: display plots interactively
        :param color: color for langmuir probes
        :return:
        """

        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

        data = self.data

        # Get coordinates
        r_z_to_plot = []
        x_y_z_to_plot = []
        self._get_all_coords(data, r_z_to_plot, x_y_z_to_plot)

        if len(r_z_to_plot) == 0 or len(x_y_z_to_plot) == 0:
            return

        # Create axes if necessary
        if ax_2d is None and ax_3d is None:
            fig = plt.figure()
            if ax_2d is None:
                ax_2d = fig.add_subplot(121)
            if ax_3d is None:
                ax_3d = fig.add_subplot(122, projection='3d')

        # 2D R-Z plot
        if ax_2d is not None:
            all_R = r_z_to_plot[::2]
            all_Z = r_z_to_plot[1::2]

            if color is None:
                color = "blue"

            ax_2d.scatter(all_R, all_Z, c=color, marker='o', s=10)
            ax_2d.set_xlabel('R [m]')
            ax_2d.set_ylabel('Z [m]')
            ax_2d.set_aspect('equal', 'datalim')

        # 3D plot
        if ax_3d is not None:
            ax_3d.scatter(x_y_z_to_plot[::3], x_y_z_to_plot[1::3], x_y_z_to_plot[2::3], c=color, marker='o', s=10)
            ax_3d.set_xlabel('x [m]')
            ax_3d.set_ylabel('y [m]')
            ax_3d.set_zlabel('z [m]')

        # 2D x-y plot (from top of tokamak)
        if ax_2d_xy is not None:
            ax_2d_xy.scatter(x_y_z_to_plot[::3], x_y_z_to_plot[1::3], c=color, marker='o', s=10)

        if show:
            plt.show()


