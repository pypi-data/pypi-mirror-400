from __future__ import (division, print_function, absolute_import)

import numpy as np
from collections import namedtuple
import logging
try:
    from enum import Enum
except ImportError:
    Enum = object

from pyuda import cpyuda, StructuredData, Video
import os
import warnings


# class ImageDecodeWarning(UserWarning):
#     def __init__(self, message):
#         super().__init__(ImageDecodeWarning, message)


class ListType(Enum):
    SIGNALS = 1
    SOURCES = 2
    SHOTS = 3


def _quote(arg):
    if isinstance(arg, list):
        arg = ';'.join(str(i) for i in arg)
    try:
        float(arg)
        return arg
    except ValueError:
        if arg.startswith('"') and arg.endswith('"'):
            return "'" + arg[1:-1] + "'"
        elif arg.startswith("'") and arg.endswith("'"):
            return arg
        else:
            return "'" + arg + "'"


class MastClient(object):

    server_tmp_dir = "/tmp/putdata"

    def __init__(self, client, debug_level=logging.ERROR):
        self.client = client
        logging.basicConfig(level=debug_level)
        self.logger = logging.getLogger(__name__)
        self.put_file_id = None

        # To allow easy switching of name of meta plugin
        try:
            self.meta_plugin = os.environ["UDA_META_PLUGINNAME"]
        except KeyError:
            raise RuntimeError('Environment variable "UDA_META_PLUGINNAME" not set. This information is required to query MAST metadata.')
            # self.meta_plugin = 'meta'

        try:
            self.metanew_plugin = os.environ["UDA_METANEW_PLUGINNAME"]
        except KeyError:
            raise RuntimeError('Environment variable "UDA_METANEW_PLUGINNAME" not set. This information is required to query MASTU metadata.')
            # self.metanew_plugin = 'metanew'

        # Map file_id => paths to file on client and server
        self.put_original_path = {}
        self.put_server_path = {}

    # @staticmethod
    # def decode_frames(video, n_threads):
    #     if video.codex == 'none':  # No codec used, we just need to reshape from 1D to 2D.
    #         frames = [np.reshape(frame.bytes, (video.width, video.height), order='F').T
    #                   for frame in video.frames]
    #     else:
    #         import cv2
    #         if n_threads is None:
    #             frames = list(cv2.imdecode(frame.bytes, cv2.IMREAD_UNCHANGED) for frame in video.frames)
    #         else:
    #             from concurrent.futures import ThreadPoolExecutor
    #             with ThreadPoolExecutor(max_workers=n_threads) as ex:
    #                 frames = list(ex.map(lambda frame: cv2.imdecode(frame.bytes, cv2.IMREAD_UNCHANGED),
    #                                      video.frames))
    #     return frames

    def get_images(self, signal, source,
                   first_frame=None, last_frame=None, stride=None, frame_number=None, header_only=False,
                   rcc_calib_path=None):
        """
        Get image data.

        Arguments:
            :param signal: The image signal name
            :param source: The MAST source name
            :param first_frame: The number of the first frame to retrieve or `None` for the first frame
            :param last_frame: The number of the last frame to retrieve or `None` for the last frame
            :param stride: The stride to use to step between the frame, or `None` for a stride of 1
            :param frame_number: The index of a single frame to fetch
            :param header_only: Flag to specify to only retrieve the image header data
            :param rcc_calib_path: Path of the RCC calibrated image data to fetch if shot < 0, `None` to use default path
            :return: A pyuda Image object
        """

        if signal != 'rcc':
            try:
                comm = "NEWIPX::read(shot={:d}, ipxtag={}".format(int(source), signal)
            except ValueError:
                comm = "NEWIPX::read(filename={}".format(source)
        else:
            try:
                shot = int(source)

                comm = "RCC::read(shot={:d}".format(shot)

                if shot < 0 and rcc_calib_path is None:
                    comm += ", /zShot"
                elif shot < 0:
                    comm += ", path={}".format(rcc_calib_path)
            except ValueError:
                comm = "RCC::read(file={})".format(source)

        if first_frame is not None:
            comm += ", first={}".format(first_frame)
        if last_frame is not None:
            comm += ", last={}".format(last_frame)
        if frame_number is not None:
            comm += ", frame={}".format(frame_number)
        if stride is not None:
            comm += ", stride={}".format(stride)
        if header_only:
            comm += ", /header_only"

        # comm += ', /no_decode)'
        comm += ')'

        result = cpyuda.get_data(comm, "")
        if result.error_code() != 0:
            if result.error_message():
                raise cpyuda.ServerException(result.error_message().decode())
            else:
                raise cpyuda.ServerException("Unknown server error")

        if result.is_tree():
            tree = result.tree()
            if tree.data()['type'] == 'VIDEO':
                return Video(StructuredData(tree))
            else:
                raise cpyuda.ServerException("Images reader did not return Video structure")
        else:
            raise cpyuda.ServerException("Images reader did not return Video structure")

        # video = Video(StructuredData(tree))
        # decodable_data = signal != 'rcc' and video.frames is not None and len(video.frames) > 0
        # if not server_decode and decodable_data:
        #     if hasattr(video.frames[0], "bytes"):
        #         decoded = MastClient.decode_frames(video, decode_threads)
        #         for frame, decoded_image in zip(video.frames, decoded):
        #             if len(decoded_image.shape) != 2:
        #                 raise cpyuda.UDAException("Only greyscale images currently supported")
        #             frame.k = decoded_image
        #     else:
        #         warnings.warn("Warning: The pyuda client cannot decode this image data as specified by the \
        #                 server_decode flag. This is because the image data received is not encoded. \
        #                 This could be caused by an old IPX server-plugin version which does not support \
        #                 compressed image transfers. \nYou can disable this warning using:\n\n \
        #                 warnings.simplefilter('ignore', mast.mast_client.ImageDecodeWarning)""",
        #                       ImageDecodeWarning)
        # return video

    def _construct_named_tuple_list(self, data):
        names = list(el for el in data._imported_attrs if el not in ("count",))
        ListData = namedtuple("ListData", names)

        vals = []
        for i in range(data.count):
            row = {}
            for name in names:
                try:
                    row[name] = getattr(data, name)[i]
                except (TypeError, IndexError):
                    row[name] = getattr(data, name)
            vals.append(ListData(**row))
        return vals

    def list(self, list_type, shot=None, alias=None, signal_type=None, signal_search=None, description_search=None, pass_number=None, machine='mastu'):
        """
        Query the server for available data.

        :param list_type: the type of data to list, must be one of pyuda.ListType
        :param shot: the shot number, or None to return for all shots
        :param alias: the device alias, or None to return for all devices
        :param signal_type: the signal types {A|R|M|I}, or None to return for all types
        :param signal_search: string to filter on signal names. Use % as wildcard.
        :param description_search: string to filter on signal descriptions. Use % as wildcard.
        :return: A list of namedtuples containing the query data
        """
        if list_type == ListType.SIGNALS:
            list_arg = ""
        elif list_type == ListType.SOURCES:
            list_arg = "/listSources"
        else:
            raise ValueError("unknown list_type: " + str(list_type))

        args = ""
        if shot is not None:
            args += "shot=%s, " % str(shot)
        if alias is not None:
            args += "alias=%s, " % alias
        if signal_type is not None:
            if signal_type not in ("A", "R", "M", "I"):
                raise ValueError("unknown signal_type " + signal_type)
            args += "type=%s, " % signal_type
        if signal_search is not None:
            args += "signal_match=%s, " % signal_search
        if description_search is not None:
            args += "description=%s, " % description_search
        if pass_number is not None:
            args += "pass=%s, " % pass_number
        if machine is not None and shot is None:
            args += "machine=%s, " % machine

        args += list_arg

        command = "%s::list(context=data, cast=column, %s)" %(self.meta_plugin, args)

        self.logger.debug(command)

        result = cpyuda.get_data(command, "")
        if not result.is_tree():
            raise RuntimeError("UDA list data failed")

        tree = result.tree()
        data = StructuredData(tree.children()[0])
        # names = list(el for el in data._imported_attrs if el not in ("count",))
        # ListData = namedtuple("ListData", names)

        # vals = []
        # for i in range(data.count):
        #     row = {}
        #     for name in names:
        #         try:
        #             row[name] = getattr(data, name)[i]
        #         except (TypeError, IndexError):
        #             row[name] = getattr(data, name)
        #     vals.append(ListData(**row))
        # return vals
        return self._construct_named_tuple_list(data)

    def list_signals(self, **kwargs):
        """
        List available signals.

        See Client.list for arguments.
        :return: A list of namedtuples returned signals
        """
        return self.list(ListType.SIGNALS, **kwargs)

    def list_sources(self, **kwargs):
        """
        List available sources/aliases/tags.

        See Client.list for arguments.
        :return: A list of namedtuples returned sources
        """
        return self.list(ListType.SOURCES, **kwargs)

    def list_shots(self, source=None, alias=None,
                   machine="mastu",
                   signal=None, signal_search=None, signal_type=None,
                   shot_start=None, shot_end=None, 
                   time_start=None, time_end=None, datetime_start=None, datetime_end=None,
                   get_first=False, get_last=False):
        """
        List shots where a given source file exists
        """

        if machine != 'mastu' or (shot_start is not None and shot_start < 40000):
            raise NotImplementedError("list_shots only implemented for mastu")

        args = ""

        if source is not None or alias is not None:
            if source is not None:
                args += "source=%s, " % source
            else:
                args += "source=%s, " % alias

        if signal is not None:
            args += "signal=%s, " % signal
        if signal_search is not None:
            args += "signal_match=%s, " % signal_search
        if signal_type is not None:
            args += "type=%s, " % signal_type
        if shot_start is not None:
            args += "shot_start=%s, " % str(shot_start)
        if shot_end is not None:
            args += "shot_end=%s, " % str(shot_end)
        if time_start is not None:
            args += "time_start=%s, " % time_start
        if time_end is not None:
            args += "time_end=%s, " % time_end
        if datetime_start is not None:
            args += "datetime_start=%s, " % datetime_start
        if datetime_end is not None:
            args += "datetime_end=%s, " % datetime_end
        if get_first:
            args += "/first, "
        if get_last:
            args += "/last, "

        command = "mastu_db::listshots(machine=%s, %s)" % (machine, args)

        self.logger.debug(command)

        result = cpyuda.get_data(command, "")
        if not result.is_tree():
            raise RuntimeError("UDA list data failed")

        tree = result.tree()
        data = StructuredData(tree.children()[0])
        # names = list(el for el in data._imported_attrs if el not in ("count",))
        # ListData = namedtuple("ListShotData", names)

        # vals = []
        # for i in range(data.count):
        #     row = {}
        #     for name in names:
        #         try:
        #             row[name] = getattr(data, name)[i]
        #         except (TypeError, IndexError):
        #             row[name] = getattr(data, name)
        #     vals.append(ListData(**row))

        # return vals
        return self._construct_named_tuple_list(data)

    def list_archive_files(self, path):
        """
        List files in the data archive directory specified by path.

        :param path: Directory to list. Use $MAST_DATA, $MAST_ZSHOT, $MAST_IMAGES etc. rather than the full path.
        :return: array of file names
        """

        result = cpyuda.get_data("%s::listfilesources(path=%s, /exclude_hidden)" % (self.metanew_plugin, path), "")
        if not result.is_tree():
            raise RuntimeError("Could not list files in %s" % path)

        tree = result.tree()
        data = StructuredData(tree.children()[0])

        return data.file_name

    def list_archive_file_info(self, path):
        """
        List files in the data archive directory specified by path, along with some metadata such as the timestamp and file size.

        :param path: Directory to list. Use $MAST_DATA, $MAST_ZSHOT, $MAST_IMAGES etc. rather than the full path.
        :return: array of file names
        """

        result = cpyuda.get_data("%s::list_file_info(path=%s, machine=mastu)" % (self.metanew_plugin, path), "")
        if not result.is_tree():
            raise RuntimeError("Could not list files in %s" % path)

        tree = result.tree()
        data = StructuredData(tree.children()[0])

        FileInfo = namedtuple('FileInfo', 'alias, filename, size, datetime, path_status')
        files = [FileInfo(name[0:3], name, size, dt, status) for (name, size, dt, status) in
                 zip(data.file_name, data.file_size, data.datetime, data.status)]
        return sorted(files, key=lambda x: x.datetime)

    def list_archive_directories(self, path):
        """
        List directories in the data archive specified by path.

        :param path: Directory to list. Use $MAST_DATA, $MAST_ZSHOT, $MAST_IMAGES etc. rather than the full path.
        :return: array of directory names
        """

        result = cpyuda.get_data("%s::listdirectories(path=%s, /exclude_hidden)" % (self.metanew_plugin, path), "")
        if not result.is_tree():
            raise RuntimeError("Could not list directories in %s" % path)

        tree = result.tree()
        data = StructuredData(tree.children()[0])

        return data.dir_name

    def list_file_signals(self, path):
        """
        List signals in a file directly. These can be used for files such as those in $MAST_ZSHOT that may not have
        been ingested into the UDA database.

        :param path: Path to file to list. Use $MAST_DATA, $MAST_ZSHOT, $MAST_IMAGES etc. rather than the expanded path.
        :return: array of signal names
        """

        result = cpyuda.get_data("%s::listfilesignals(dataSource=%s)" % (self.metanew_plugin, path), "")
        if not result.is_tree():
            raise RuntimeError("Could not list signals in %s" % path)

        tree = result.tree()
        data = StructuredData(tree.children()[0])

        return data.signal_name

    def latest_source_pass_in_range(self, source_alias, shot_start=None, shot_end=None, datetime_start=None, datetime_end=None):
        """
        Retrieve latest pass numbers for a specific source file.
        :param source: Source alias (eg. amc)
        :param shot_start: Start shot
        :param shot_end: End shot
        :param datetime_start: Start datetime : string with datetime format of '%Y-%m-%d %H:%M:%S'
        :param datetime_end: End datetime : string with datetime format of '%Y-%m-%d %H:%M:%S'
        :return: Structured object containing shot number, pass number, shot date time
        """

        args = ""

        if shot_start is not None:
            args += ",shot_start=%s " % str(shot_start)
        if shot_end is not None:
            args += ",shot_end=%s " % str(shot_end)
        if datetime_start is not None:
            args += ",datetime_start=%s " % str(datetime_start)
        if datetime_end is not None:
            args += ",datetime_end=%s " % str(datetime_end)

        result = cpyuda.get_data("%s::lastpassshotrange(source=%s %s)" %(self.metanew_plugin, source_alias, args), "")

        if not result.is_tree():
            raise RuntimeError("Could retrieve pass numbers for source and range requested")

        tree = result.tree()
        data = StructuredData(tree.children()[0])

        return data

    def latest_source_pass(self, source_alias, shot):
        """
        Retrieve latest pass number for a specific source file and shot number
        :param source_alias: Source alias (eg. AMC)
        :return: int latest pass number
        """
        result = cpyuda.get_data("%s::get(context=data,shot=%s,source=%s,/lastpass)" %
                                 (self.meta_plugin, str(shot), source_alias), "")

        if not result.is_tree():
            raise RuntimeError("Could retrieve pass number for source and shot requested")

        tree = result.tree()
        data = StructuredData(tree.children()[0])

        return data.lastpass

    def latest_shot(self, machine='mastu'):
        """
        Retrieve latest shot number available via UDA
        :return:
        """
        result = cpyuda.get_data("{}::get(context=data, /lastshot, machine={})".format(self.meta_plugin, machine), "")
        if not result.is_tree():
            raise RuntimeError("Could not retrieve latest shot number")

        tree = result.tree()
        data = StructuredData(tree.children()[0])

        return data.lastshot

    def get_shot_date_time(self, shot):

        result = cpyuda.get_data("{}::get(context=data,shot={},/shotdatetime)".format(self.meta_plugin, shot), "")

        if not result.is_tree():
            raise RuntimeError("Could not retrieve shot date and time for {}".format(shot))

        tree = result.tree()
        data = StructuredData(tree.children()[0])

        return (data.date, data.time)

    def put(self, *args, **kwargs):

        if 'detete' in kwargs:
            print('Sorry, not delete function is available at the moment')
            return

        if 'step_id' not in kwargs:
            print('Please specify the step_id, e.g. "dimension"')
            return

        step_id = kwargs['step_id']
        if kwargs.get('create', False): step_id = 'create'
        if kwargs.get('close', False): step_id = 'close'
        if kwargs.get('update', False): step_id = 'update'

        step = step_id.strip().lower()

        step_id_options = ('create', 'close', 'update', 'device', 'dimension', 'coordinate', 'variable', 'attribute')

        if step not in step_id_options:
            print('step_id must be open of: ' + ', '.join(step_id_options))
            return

        if step == 'create' or step == 'update':
            func = 'open'
        else:
            func = step

        comm = 'PUTDATA::%s(' % func

        data_to_put = None
        directory = None

        if step == 'create' or step == 'update':
            if len(args) < 1 or not isinstance(args[0], str):
                print('Please provide a filename as the first argument')
                return

            if 'directory' in kwargs:
                directory = os.path.abspath(kwargs['directory'])

                server_directory = self.server_tmp_dir + directory
                comm += 'directory=%s, ' % server_directory
                put_filename = args[0]
            else:
                put_filename = self.server_tmp_dir + os.path.abspath(args[0])

            comm += 'filename=%s' % put_filename

            if step == 'update':
                if directory is not None:
                    file_path = directory + '/' + args[0]
                else:
                    file_path = os.path.abspath(args[0])

                try:
                    data_to_put = np.array(bytearray(open(file_path, "rb+").read()), dtype=np.int8)
                except FileNotFoundError:
                    print("File not found {} so can not be opened for update. For new files use step_id=create.".format(file_path))
                    return
        else:
            if 'file_id' in kwargs:
                comm += 'fileid=%s' % str(kwargs['file_id']).strip()
            elif self.put_file_id is not None:
                comm += 'fileid=%d' % self.put_file_id
            else:
                print('No file_id was given, and no file id is stored. Please open the file (either with step_id=create or step_id=update)')
                return

        if step == 'coordinate':
            starts      = kwargs['starts'] if 'starts' in kwargs else None
            increments  = kwargs['increments'] if 'increments' in kwargs else None
            counts      = kwargs['counts'] if 'counts' in kwargs else None

            if len(args) == 1:
                data_to_put = args[0]

            # TODO: could do a bunch more validation of these starts, increments & counts to make sure they are valid.

            if starts is not None:
                if not isinstance(starts, list):
                    starts = [starts]
                comm += ', starts=%s' % ';'.join(str(i) for i in starts)
            if increments is not None:
                if not isinstance(increments, list):
                    increments = [increments]
                comm += ', increments=%s' % ';'.join(str(i) for i in increments)
            if counts is not None:
                if not isinstance(counts, list):
                    counts = [counts]
                comm += ', counts=%s' % ';'.join(str(i) for i in counts)
        elif step == 'variable' or step == 'attribute':
            data_to_put = args[0]

            if isinstance(data_to_put, (list, tuple)):
                data_to_put = np.array(data_to_put)

            if step == 'variable':
                if 'dimensions' not in kwargs:
                    print('dimensions must be defined for variable step.')
                    return

                if isinstance(kwargs['dimensions'], list):
                    reversed_dim = kwargs['dimensions']
                else:
                    reversed_dim = kwargs['dimensions'].split(',')

                # For variables, putdata only supports writing strings as arrays of strings at the moment
                # in which case an additional dimension also needs to be defined for the string lengths
                if isinstance(data_to_put, str):
                    data_to_put = np.array([data_to_put])

                if isinstance(data_to_put, np.ndarray):
                    if (data_to_put.dtype.kind == 'U' or data_to_put.dtype.kind == 'S'):
                        reversed_dim += ['strdim_%s' % kwargs['name']]

                kwargs['dimensions'] = ';'.join(reversed_dim)

        if step == 'device':
            if len(args) < 1 or not isinstance(args[0], str) and 'device' not in kwargs:
                print('No device name was given. Please supply the device name as the first argument.')
                return

            kwargs['device'] = kwargs.get('device', args[0]).strip()

        if step == 'dimension':
            if len(args) < 1 or not isinstance(args[0], int) and 'length' not in kwargs and 'unlimited' not in kwargs:
                print('No dimension length was given and the unlimited flag was not set. Assuming the dimension is unlimited')
                kwargs['unlimited'] = True

            length = None

            if len(args) == 1 and isinstance(args[0], int) and 'length' not in kwargs:
                length = args[0]
            elif 'length' in kwargs:
                length = kwargs['length']

            if length is not None:
                comm += ', length=%d' % length

        exp_number = None

        if 'pulse' in kwargs:
            exp_number = kwargs['pulse']
        elif 'shot' in kwargs:
            exp_number = kwargs['shot']

        if exp_number is not None:
            comm += ', shot=%d' % exp_number


        if 'group' in kwargs:
            if kwargs['group'][0] == '/': kwargs['group'] = kwargs['group'][1:]

        parameters = (
            'channels',
            'channel',
            'device',
            'chunksize',
            'data_class',
            'code',
            'comment',
            'coord_class',
            'compression',
            'conventions',
            'date',
            'dimensions',
            'errors',
            'format',
            'group',
            'id',
            'label',
            'name',
            'offset',
            'packdata',
            'pass_number',
            'range',
            'resolution',
            'scale',
            'serial',
            'status',
            'time',
            'title',
            'type',
            'units',
            'varname',
            'version',
            'xml',
        )

        for name in parameters:
            if name in kwargs:
                if (kwargs[name] is None):
                    if kwargs.get('verbose', False):
                        print('Ignoring put keyword argument set to None: "{}"'.format(name))
                else:
                    comm += ', %s=%s' % (name, _quote(kwargs[name]))

        # If it is not specified by the user set compression to 1
        if 'compression' not in kwargs:
            comm += ', compression=1'

        if 'debug' in kwargs:
            comm += ', debug=%d' % int(kwargs['debug'])

        if 'verbose' in kwargs:
            comm += ', verbose=%d' % int(kwargs['verbose'])

        if step == 'create':
            comm += ', /create'
        if step == 'update':
            comm += ', /update'

        keywords = ('nocompliance', 'notstrict', 'unlimited')

        for keyword in keywords:
            if kwargs.get(keyword, False):
                comm += ', /%s' % keyword

        comm += ')'

        if kwargs.get('verbose', False):
            print('instruction: ' + comm)
            print('data to put: ' + str(data_to_put))

        if data_to_put is not None:
            if isinstance(data_to_put, int):
                data_to_put = np.int64(data_to_put)
            elif isinstance(data_to_put, float):
                data_to_put = np.float64(data_to_put)
            elif isinstance(data_to_put, list):
                data_to_put = np.array(data_to_put)
            elif isinstance(data_to_put, str):
                data_to_put = data_to_put.encode()
            elif not isinstance(data_to_put, np.ndarray) and not isinstance(data_to_put, np.generic):
                raise TypeError('invalid data type')

            if isinstance(data_to_put, np.ndarray):
                data_to_put = np.require(data_to_put, requirements=['C'])

                if step == 'variable' and (data_to_put.dtype.kind == 'U' or data_to_put.dtype.kind == 'S'):
                    # We need an additional dimension declared for the 2D char array
                    dim_comm = 'PUTDATA::dimension('
                    if 'file_id' in kwargs:
                        dim_comm += 'fileid=%s' % str(kwargs['file_id']).strip()
                    elif self.put_file_id is not None:
                        dim_comm += 'fileid=%d' % self.put_file_id
                    else:
                        print('No file_id was given, and no file id is stored. Please open the file (either with step_id=create or step_id=update)')
                        return

                    max_str_len = len(max(data_to_put, key=len))
                    dim_comm += ', length=%d' % max_str_len
                    dim_comm += ', group=%s' % kwargs['group']
                    dim_comm += ', name=strdim_%s' % kwargs['name']
                    dim_comm += ')'

                    ret = cpyuda.put_data(dim_comm.encode())

                    if ret.error_code() != 0:
                        raise cpyuda.UDAException(ret.error_message().decode())

            ret = cpyuda.put_data(comm.encode(), data=data_to_put)

            if ret.error_code() != 0:
                raise cpyuda.UDAException(ret.error_message().decode())
        else:
            ret = cpyuda.put_data(comm.encode())

            if ret.error_code() != 0:
                raise cpyuda.UDAException(ret.error_message().decode())

        if step == 'create' or step == 'update':
            self.put_file_id = ret.data()

            if kwargs.get('verbose', False):
                print('Opened file. File index is %s' % str(self.put_file_id))

            if directory is not None:
                self.put_original_path[self.put_file_id] = directory + '/' + args[0]
                self.put_server_path[self.put_file_id] = self.server_tmp_dir + self.put_original_path[self.put_file_id]
            else:
                self.put_original_path[self.put_file_id] = os.path.abspath(args[0])
                self.put_server_path[self.put_file_id] = self.server_tmp_dir + self.put_original_path[self.put_file_id]
        elif step == 'close':
            # Retrieve file from server
            if 'file_id' in kwargs:
                file_id = int(kwargs['file_id'])
            elif self.put_file_id is not None:
                file_id = self.put_file_id
            else:
                print('No file_id was given, and no file id is stored. Please open the file (either with step_id=create or step_id=update)')
                return

            retrieve_comm = "bytes::read(path=%s)" % self.put_server_path[file_id]

            if kwargs.get('verbose', False):
                print("Closed file, retrieving from server: {}".format(retrieve_comm))
                
            bytes_file = cpyuda.get_data(retrieve_comm, "")

            with open(self.put_original_path[file_id], 'wb') as f_out:
                bytes_file.data().tofile(f_out)

            self.put_file_id = None

    def calculate_packing_factors(self, min_range, max_range, nbits):
        scale_factor = (max_range - min_range) / (2**nbits - 1)
        add_offset = min_range + 2**(nbits - 1) * scale_factor

        return scale_factor, add_offset


