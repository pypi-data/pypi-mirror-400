
from pyuda._data import Data
from pyuda import UDAException
from .structuredWritable import StructuredWritable

import numpy as np
import inspect
import logging

class GeometryData(Data):

    def __init__(self, uda_client):
        """
        Initialisation
        :param uda_client: instance of UDA client pyuda.Client() for data retrieval
        """
        self._uda_client = uda_client

        self._logger = logging.getLogger(__name__)

        self.signal_name = None
        self.shot = None
        self.data = None

    def get(self, signal_name, source_call, filename=None,
            version_config=None, version_cal=None, no_cal=False,
            cal_source=None, coord_system="",
            cartesian_coords=False, cylindrical_coords=True,
            **kwargs):
        """
        Get data
        :param signal_name: Geometry signal name
        :param source_call: Source to pass to get call
        :param filename: Filename for reading local file. Leave as None for read from data archive.
        :param version_config: Version of configuration data to retrieve
        :param version_cal: Version of calibration data to retrieve
        :param no_cal: Don't apply geometry calibration
        :param cal_source: Specify local file to read calibration data out of.
        :param coord_system: Specify what the co-ordinate system is for the data.
        :param cartesian_coords: Set to True for Cartesian coords where possible
        :param cylindrical_coords: Set to True for Cylindrical coords where possible.
        :param kwargs: Additional keywords
        :return:
        """


        geom_call = "GEOM::get(signal={}".format(signal_name)

        ############################
        # Retrieve config file
        config_call = geom_call

        if version_config is not None:
            config_call += ", version={}".format(version_config)

        if filename is None:
            config_call += ", Config=1)"
        else:
            config_call += ", file={})".format(filename)

        # Retrieve file
        self._logger.info("Call is {} Source is {}\n".format(config_call, source_call))
        try:
            config_data = self._uda_client.get(str(config_call), source_call)
            config_struct = StructuredWritable(config_data._cnode)
        except UDAException as uda_err:
            self._logger.error("ERROR: Could not retrieve geometry data for signal {} and source {}. UDA Error: {}\n".format(signal_name, source_call, uda_err))
            return

        ############################
        # Get calibration data unless asked not to calibrate, or unless we're just reading in a local file
        cal_struct = None

        if not no_cal and (filename is None or cal_source is not None):
            cal_call = geom_call

            if cal_source is None:
                if version_cal is not None:
                    cal_call += ", version_cal={}".format(version_cal)
                cal_call += ", Cal=1)"
            else:
                cal_call += ", file={})".format(cal_source)

            self._logger.debug("Call is {0}\n".format(cal_call))
            try:
                cal_data = self._uda_client.get(str(cal_call), str(source_call))
                cal_struct = StructuredWritable(cal_data._cnode)
                self._logger.debug("Calibration data was found")
            except UDAException:
                cal_struct = None
                self._logger.debug("No calibration data was found")

        signal_type = config_struct.signal_type

        ############################
        # Calibrate geometry data
        if cal_struct is not None:
            self._logger.debug("Applying geometry calibration for signal_name {0}".format(signal_name))
            self._child_loop(cal_struct, config_struct, signal_name, signal_type)

        self._logger.debug("Applying manipulations")

        # Manipulations to return the correct aspect of the data.
        self._do_manip(config_struct, **kwargs)

        # Get rid of some unnecessary levels in the tree
        group_name = signal_name[signal_name.rfind('/')+1:]
        config_struct.change_child_name("data", group_name)

        if signal_type == "group" or signal_type == "array":
            config_struct[group_name].delete_level("data")

        config_struct.delete_level(group_name)

        self._logger.debug("Storing data")

        # Store the data
        self.data = config_struct
        self.signal_name = signal_name
        try:
            self.shot = int(source_call)
        except ValueError:
            pass

        # If requested, convert data to a different co-ordinate system
        if (coord_system.lower() == "cylindrical" and cartesian_coords):
            self._logger.debug("Converting to cartesian coordinates")
            self.convert_coords_cartesian()
        elif (coord_system.lower() == "cartesian" and cylindrical_coords):
            self._logger.debug("Converting to cylindrical coordinates")
            self.convert_coords_cylindrical()


    def _get_all_attr(self, data, exclude=()):
        """
        Get all attributes except those in exclude
        :param data: class
        :param exclude: attributes to be excluded from list
        :return: list of attributes of the class
        """
        attr_data = inspect.getmembers(data, lambda a: not (inspect.isroutine(a)))
        attr_data = [a for a in attr_data
                     if not (a[0].startswith('_') or a[0] in exclude)]

        return attr_data


    def _child_loop(self, cal_data, config_data, signal_name, signal_type):
        """
        Recursively loop over children in the cal tree.
        If an attribute doesn't exist in the Config tree
        it is added.
        If the user has asked for a variable, or an element
        of a variable then this is calibrated and returned,
        if a calibration exists.
        If the user has asked for a group of variables, then
        the children are looped over, looking for variables
        that need to be calibrated.
        The assumption is that a variable containing calibration
        data ends with "_cal".
        :param cal_data: calibration data (instance of StructuredWritable)
        :param config_data: configuration data (instance of StructuredWritable)
        :param signal_name: signal name that was asked for.
        :param signal_type: 'group', 'array' or 'element'.
        :return:
        """

        # Attributes
        attr_cal = self._get_all_attr(cal_data, exclude=('children', 'name'))
        attr_config = self._get_all_attr(config_data, exclude=('children', 'name'))
        attr_names_config = [a[0] for a in attr_config]

        for attr in attr_cal:
            # If there is an attribute in the calibration,
            # but not in the configuration, add it to the configuration.
            if attr[0] not in attr_names_config:
                # Add it in
                config_data.add_attr(attr[0], attr[1])

        if signal_type == "element":
            # We've already retrieved the correct data -> calibrate!
            # NB: Strings coming back wrong here, otherwise we could double-check
            self._calibrate_data(cal_data["data"], config_data["data"])
        else:
            # They've asked for a group of variables:
            # Loop over children and check for data that needs calibrating.
            children_names_config = [child.name for child in config_data.children]

            for child in cal_data.children:
                if (hasattr(child, 'calibration')):
                    if child.calibration == "True" and child.name in children_names_config:
                        # Found data to be calibrated: find matching Config data & calibrate
                        child_ind = children_names_config.index(child.name)

                        if isinstance(child["data"], list):
                            for cal_data, conf_data in zip(child["data"], (config_data.children[child_ind])["data"]):
                                self._calibrate_data(cal_data, conf_data)
                        else:
                            self._calibrate_data(child["data"], (config_data.children[child_ind])["data"])
                    else:
                        # This is a group that is not in the Config file and/or is not calibration data: add it.
                        config_data.add_child(child)
                elif child.name in children_names_config:
                    # Child is in calibration and Config data, continue looping to look
                    # for variable that needs calibrating
                    child_ind = children_names_config.index(child.name)
                    self._child_loop(child, config_data.children[child_ind], signal_name, signal_type)


    def _calibrate_data(self, cal_data, config_data):
        """
        Calibrate configuration data using cal data.
        :param cal_data: calibration data
        :param config_data: configuration data
        :return:
        """

        # Char arrays in NC file are returned as a list of strings
        # Whereas string arrays in NC file are returned as a scalar string
        if isinstance(cal_data.type, list):
            cal_type = cal_data.type[0]
        else:
            cal_type = cal_data.type

        replace_values = (cal_type == "ABSOLUTE")
        self._correct_loop(cal_data, config_data, replace=replace_values)


    def _correct_loop(self, cal_data, config_data, replace=False):
        """
        Recursively loop over all children and attributes.
        If an attribute exists in calibration and configuration
        data then the configuration data is modified using the
        calibration data.
        If an attribute or child doesn't exist in the configuration
        data it is added to the structure.
        :param cal_data: calibration data (instance of StructuredWritable)
        :param config_data: configuration data (instance of StructuredWritable)
        :param replace: True, calibration data replaces configuration data
                        False, calibration data is summed with configuration data.
                        (ie. relative or absolulte calibration)
        :return:
        """
        # Attributes
        attr_cal = self._get_all_attr(cal_data, exclude=('children', 'name', 'type', 'status'))
        attr_config = self._get_all_attr(config_data, exclude=('children', 'name', 'type', 'status'))
        attr_names_config = [a[0] for a in attr_config]

        for attr in attr_cal:

            # If there is an attribute in the calibration,
            # but not in the configuration, add it to the configuration.
            is_numeric = isinstance(attr[1], (int, float))
            if isinstance(attr[1], (np.ndarray, np.generic)):
                is_numeric = np.issubdtype(attr[1].dtype, np.number)

            if attr[0] in attr_names_config and is_numeric:
                # Get Config data
                if replace:
                    self._logger.debug("Old value {} new value {}".format(attr[0], attr[1]))
                    setattr(config_data, attr[0], attr[1])
                else:
                    config = getattr(config_data, attr[0])
                    self._logger.debug("Old value {} new value {}".format(attr[0], config+attr[1]))
                    setattr(config_data, attr[0], config+attr[1])

            elif attr[0] not in attr_names_config:
                config_data.add_attr(attr[0], attr[1])

        # Loop over children and check for matching data in Config.
        children_names_config = [child.name for child in config_data.children]

        for child in cal_data.children:

            if child.name in children_names_config:
                child_ind = children_names_config.index(child.name)
                self._correct_loop(child, config_data.children[child_ind], replace=replace)
            else:
                config_data.add_child(child)


    def _get_dependencies(self):
        """
        Get any dependencies needed for eg. plotting, calculating other geometry related quantities etc.
        :return:
        """
        pass


    def _do_manip(self, data, **kwargs):
        """
        Manipulate data as needed
        :param data:
        :param kwargs:
        :return:
        """
        pass


    def plot(self, show=True, color='blue', **kwargs):
        """
        Plot components in 2D and 3D.
        :param ax_2d: Axis on which to plot location of components in R-Z (2D) plane.
                    If None, then an axis will be created.
        :param ax_3d: Axis on which to plot location of components in x-y-z (3D) plane.
                    If None, then an axis will be created.
        :return:
        """
        raise NotImplementedError("Plot function not implemented")


    def _convert_coords_loop(self, data, cartesian=True):
        """
        Convert co-ordinates from cylindrical to cartesian or vice-versa.
        Recursive function, walks the tree to find attributes that match them being co-ordinates
        ie. x, y, z OR R,Z,phi OR r,z,phi attributes exist.
        :param data: instance of StructuredWritable to traverse
        :param cartesian: if set to True looks for cylindrical co-ordinates to convert. Otherwise looks for cartesian co-oridnates to convert.
        :return:
        """

        raise NotImplementedError("Conversion to other co-ordinate systems is not yet implemented for this group.")


    def convert_coords_cartesian(self):
        """
        Convert (x,y,z) => (R,Z,phi)
        :return:
        """
        self._convert_coords_loop(self.data, cartesian=True)


    def convert_coords_cylindrical(self):
        """
        Convert
        :return: (R,Z,phi) => (x,y,z)
        """
        self._convert_coords_loop(self.data, cartesian=False)

    def widget(self):
        raise NotImplementedError("widget function not implemented for GeometryData objects")
