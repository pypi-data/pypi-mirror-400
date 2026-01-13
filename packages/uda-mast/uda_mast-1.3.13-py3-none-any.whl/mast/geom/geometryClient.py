import logging
from .geometryFiles import GeometryFiles
from .geometry import GeometryData
from pyuda import UDAException
import sys

class GeomClient(object):
    def __init__(self, client, debug_level=logging.ERROR):
        self.client = client
        logging.basicConfig(level=debug_level)
        self.logger = logging.getLogger(__name__)

    def geometry_signal_mapping(self, shot=None, geom_group=None, geom_signal=None, uda_signal=None,
                                version_config=None, version_signal_map=None):

        if shot is None:
            self.logger.error("Please set shot")
            return None

        if geom_group is None and geom_signal is None and uda_signal is None:
            print("Please set one of geom_group, geom_signal OR uda_signal\n")
            return None

        command = "GEOM::getGeomUdaSignalMapping(shot={}".format(shot)

        if geom_group is not None:
            command += ", geomgroup={}".format(geom_group)
            if geom_group[-1] != '/':
                command += '/'
        elif geom_signal is not None:
            command += ", geomsignal={}".format(geom_signal)
            if geom_signal[-1] != '/':
                command += '/'
        elif uda_signal is not None:
            command += ", udasignal={}".format(uda_signal)

        if version_config is not None:
            command += ", geom_version={}".format(version_config)

        if version_signal_map is not None:
            command += ", signal_map_version={}".format(version_signal_map)

        command += ')'

        self.logger.debug("Call is: {} for shot {}".format(command, shot))

        return self.client.get(command, shot)


    def geometry(self, signal, source,
                 version_config=None, version_cal=None,
                 no_cal=False, cal_source=None,
                 cartesian_coords=None, cylindrical_coords=None, **kwargs):

        if cartesian_coords and cylindrical_coords:
            self.logger.error("You cannot ask for cartesian and cylindrical coordinates at the same time! Please choose one or the other.")
            return

        if cartesian_coords is None and cylindrical_coords is None:
            cartesian_coords = False
            cylindrical_coords = True
        elif cartesian_coords is None:
            cartesian_coords = False
        elif cylindrical_coords is None:
            cylindrical_coords = False

        # Get rid of trailing slash...
        if signal[-1] == '/':
            signal = signal[:-1]

        source_call = "{}".format(source)
        isfile = source_call.endswith(".nc")

        signal_map = GeometryFiles()

        if not isfile:
            filename = None

            # Because we can retrieve signals using bottom-level variable name only,
            # need to find which group they belong to, to assign the appropriate manipulator
            filenames_call = "GEOM::getConfigFilenames(signal={})".format(signal.lower())

            self.logger.debug("Call to retrieve filenames is {}".format(filenames_call))

            multiple_names = self.client.get(filenames_call, source)

            signal_groups = multiple_names.geomgroups
            signal_groups = list(set(signal_groups))

            if len(signal_groups) > 1:
                self.logger.error("Multiple groups found for this signal: {}".format(signal_groups))
                return

            self.logger.debug("Signal groups: {}".format(signal_groups))

            if len(signal_groups) > 1:
                signal_name = signal_groups[0]
            else:
                signal_name = signal.lower()

            if signal_name is None:
                return

            # Retrieve global attributes from file
            header_info = self.client.get("GEOM::getMetaData(geomgroup={}, /config)".format(signal_groups[0]), source)
            coord_system = header_info.coordinateSystem

            # Mapping from system and class to Class that needs to be used.
            manip = signal_map.get_signals(header_info.system)

            if manip is not None:
                self.logger.debug("Class to be used: {}".format(manip['class']))
            else:
                self.logger.debug("Class was not detected, will use GeometryData class")
        else:
            # Retrieving local file
            signal_name = signal
            source_call = ""
            filename = source
            header_info = self.client.get("GEOM::getMetaData(file={})".format(source), "")
            coord_system = header_info.coordinateSystem

            # Mapping from system and class to Class that needs to be used.
            manip = signal_map.get_signals(header_info.system)

            if manip is not None:
                self.logger.debug("Class to be used: {}".format(manip['class']))
            else:
                self.logger.debug("Class for {} was not detected, will use GeometryData class".format(header_info.system))

        # Get data
        try:
            geomclass = getattr(sys.modules[manip['file']], manip['class'])
            geom_data = geomclass(self.client)
        except TypeError:
            geom_data = GeometryData(self.client)

        geom_data.get(signal_name, source_call, filename=filename,
                      version_config=version_config, version_cal=version_cal, no_cal=no_cal,
                      cal_source=cal_source,
                      coord_system=coord_system,
                      cartesian_coords=cartesian_coords, cylindrical_coords=cylindrical_coords,
                      **kwargs)

        self.logger.debug("Coordinate system is {}".format(coord_system))

        return geom_data


    def listGeomSignals(self, shot=None, group=None, version=None):

        if shot is None:
            shot = ""

        command = "GEOM::listgeomsignals("

        if group is not None:
            if group[-1] != "/":
                group += "/"

            command = command + "geomgroup={}".format(group)

        if version is not None:
            command = command + ", version={}".format(version)

        command = command + ")"

        self.logger.debug("Call is: {} for shot {}".format(command, shot))

        return self.client.get(command, shot)

    def listGeomGroups(self, shot=None):

        if shot is None:
            shot = ""

        command = "GEOM::listgeomgroups()"

        self.logger.debug("Call is: {} for shot {}".format(command, shot))

        return self.client.get(command, shot)

