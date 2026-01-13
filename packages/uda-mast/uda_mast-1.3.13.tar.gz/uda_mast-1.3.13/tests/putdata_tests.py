import unittest
from pyuda import cpyuda
import tempfile
import os
import numpy as np


#tempfile.mkdtemp()
#DIRECTORY = tempfile.tempdir
#DIRECTORY = '/Users/jhollocombe/Projects/mastcodes/uda/python/tests'
SERVER_TMP_DIR = "/tmp/putdata"
DIRECTORY = '/home/lkogan/mastcodes/uda/python/tests'
FILENAME_FROM_ID = {}


def _delete_file(file_name):
    try:
        os.remove(file_name)
    except FileNotFoundError:
        pass


class PutDataTests(unittest.TestCase):

    def _close_file(self, file_id):
        instruction = "PUTDATA::close(fileid=%d, debug=0, verbose=0)" % file_id
        rc = cpyuda.put_data(instruction.encode())
        self.assertEqual(rc.error_code(), 0)

        server_path = SERVER_TMP_DIR+DIRECTORY+'/'+FILENAME_FROM_ID[file_id]
        bytes_file = cpyuda.get_data("bytes::read(path=%s)" % server_path, "")
        
        local_path = DIRECTORY+'/'+FILENAME_FROM_ID[file_id]
        with open(local_path, 'wb') as f_out:
            bytes_file.data().tofile(f_out)

    def test_creating_file_by_directory_keyword(self, file='test1a.nc', delete_file=True, close_file=True):
        # IDL Test 1A
        if delete_file:
            _delete_file(os.path.join(DIRECTORY, file))
            
        instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', data_class='analysed data'"
                           ", title='Test #1A', shot=123456, pass_number=789, date='02 April 2009', time='09:43'"
                           ", status=1, comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % (file, SERVER_TMP_DIR+DIRECTORY))

        rc = cpyuda.put_data(instruction.encode())

        self.assertEqual(rc.error_code(), 0)

        file_id = rc.data()

        FILENAME_FROM_ID[file_id] = file

        if close_file:
            self._close_file(file_id)

        return file_id

    def test_creating_file_by_full_path(self):
        # IDL Test 1B
        file = 'test1b.nc'
        _delete_file(os.path.join(DIRECTORY, file))

        instruction = ("PUTDATA::open(filename=%s, conventions='Fusion-1.0', data_class='analysed data'"
                           ", title='Test #1A', shot=123456, pass_number=789, date='02 April 2009', time='09:43'"
                           ", status=1, comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % os.path.join(SERVER_TMP_DIR+DIRECTORY, file))

        rc = cpyuda.put_data(instruction.encode())

        self.assertEqual(rc.error_code(), 0)

        file_id = rc.data()

        FILENAME_FROM_ID[file_id] = file

        self._close_file(file_id)

    def test_updating_file_changing_class_of_data(self, file='test1a.nc', close_file=True):
        if not os.path.exists(file):
            test_creating_file_by_directory_keyword(file=file, delete_file=False, close_file=True)

        data_to_put = np.array(bytearray(open(file, "rb+").read()), dtype=np.int8)

        # IDL Test 2A
        instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', data_class='raw data'"
                           ", title='Test #2A', shot=654321, pass_number=987, date='01 April 2009', time='10:52'"
                           ", status=2, comment='Comment for test #2A', code='put_test.py', version=88"
                           ", xml='<xml>Modified XML</xml>', debug=0, verbose=0"
                           ", /update)" % (file, SERVER_TMP_DIR+DIRECTORY))

        rc = cpyuda.put_data(instruction.encode(), data=data_to_put)

        self.assertEqual(rc.error_code(), 0)

        file_id = rc.data()

        FILENAME_FROM_ID[file_id] = file

        if close_file:
            self._close_file(file_id)

        return file_id

    def _put_device(self, file_id, name, serial, type, id, resolution, range, channels):
        instruction = ("PUTDATA::device(fileid=%d, device='%s', serial='%s', type='%s', id='%s'"
                       ", resolution=%d, range=%s, channels=%d, debug=0, verbose=0)"
                       % (file_id, name, serial, type, id, resolution, range, channels))
        rc = cpyuda.put_data(instruction.encode())
        self.assertEqual(rc.error_code(), 0)

    def test_creating_devices_and_attributes(self):
        file = 'test3.nc'
        file_id = self.test_creating_file_by_directory_keyword(file=file, close_file=False)

        self._put_device(file_id, 'dataq1', 'abc123', 'def456', 'identity #1', 16, '100;200', 32)
        self._put_device(file_id, 'dataq2', 'abc234', 'def567', 'identity #2', 16, '100;200', 32)

        instruction = "PUTDATA::attribute(fileid=%d, group='/devices/dataq1', name='notes', debug=0, verbose=0)" % file_id

        rc = cpyuda.put_data(instruction.encode(), 'new stuff on dataq1'.encode())

        self.assertEqual(rc.error_code(), 0)

        instruction = "PUTDATA::attribute(fileid=%d, group='/devices/dataq2', name='notes', debug=0, verbose=0)" % file_id

        rc = cpyuda.put_data(instruction.encode(), 'new stuff on dataq2'.encode())

        self.assertEqual(rc.error_code(), 0)

        self._close_file(file_id)

    def _put_attribute(self, file_id, name, value, group='/a'):
        instruction = "PUTDATA::attribute(fileid=%d, group='%s', name='%s', debug=0, verbose=0)" % (file_id, group, name)
        rc = cpyuda.put_data(instruction.encode(), value)
        self.assertEqual(rc.error_code(), 0)

    def _test_adding_attributes(self):
        file = 'test4.nc'
        file_id = self.test_creating_file_by_directory_keyword(file=file, close_file=False)

        self._put_attribute(file_id, 'stringscalar', 'Hello World')

        self._put_attribute(file_id, 'floatscalar', np.array(3.1415927, dtype=np.float32))
        self._put_attribute(file_id, 'doublescalar', np.array(3.1415927, dtype=np.float64))
        self._put_attribute(file_id, 'bytescalar', np.array(1, dtype=np.int8))
        self._put_attribute(file_id, 'int16scalar', np.array(2, dtype=np.int16))
        self._put_attribute(file_id, 'int32scalar', np.array(3, dtype=np.int32))
        self._put_attribute(file_id, 'int64scalar', np.array(4, dtype=np.int64))
        self._put_attribute(file_id, 'uint16scalar', np.array(5, dtype=np.uint16))
        self._put_attribute(file_id, 'uint32scalar', np.array(6, dtype=np.uint32))
        self._put_attribute(file_id, 'uint64scalar', np.array(7, dtype=np.uint64))

        self._put_attribute(file_id, 'floatscalar', np.array(3.1415927, dtype=np.float32), group='/b')
        self._put_attribute(file_id, 'floatscalar', np.array(2.718281828, dtype=np.float32), group='/b')

        self._put_attribute(file_id, 'complexscalar', np.complex64(6 + 7j), group='/')
        self._put_attribute(file_id, 'complexscalar', np.complex64(6 + 7j), group='/a')
        self._put_attribute(file_id, 'complexscalar', np.complex64(6 + 7j), group='/a/b')

        self._put_attribute(file_id, 'dcomplexscalar', np.complex128(6 + 7j), group='/')
        self._put_attribute(file_id, 'dcomplexscalar', np.complex128(6 + 7j), group='/a')
        self._put_attribute(file_id, 'dcomplexscalar', np.complex128(6 + 7j), group='/a/b')

        self._close_file(file_id)

    def test_updating_attributes(self):
        self._test_adding_attributes()
        file_id = self.test_updating_file_changing_class_of_data(file='test4.nc', close_file=False)

        self._put_attribute(file_id, 'floatarray', np.array([1, 2, 3, 4, 5], dtype=np.float32), group='/a/b')
        self._put_attribute(file_id, 'doublearray', np.array([1, 2, 3, 4, 5], dtype=np.float64), group='/a/b')
        self._put_attribute(file_id, 'bytearray', np.array([1, 2, 3, 4, 5], dtype=np.int8), group='/a/b')
        self._put_attribute(file_id, 'int16array', np.array([1, 2, 3, 4, 5], dtype=np.int16), group='/a/b')
        self._put_attribute(file_id, 'int32array', np.array([1, 2, 3, 4, 5], dtype=np.int32), group='/a/b')
        self._put_attribute(file_id, 'int64array', np.array([1, 2, 3, 4, 5], dtype=np.int64), group='/a/b')
        self._put_attribute(file_id, 'uint16array', np.array([1, 2, 3, 4, 5], dtype=np.uint16), group='/a/b')
        self._put_attribute(file_id, 'uint32array', np.array([1, 2, 3, 4, 5], dtype=np.uint32), group='/a/b')
        self._put_attribute(file_id, 'uint64array', np.array([1, 2, 3, 4, 5], dtype=np.uint64), group='/a/b')

        self._put_attribute(file_id, 'complexarray', np.complex64([16 + 17j, 18 + 19j]), group='/a/b')

        self._put_attribute(file_id, 'dcomplexarray', np.complex128([16.5 + 17.5j, 18.5 + 19.5j]), group='/a/b')

        self._close_file(file_id)


    def _put_dimension(self, file_id, group, name, length=None, unlimited=False):
        extra_args = ''
        if unlimited:
            extra_args = ', /unlimited'
        elif length:
            extra_args = ', length=%d' % length
        instruction = "PUTDATA::dimension(fileid=%d, group='%s', name='%s', debug=0, verbose=0%s)"\
                      % (file_id, group, name, extra_args)
        rc = cpyuda.put_data(instruction.encode(), None)
        self.assertEqual(rc.error_code(), 0)


    def _test_writing_dimensions(self):
        file = 'test6.nc'
        file_id = self.test_creating_file_by_directory_keyword(file=file, close_file=False)

        self._put_dimension(file_id, '/a', 'unit', 1)
        self._put_dimension(file_id, '/a', 'y', 5)
        self._put_dimension(file_id, '/a', 'x', 2)
        self._put_dimension(file_id, '/a', 'time', 0, unlimited=True)
        self._put_dimension(file_id, '/a', 't')
        self._put_dimension(file_id, '/a/b', 'single', 1)
        self._put_dimension(file_id, '/a/b', 'y', 6)
        self._put_dimension(file_id, '/a/b', 'x', 3)

        self._close_file(file_id)

    def _put_coordinate(self, file_id, group, name, units, label, value, time=False):
        instruction = "PUTDATA::coordinate(fileid=%d, group='%s', name='%s', units='%s', label='%s', debug=0, verbose=0, %s)" \
                      % (file_id, group, name, units, label, ", class='time'" if time else '')
        rc = cpyuda.put_data(instruction.encode(), value)
        self.assertEqual(rc.error_code(), 0)

    def _test_writing_coordinates_for_arrays(self):
        self._test_writing_dimensions()
        file_id = self.test_updating_file_changing_class_of_data(file='test6.nc', close_file=False)

        self._put_coordinate(file_id, '/a', 'y', 'm', 'y-label', np.array([1, 2, 3, 4, 5], dtype=np.float32))
        self._put_coordinate(file_id, '/a', 'x', 'A', 'x-label', np.array([-1, -2], dtype=np.float64))
        self._put_coordinate(file_id, '/a/b', 'y', 'kg', 'y-label', np.array([1, 2, 3, 4, 5, 6], dtype=np.float32))
        self._put_coordinate(file_id, '/a/b', 'x', 'N', 'x-label', np.array([-1, -2, -3], dtype=np.float64))

        self._put_coordinate(file_id, '/a', 'time', 's', 'time', np.array([-1, 0, 1, 2, 3, 4], dtype=np.float32), time=True)
        self._put_coordinate(file_id, '/a', 't', 's', 'time', np.array([-4, 0, 4], dtype=np.float64), time=True)

        self._close_file(file_id)

    def test_writing_coordinates_for_scalars(self):        
        self._test_writing_coordinates_for_arrays()
        file_id = self.test_updating_file_changing_class_of_data(file='test6.nc', close_file=False)

        self._put_coordinate(file_id, '/a', 'unit', 'counts', 'unitary pi value', np.array(3.14159, dtype=np.float32))
        self._put_coordinate(file_id, '/a/b', 'single', 'counts', 'unitary e value', np.array(2.71828, dtype=np.float64))

        self._put_dimension(file_id, '/a/b/c', 'byte', 1)
        self._put_dimension(file_id, '/a/b/c', 'int16', 1)
        self._put_dimension(file_id, '/a/b/c', 'int32', 1)
        self._put_dimension(file_id, '/a/b/c', 'int64', 1)
        self._put_dimension(file_id, '/a/b/c', 'uint16', 1)
        self._put_dimension(file_id, '/a/b/c', 'uint32', 1)
        self._put_dimension(file_id, '/a/b/c', 'uint64', 1)
        self._put_dimension(file_id, '/a/b/c', 'complex', 1)
        self._put_dimension(file_id, '/a/b/c', 'dcomplex', 1)

        self._put_coordinate(file_id, '/a/b/c', 'byte', '', '', np.array(10, dtype=np.int8))
        self._put_coordinate(file_id, '/a/b/c', 'int16', '', '', np.array(20, dtype=np.int16))
        self._put_coordinate(file_id, '/a/b/c', 'int32', '', '', np.array(30, dtype=np.int32))
        self._put_coordinate(file_id, '/a/b/c', 'int64', '', '', np.array(40, dtype=np.int64))
        self._put_coordinate(file_id, '/a/b/c', 'uint16', '', '', np.array(50, dtype=np.uint16))
        self._put_coordinate(file_id, '/a/b/c', 'uint32', '', '', np.array(60, dtype=np.uint32))
        self._put_coordinate(file_id, '/a/b/c', 'uint64', '', '', np.array(70, dtype=np.uint64))
        self._put_coordinate(file_id, '/a/b/c', 'complex', '', '', np.complex64(80 + 90j))
        self._put_coordinate(file_id, '/a/b/c', 'dcomplex', '', '', np.complex128(90 + 100j))

        self._close_file(file_id)

    def test_writing_array_coordinates(self):
        # IDL test 9
        file_id  = self.test_creating_file_by_directory_keyword('test9.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'float', 3)
        self._put_dimension(file_id, '/a', 'double', 3)
        self._put_dimension(file_id, '/a', 'byte', 3)
        self._put_dimension(file_id, '/a', 'int16', 3)
        self._put_dimension(file_id, '/a', 'int32', 3)
        self._put_dimension(file_id, '/a', 'int64', 3)
        self._put_dimension(file_id, '/a', 'uint16', 3)
        self._put_dimension(file_id, '/a', 'uint32', 3)
        self._put_dimension(file_id, '/a', 'uint64', 3)
        self._put_dimension(file_id, '/a', 'complex', 3)
        self._put_dimension(file_id, '/a', 'dcomplex', 3)

        self._put_coordinate(file_id, '/a', 'float', '', '', np.arange(3, dtype=np.float32))
        self._put_coordinate(file_id, '/a', 'double', '', '', np.arange(3, dtype=np.float64))
        self._put_coordinate(file_id, '/a', 'byte', '', '', np.arange(3, dtype=np.int8))
        self._put_coordinate(file_id, '/a', 'int16', '', '', np.arange(3, dtype=np.int16))
        self._put_coordinate(file_id, '/a', 'int32', '', '', np.arange(3, dtype=np.int32))
        self._put_coordinate(file_id, '/a', 'int64', '', '', np.arange(3, dtype=np.int64))
        self._put_coordinate(file_id, '/a', 'uint32', '', '', np.arange(3, dtype=np.uint16))
        self._put_coordinate(file_id, '/a', 'uint64', '', '', np.arange(3, dtype=np.uint32))
        self._put_coordinate(file_id, '/a', 'uint16', '', '', np.arange(3, dtype=np.uint64))
        self._put_coordinate(file_id, '/a', 'complex', '', '', np.complex64(range(3)))
        self._put_coordinate(file_id, '/a', 'dcomplex', '', '', np.complex128(range(3)))

        self._close_file(file_id)

    def test_writing_unlimited_coordinates(self):
        # IDL test 10
        file_id = self.test_creating_file_by_directory_keyword('test10.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'float', unlimited=True)
        self._put_dimension(file_id, '/a', 'double', unlimited=True)
        self._put_dimension(file_id, '/a', 'byte', unlimited=True)
        self._put_dimension(file_id, '/a', 'int16', unlimited=True)
        self._put_dimension(file_id, '/a', 'int32', unlimited=True)
        self._put_dimension(file_id, '/a', 'int64', unlimited=True)
        self._put_dimension(file_id, '/a', 'uint16', unlimited=True)
        self._put_dimension(file_id, '/a', 'uint32', unlimited=True)
        self._put_dimension(file_id, '/a', 'uint64', unlimited=True)
        self._put_dimension(file_id, '/a', 'complex', unlimited=True)
        self._put_dimension(file_id, '/a', 'dcomplex', unlimited=True)

        self._put_coordinate(file_id, '/a', 'float', '', '', np.arange(3, dtype=np.float32))
        self._put_coordinate(file_id, '/a', 'double', '', '', np.arange(3, dtype=np.float64))
        self._put_coordinate(file_id, '/a', 'byte', '', '', np.arange(3, dtype=np.int8))
        self._put_coordinate(file_id, '/a', 'int16', '', '', np.arange(3, dtype=np.int16))
        self._put_coordinate(file_id, '/a', 'int32', '', '', np.arange(3, dtype=np.int32))
        self._put_coordinate(file_id, '/a', 'int64', '', '', np.arange(3, dtype=np.int64))
        self._put_coordinate(file_id, '/a', 'uint32', '', '', np.arange(3, dtype=np.uint16))
        self._put_coordinate(file_id, '/a', 'uint64', '', '', np.arange(3, dtype=np.uint32))
        self._put_coordinate(file_id, '/a', 'uint16', '', '', np.arange(3, dtype=np.uint64))
        self._put_coordinate(file_id, '/a', 'complex', '', '', np.arange(3, dtype=np.complex64))
        self._put_coordinate(file_id, '/a', 'dcomplex', '', '', np.arange(3, dtype=np.complex128))

        self._close_file(file_id)


    def _put_coordinate2(self, file_id, group, name, value, starts, increments, counts=None, label="", units=""):
        start = ';'.join(str(i) for i in starts)
        increment = ';'.join(str(i) for i in increments)
        if counts is not None:
            count = ';'.join(str(i) for i in counts)
        else:
            count = None
        instruction = "PUTDATA::coordinate(fileid=%d, group='%s', name='%s', starts=%s, increments=%s, label='%s', units='%s', debug=0, verbose=0%s)"\
                      % (file_id, group, name, start, increment, label, units, ', counts=%s' % count if count is not None else '')
        rc = cpyuda.put_data(instruction.encode(), value)
        self.assertEqual(rc.error_code(), 0)

    def test_writing_coordinates_using_start_increment_and_count(self):
        # IDL test 11
        file_id = self.test_creating_file_by_directory_keyword('test11.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'm', 3)
        self._put_dimension(file_id, '/a', 'n', 3)
        self._put_dimension(file_id, '/a', 'o', 3)
        self._put_dimension(file_id, '/a', 'p', 3)

        starts      = [0.0]
        increments  = [0.5]
        counts      = [3]

        self._put_coordinate2(file_id, '/a', 'm', None, starts, increments)
        self._put_coordinate2(file_id, '/a', 'n', None, starts, increments, counts=counts)
        self._put_coordinate2(file_id, '/a', 'o', np.array([-1, -2, -3], dtype=np.float32), starts, increments)
        self._put_coordinate2(file_id, '/a', 'p', np.array([-1, -2, -3], dtype=np.float32), starts, increments, counts=counts)

        self._close_file(file_id)

    def _put_variable(self, file_id, group, name, dimensions, value, **kwargs):
        extra = ', '.join('%s=%s' % (k, v) for k, v in kwargs.items())
        if extra:
            extra = ', ' + extra
        instruction = "PUTDATA::variable(fileid=%d, group='%s', name='%s', dimensions='%s', debug=0, verbose=0%s)"\
                      % (file_id, group, name, dimensions, extra)
        rc = cpyuda.put_data(instruction.encode(), value)
        self.assertEqual(rc.error_code(), 0)

    def test_writing_variables_with_scalar_data(self):
        # IDL test 12
        file_id = self.test_creating_file_by_directory_keyword('test12.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'x', 1)
        self._put_coordinate(file_id, '/a', 'x', '', '', np.array(3.1415927, dtype=np.float32))
        self._put_device(file_id, 'abc123', 'abc321', 'def456', 'identity #1', 16, '100;200', 32)

        self._put_variable(file_id, '/a', 'float', 'x', np.array(1.0E3, dtype=np.float32), label='test label',
                           units='counts.m/s^2', scale=10.0, offset=-1.0, device='abc123', channels=1, comment='test comment')

        self._put_variable(file_id, '/a', 'double', 'x', np.array(2.0E3, dtype=np.float64), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte', 'x', np.array(30, dtype=np.int8), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16', 'x', np.array(40, dtype=np.int16), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32', 'x', np.array(50, dtype=np.int32), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64', 'x', np.array(60, dtype=np.int64), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16', 'x', np.array(70, dtype=np.uint16), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32', 'x', np.array(80, dtype=np.uint32), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64', 'x', np.array(90, dtype=np.uint64), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex', 'x', np.complex64(100 + 110j), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex', 'x', np.complex128(120 + 130j), label='test', units="m")

        self._close_file(file_id)

    def test_writing_variables_with_1d_data(self):
        # IDL test 13
        file_id = self.test_creating_file_by_directory_keyword('test13.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'x', 3)
        self._put_coordinate(file_id, '/a', 'x', '', '', np.array([1.0, 2.0, 3.0], dtype=np.float32))
        self._put_device(file_id, 'abc123', 'abc321', 'def456', 'identity #1', 16, '100;200', 32)

        self._put_variable(file_id, '/a', 'float', 'x', np.array([4, 5, 6], dtype=np.float32), label='test label',
                           units='m.A N*s-kg', scale=10.0, offset=-1.0, device='abc123', channels=1, comment='test comment')

        self._put_variable(file_id, '/a', 'double', 'x', np.arange(3, dtype=np.float64), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte', 'x', np.arange(3, dtype=np.int8), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16', 'x', np.arange(3, dtype=np.int16), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32', 'x', np.arange(3, dtype=np.int32), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64', 'x', np.arange(3, dtype=np.int64), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16', 'x', np.arange(3, dtype=np.uint16), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32', 'x', np.arange(3, dtype=np.uint32), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64', 'x', np.arange(3, dtype=np.uint64), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex', 'x', np.arange(3, dtype=np.complex64), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex', 'x', np.arange(3, dtype=np.complex128), label='test', units="m")

        self._close_file(file_id)

    def test_writing_variables_with_2d_data(self):
        # IDL test 14
        file_id = self.test_creating_file_by_directory_keyword('test14.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'x', 4)
        self._put_dimension(file_id, '/a', 'y', 2)
        self._put_coordinate(file_id, '/a', 'x', '', '', np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32))
        self._put_coordinate(file_id, '/a', 'y', '', '', np.array([4.0, 5.0], dtype=np.float32))
        self._put_device(file_id, 'abc123', 'abc321', 'def456', 'identity #1', 16, '100;200', 32)

        self._put_variable(file_id, '/a', 'float', 'x;y', np.arange(8, dtype=np.float32).reshape(4, 2), label='test label',
                           units='m', scale=10.0, offset=-1.0, device='abc123', channels=1, comment='test comment')

        self._put_variable(file_id, '/a', 'double', 'x;y', np.arange(8, dtype=np.float64).reshape(4, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte', 'x;y', np.arange(8, dtype=np.int8).reshape(4, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16', 'x;y', np.arange(8, dtype=np.int16).reshape(4, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32', 'x;y', np.arange(8, dtype=np.int32).reshape(4, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64', 'x;y', np.arange(8, dtype=np.int64).reshape(4, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16', 'x;y', np.arange(8, dtype=np.uint16).reshape(4, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32', 'x;y', np.arange(8, dtype=np.uint32).reshape(4, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64', 'x;y', np.arange(8, dtype=np.uint64).reshape(4, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex', 'x;y', np.arange(8, dtype=np.complex64).reshape(4, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex', 'x;y', np.arange(8, dtype=np.complex128).reshape(4, 2), label='test', units="m")

        self._close_file(file_id)

    def test_writing_variables_with_3d_data(self):
        # IDL test 15
        file_id = self.test_creating_file_by_directory_keyword('test15.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'x', 3)
        self._put_dimension(file_id, '/a', 'y', 2)
        self._put_dimension(file_id, '/a', 'z', 2)
        self._put_coordinate(file_id, '/a', 'x', '', '', np.array([1.0, 2.0, 3.0], dtype=np.float32))
        self._put_coordinate(file_id, '/a', 'y', '', '', np.array([4.0, 5.0], dtype=np.float32))
        self._put_coordinate(file_id, '/a', 'z', '', '', np.array([6.0, 7.0], dtype=np.float32))
        self._put_device(file_id, 'abc123', 'abc321', 'def456', 'identity #1', 16, '100;200', 32)

        self._put_variable(file_id, '/a', 'float', 'x;y;z', np.arange(12, dtype=np.float32).reshape(3, 2, 2), label='test label',
                           units='s', scale=10.0, offset=-1.0, device='abc123', channels=1, comment='test comment')

        self._put_variable(file_id, '/a', 'double', 'x;y;z', np.arange(12, dtype=np.float64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte', 'x;y;z', np.arange(12, dtype=np.int8).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16', 'x;y;z', np.arange(12, dtype=np.int16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32', 'x;y;z', np.arange(12, dtype=np.int32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64', 'x;y;z', np.arange(12, dtype=np.int64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16', 'x;y;z', np.arange(12, dtype=np.uint16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32', 'x;y;z', np.arange(12, dtype=np.uint32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64', 'x;y;z', np.arange(12, dtype=np.uint64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex', 'x;y;z', np.arange(12, dtype=np.complex64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex', 'x;y;z', np.arange(12, dtype=np.complex128).reshape(3, 2, 2), label='test', units="m")

        self._close_file(file_id)

    def test_writing_scalar_variables_with_unlimited_dimension(self):
        # IDL test 16
        file_id = self.test_creating_file_by_directory_keyword('test16.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'x', None, unlimited=True)

        self._put_variable(file_id, '/a', 'float', 'x', np.array(10, dtype=np.float32), label='test', units="m")
        self._put_variable(file_id, '/a', 'double', 'x', np.array(20, dtype=np.float64), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte', 'x', np.array(30, dtype=np.int8), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16', 'x', np.array(40, dtype=np.int16), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32', 'x', np.array(50, dtype=np.int32), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64', 'x', np.array(60, dtype=np.int64), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16', 'x', np.array(70, dtype=np.uint16), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32', 'x', np.array(80, dtype=np.uint32), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64', 'x', np.array(90, dtype=np.uint64), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex', 'x', np.complex64(100 + 110j), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex', 'x', np.complex128(120 + 130j), label='test', units="m")

        self._close_file(file_id)

    def test_writing_1d_variables_with_unlimited_dimension(self):
        # IDL test 17
        file_id = self.test_creating_file_by_directory_keyword('test17.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'x', None, unlimited=True)

        self._put_variable(file_id, '/a', 'float', 'x', np.arange(3, dtype=np.float32), label='test', units="m")
        self._put_variable(file_id, '/a', 'double', 'x', np.arange(3, dtype=np.float64), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte', 'x', np.arange(3, dtype=np.int8), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16', 'x', np.arange(3, dtype=np.int16), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32', 'x', np.arange(3, dtype=np.int32), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64', 'x', np.arange(3, dtype=np.int64), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16', 'x', np.arange(3, dtype=np.uint16), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32', 'x', np.arange(3, dtype=np.uint32), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64', 'x', np.arange(3, dtype=np.uint64), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex', 'x', np.arange(3, dtype=np.complex64), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex', 'x', np.arange(3, dtype=np.complex128), label='test', units="m")

        self._close_file(file_id)

    def test_writing_2d_variables_with_unlimited_dimension(self):
        # IDL test 18
        file_id = self.test_creating_file_by_directory_keyword('test18.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'x', None, unlimited=True)
        self._put_dimension(file_id, '/a', 'y', None, unlimited=True)
        self._put_dimension(file_id, '/a', 'x3', 3)
        self._put_dimension(file_id, '/a', 'y2', 2)

        self._put_variable(file_id, '/a', 'float', 'x;y', np.arange(6, dtype=np.float32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double', 'x;y', np.arange(6, dtype=np.float64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte', 'x;y', np.arange(6, dtype=np.int8).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16', 'x;y', np.arange(6, dtype=np.int16).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32', 'x;y', np.arange(6, dtype=np.int32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64', 'x;y', np.arange(6, dtype=np.int64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16', 'x;y', np.arange(6, dtype=np.uint16).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32', 'x;y', np.arange(6, dtype=np.uint32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64', 'x;y', np.arange(6, dtype=np.uint64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex', 'x;y', np.arange(6, dtype=np.complex64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex', 'x;y', np.arange(6, dtype=np.complex128).reshape(3, 2), label='test', units="m")

        self._put_variable(file_id, '/a', 'float_2', 'x3;y', np.arange(6, dtype=np.float32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double_2', 'x3;y', np.arange(6, dtype=np.float64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte_2', 'x3;y', np.arange(6, dtype=np.int8).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16_2', 'x3;y', np.arange(6, dtype=np.int16).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32_2', 'x3;y', np.arange(6, dtype=np.int32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64_2', 'x3;y', np.arange(6, dtype=np.int64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16_2', 'x3;y', np.arange(6, dtype=np.uint16).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32_2', 'x3;y', np.arange(6, dtype=np.uint32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64_2', 'x3;y', np.arange(6, dtype=np.uint64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex_2', 'x3;y', np.arange(6, dtype=np.complex64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex_2', 'x3;y', np.arange(6, dtype=np.complex128).reshape(3, 2), label='test', units="m")

        self._put_variable(file_id, '/a', 'float_3', 'x;y2', np.arange(6, dtype=np.float32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double_3', 'x;y2', np.arange(6, dtype=np.float64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte_3', 'x;y2', np.arange(6, dtype=np.int8).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16_3', 'x;y2', np.arange(6, dtype=np.int16).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32_3', 'x;y2', np.arange(6, dtype=np.int32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64_3', 'x;y2', np.arange(6, dtype=np.int64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16_3', 'x;y2', np.arange(6, dtype=np.uint16).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32_3', 'x;y2', np.arange(6, dtype=np.uint32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64_3', 'x;y2', np.arange(6, dtype=np.uint64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex_3', 'x;y2', np.arange(6, dtype=np.complex64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex_3', 'x;y2', np.arange(6, dtype=np.complex128).reshape(3, 2), label='test', units="m")

        self._close_file(file_id)

    def test_writing_3d_variables_with_unlimited_dimension(self):
        # IDL test 19
        file_id = self.test_creating_file_by_directory_keyword('test19.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'x', None, unlimited=True)
        self._put_dimension(file_id, '/a', 'y', None, unlimited=True)
        self._put_dimension(file_id, '/a', 'z', None, unlimited=True)
        self._put_dimension(file_id, '/a', 'x3', 3)
        self._put_dimension(file_id, '/a', 'y2', 2)
        self._put_dimension(file_id, '/a', 'z2', 2)

        self._put_variable(file_id, '/a', 'float', 'x;y;z', np.arange(12, dtype=np.float32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double', 'x;y;z', np.arange(12, dtype=np.float64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte', 'x;y;z', np.arange(12, dtype=np.int8).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16', 'x;y;z', np.arange(12, dtype=np.int16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32', 'x;y;z', np.arange(12, dtype=np.int32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64', 'x;y;z', np.arange(12, dtype=np.int64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16', 'x;y;z', np.arange(12, dtype=np.uint16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32', 'x;y;z', np.arange(12, dtype=np.uint32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64', 'x;y;z', np.arange(12, dtype=np.uint64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex', 'x;y;z', np.arange(12, dtype=np.complex64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex', 'x;y;z', np.arange(12, dtype=np.complex128).reshape(3, 2, 2), label='test', units="m")

        self._put_variable(file_id, '/a', 'float_2', 'x3;y;z', np.arange(12, dtype=np.float32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double_2', 'x3;y;z', np.arange(12, dtype=np.float64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte_2', 'x3;y;z', np.arange(12, dtype=np.int8).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16_2', 'x3;y;z', np.arange(12, dtype=np.int16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32_2', 'x3;y;z', np.arange(12, dtype=np.int32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64_2', 'x3;y;z', np.arange(12, dtype=np.int64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16_2', 'x3;y;z', np.arange(12, dtype=np.uint16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32_2', 'x3;y;z', np.arange(12, dtype=np.uint32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64_2', 'x3;y;z', np.arange(12, dtype=np.uint64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex_2', 'x3;y;z', np.arange(12, dtype=np.complex64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex_2', 'x3;y;z', np.arange(12, dtype=np.complex128).reshape(3, 2, 2), label='test', units="m")

        self._put_variable(file_id, '/a', 'float_3', 'x;y2;z', np.arange(12, dtype=np.float32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double_3', 'x;y2;z', np.arange(12, dtype=np.float64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte_3', 'x;y2;z', np.arange(12, dtype=np.int8).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16_3', 'x;y2;z', np.arange(12, dtype=np.int16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32_3', 'x;y2;z', np.arange(12, dtype=np.int32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64_3', 'x;y2;z', np.arange(12, dtype=np.int64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16_3', 'x;y2;z', np.arange(12, dtype=np.uint16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32_3', 'x;y2;z', np.arange(12, dtype=np.uint32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64_3', 'x;y2;z', np.arange(12, dtype=np.uint64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex_3', 'x;y2;z', np.arange(12, dtype=np.complex64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex_3', 'x;y2;z', np.arange(12, dtype=np.complex128).reshape(3, 2, 2), label='test', units="m")

        self._put_variable(file_id, '/a', 'float_4', 'x;y;z2', np.arange(12, dtype=np.float32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double_4', 'x;y;z2', np.arange(12, dtype=np.float64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte_4', 'x;y;z2', np.arange(12, dtype=np.int8).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16_4', 'x;y;z2', np.arange(12, dtype=np.int16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32_4', 'x;y;z2', np.arange(12, dtype=np.int32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64_4', 'x;y;z2', np.arange(12, dtype=np.int64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16_4', 'x;y;z2', np.arange(12, dtype=np.uint16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32_4', 'x;y;z2', np.arange(12, dtype=np.uint32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64_4', 'x;y;z2', np.arange(12, dtype=np.uint64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex_4', 'x;y;z2', np.arange(12, dtype=np.complex64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex_4', 'x;y;z2', np.arange(12, dtype=np.complex128).reshape(3, 2, 2), label='test', units="m")

        self._put_variable(file_id, '/a', 'float_5', 'x3;y2;z', np.arange(12, dtype=np.float32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double_5', 'x3;y2;z', np.arange(12, dtype=np.float64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte_5', 'x3;y2;z', np.arange(12, dtype=np.int8).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16_5', 'x3;y2;z', np.arange(12, dtype=np.int16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32_5', 'x3;y2;z', np.arange(12, dtype=np.int32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64_5', 'x3;y2;z', np.arange(12, dtype=np.int64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16_5', 'x3;y2;z', np.arange(12, dtype=np.uint16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32_5', 'x3;y2;z', np.arange(12, dtype=np.uint32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64_5', 'x3;y2;z', np.arange(12, dtype=np.uint64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex_5', 'x3;y2;z', np.arange(12, dtype=np.complex64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex_5', 'x3;y2;z', np.arange(12, dtype=np.complex128).reshape(3, 2, 2), label='test', units="m")

        self._put_variable(file_id, '/a', 'float_6', 'x;y2;z2', np.arange(12, dtype=np.float32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double_6', 'x;y2;z2', np.arange(12, dtype=np.float64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte_6', 'x;y2;z2', np.arange(12, dtype=np.int8).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16_6', 'x;y2;z2', np.arange(12, dtype=np.int16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32_6', 'x;y2;z2', np.arange(12, dtype=np.int32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64_6', 'x;y2;z2', np.arange(12, dtype=np.int64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16_6', 'x;y2;z2', np.arange(12, dtype=np.uint16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32_6', 'x;y2;z2', np.arange(12, dtype=np.uint32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64_6', 'x;y2;z2', np.arange(12, dtype=np.uint64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex_6', 'x;y2;z2', np.arange(12, dtype=np.complex64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex_6', 'x;y2;z2', np.arange(12, dtype=np.complex128).reshape(3, 2, 2), label='test', units="m")

        self._put_variable(file_id, '/a', 'float_7', 'x3;y;z2', np.arange(12, dtype=np.float32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'double_7', 'x3;y;z2', np.arange(12, dtype=np.float64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'byte_7', 'x3;y;z2', np.arange(12, dtype=np.int8).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int16_7', 'x3;y;z2', np.arange(12, dtype=np.int16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int32_7', 'x3;y;z2', np.arange(12, dtype=np.int32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'int64_7', 'x3;y;z2', np.arange(12, dtype=np.int64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint16_7', 'x3;y;z2', np.arange(12, dtype=np.uint16).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint32_7', 'x3;y;z2', np.arange(12, dtype=np.uint32).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'uint64_7', 'x3;y;z2', np.arange(12, dtype=np.uint64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'complex_7', 'x3;y;z2', np.arange(12, dtype=np.complex64).reshape(3, 2, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'dcomplex_7', 'x3;y;z2', np.arange(12, dtype=np.complex128).reshape(3, 2, 2), label='test', units="m")

        self._close_file(file_id)

    def test_opening_multiple_files_at_one_time(self):
        # IDL test 20
        file_id1 = self.test_creating_file_by_directory_keyword('test20a.nc', close_file=False)
        file_id2 = self.test_creating_file_by_directory_keyword('test20b.nc', close_file=False)
        file_id3 = self.test_creating_file_by_directory_keyword('test20c.nc', close_file=False)
        file_id4 = self.test_creating_file_by_directory_keyword('test20d.nc', close_file=False)

        self._put_dimension(file_id1, '/a', 'x1', 1)
        self._put_dimension(file_id2, '/a', 'x2', 2)
        self._put_dimension(file_id3, '/a', 'x3', 3)
        self._put_dimension(file_id4, '/a', 'x4', 4)

        self._put_coordinate(file_id1, '/a', 'x1', '', '', np.arange(1, dtype=np.int32))
        self._put_coordinate(file_id2, '/a', 'x2', '', '', np.arange(2, dtype=np.int32))
        self._put_coordinate(file_id3, '/a', 'x3', '', '', np.arange(3, dtype=np.int32))
        self._put_coordinate(file_id4, '/a', 'x4', '', '', np.arange(4, dtype=np.int32))

        self._put_variable(file_id1, '/a', 'xx1', 'x1', np.arange(1, dtype=np.float32) * np.pi, label='test', units="m")
        self._put_variable(file_id2, '/a', 'xx2', 'x2', np.arange(2, dtype=np.float32) * np.pi, label='test', units="m")
        self._put_variable(file_id3, '/a', 'xx3', 'x3', np.arange(3, dtype=np.float32) * np.pi, label='test', units="m")
        self._put_variable(file_id4, '/a', 'xx4', 'x4', np.arange(4, dtype=np.float32) * np.pi, label='test', units="m")

        self._close_file(file_id1)
        self._close_file(file_id2)
        self._close_file(file_id3)
        self._close_file(file_id4)

    def test_writing_variables_with_errors(self):
        # IDL test 21
        file_id = self.test_creating_file_by_directory_keyword('test21.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'scalardim', 1)
        self._put_dimension(file_id, '/a', 'x', 3)
        self._put_dimension(file_id, '/a', 'y', 2)
        self._put_coordinate(file_id, '/a', 'scalardim', '', '', np.float32(20.0))
        self._put_coordinate(file_id, '/a', 'x', '', '', np.array([1.0, 2.0, 3.0], dtype=np.float32))
        self._put_coordinate(file_id, '/a', 'y', '', '', np.array([4.0, 5.0], dtype=np.float32))

        self._put_variable(file_id, '/a', 'escalar', 'scalardim', np.float32(12.3), label='test', units="m")
        self._put_variable(file_id, '/a', 'efloat', 'x;y', np.arange(6, dtype=np.float32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'edouble', 'x;y', np.arange(6, dtype=np.float64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'ebyte', 'x;y', np.arange(6, dtype=np.int8).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'eint16', 'x;y', np.arange(6, dtype=np.int16).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'eint32', 'x;y', np.arange(6, dtype=np.int32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'eint64', 'x;y', np.arange(6, dtype=np.int64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'euint16', 'x;y', np.arange(6, dtype=np.uint16).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'euint32', 'x;y', np.arange(6, dtype=np.uint32).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'euint64', 'x;y', np.arange(6, dtype=np.uint64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'ecomplex', 'x;y', np.arange(6, dtype=np.complex64).reshape(3, 2), label='test', units="m")
        self._put_variable(file_id, '/a', 'edcomplex', 'x;y', np.arange(6, dtype=np.complex128).reshape(3, 2), label='test', units="m")

        self._put_variable(file_id, '/a', 'scalar', 'scalardim', np.float32(321.0), label='test', units="m", errors='escalar')
        self._put_variable(file_id, '/a', 'float', 'x;y', np.arange(6, dtype=np.float32).reshape(3, 2), label='test', units="m", errors='efloat')
        self._put_variable(file_id, '/a', 'double', 'x;y', np.arange(6, dtype=np.float64).reshape(3, 2), label='test', units="m", errors='edouble')
        self._put_variable(file_id, '/a', 'byte', 'x;y', np.arange(6, dtype=np.int8).reshape(3, 2), label='test', units="m", errors='ebyte')
        self._put_variable(file_id, '/a', 'int16', 'x;y', np.arange(6, dtype=np.int16).reshape(3, 2), label='test', units="m", errors='eint16')
        self._put_variable(file_id, '/a', 'int32', 'x;y', np.arange(6, dtype=np.int32).reshape(3, 2), label='test', units="m", errors='eint32')
        self._put_variable(file_id, '/a', 'int64', 'x;y', np.arange(6, dtype=np.int64).reshape(3, 2), label='test', units="m", errors='eint64')
        self._put_variable(file_id, '/a', 'uint16', 'x;y', np.arange(6, dtype=np.uint16).reshape(3, 2), label='test', units="m", errors='euint16')
        self._put_variable(file_id, '/a', 'uint32', 'x;y', np.arange(6, dtype=np.uint32).reshape(3, 2), label='test', units="m", errors='euint32')
        self._put_variable(file_id, '/a', 'uint64', 'x;y', np.arange(6, dtype=np.uint64).reshape(3, 2), label='test', units="m", errors='euint64')
        self._put_variable(file_id, '/a', 'complex', 'x;y', np.arange(6, dtype=np.complex64).reshape(3, 2), label='test', units="m", errors='ecomplex')
        self._put_variable(file_id, '/a', 'dcomplex', 'x;y', np.arange(6, dtype=np.complex128).reshape(3, 2), label='test', units="m", errors='edcomplex')

        self._close_file(file_id)


    def test_writing_dimensions_using_start_increment_and_count(self):
        # IDL test 22
        file_id = self.test_creating_file_by_directory_keyword('test22.nc', close_file=False)

        self._put_dimension(file_id, '/a', 'm', 9)
        self._put_dimension(file_id, '/a', 'n', 0, unlimited=True)
        self._put_dimension(file_id, '/a', 'p', 9)

        starts     = np.array([0.0, 10.0, 20.0], dtype=np.float64)
        increments = np.array([0.5, 0.1, 0.2], dtype=np.float64)
        counts     = np.array([3, 3, 3], dtype=np.uint32)

        self._put_coordinate2(file_id, '/a', 'm', None, starts, increments, counts=counts)
        self._put_coordinate2(file_id, '/a', 'n', None, starts, increments, counts=counts)

        self._put_coordinate2(file_id, '/a', 'p',
                              np.array([0, 0.5, 1, 10, 10.1, 10.2, 20, 20.2, 20.4], dtype=np.float32),
                              starts, increments, counts=counts)

        self._close_file(file_id)

    def test_create_fail_required_attributes(self):
        file = 'test23.nc'        

        _delete_file(os.path.join(DIRECTORY, file))

        # No title
        instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', data_class='analysed data'"
                           ", shot=123456, pass_number=789, date='02 April 2009', time='09:43'"
                           ", status=1, comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % (file, SERVER_TMP_DIR+DIRECTORY))

        rc = cpyuda.put_data(instruction.encode())

        self.assertNotEqual(rc.error_code(), 0)

        # No class specified
        instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', "
                           ", title='Test #1A', shot=123456, pass_number=789, date='02 April 2009', time='09:43'"
                           ", status=1, comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % (file, SERVER_TMP_DIR+DIRECTORY))

        rc = cpyuda.put_data(instruction.encode())

        self.assertNotEqual(rc.error_code(), 0)

        # Invalid class
        instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', data_class='something or another'"
                           ", title='Test #1A', shot=123456, pass_number=789, date='02 April 2009', time='09:43'"
                           ", status=1, comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % (file, SERVER_TMP_DIR+DIRECTORY))

        rc = cpyuda.put_data(instruction.encode())

        self.assertNotEqual(rc.error_code(), 0)

        # No conventions
        instruction = ("PUTDATA::open(filename=%s, directory=%s, data_class='analysed data'"
                           ", title='Test #1A', shot=123456, pass_number=789, date='02 April 2009', time='09:43'"
                           ", status=1, comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % (file, SERVER_TMP_DIR+DIRECTORY))

        rc = cpyuda.put_data(instruction.encode())

        self.assertNotEqual(rc.error_code(), 0)

        # Raw data, no shot given
        instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', data_class='raw data'"
                           ", title='Test #1A', date='02 April 2009', time='09:43'"
                           ", comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % (file, SERVER_TMP_DIR+DIRECTORY))
        
        rc = cpyuda.put_data(instruction.encode())

        self.assertNotEqual(rc.error_code(), 0)

        # Analysed data, no shot given
        instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', data_class='analysed data'"
                           ", title='Test #1A', pass_number=789, date='02 April 2009', time='09:43'"
                           ", status=1, comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % (file, SERVER_TMP_DIR+DIRECTORY))

        rc = cpyuda.put_data(instruction.encode())

        self.assertNotEqual(rc.error_code(), 0)

        # Analysed data, no pass
        instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', data_class='analysed data'"
                           ", title='Test #1A', shot=123456, date='02 April 2009', time='09:43'"
                           ", status=1, comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % (file, SERVER_TMP_DIR+DIRECTORY))

        rc = cpyuda.put_data(instruction.encode())

        self.assertNotEqual(rc.error_code(), 0)

        # Analysed data, no status
        instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', data_class='analysed data'"
                           ", title='Test #1A', shot=123456, pass_number=789, date='02 April 2009', time='09:43'"
                           ", comment='Comment for test #1A', code='put_test.py', version=99"
                           ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
                           ", /create)" % (file, SERVER_TMP_DIR+DIRECTORY))

        rc = cpyuda.put_data(instruction.encode())

        self.assertNotEqual(rc.error_code(), 0)


    def _put_variable_fail(self, file_id, group, name, dimensions, value, **kwargs):
        extra = ', '.join('%s=%s' % (k, v) for k, v in kwargs.items())
        if extra:
            extra = ', ' + extra
        instruction = "PUTDATA::variable(fileid=%d, group='%s', name='%s', dimensions='%s', debug=0, verbose=1%s)"\
                      % (file_id, group, name, dimensions, extra)
        rc = cpyuda.put_data(instruction.encode(), value)
        self.assertNotEqual(rc.error_code(), 0)


    def test_create_variable_fail_missing_attributes(self):
        file = 'test24.nc'
        file_id = self.test_creating_file_by_directory_keyword(file=file, close_file=False)

        self._put_dimension(file_id, '/a', 'x', length=3)
        self._put_coordinate(file_id, '/a', 'x', 'm', 'coord label', np.array([1.0,2.0,3.0], dtype=np.float64))

        # No label or title
        self._put_variable_fail(file_id, '/a', 'double', 'x', np.arange(3, dtype=np.float64), units='m')

        # Label and Title
        self._put_variable_fail(file_id, '/a', 'double', 'x', np.arange(3, dtype=np.float64), units='m', label='label', title='title')

        # No units
        self._put_variable_fail(file_id, '/a', 'double', 'x', np.arange(3, dtype=np.float64), label='label')

        # random units
        self._put_variable_fail(file_id, '/a', 'double', 'x', np.arange(3, dtype=np.float64), label='label', units="blah")

        self._close_file(file_id)


    def _put_coordinate_fail(self, file_id, group, name, value, time=False, **kwargs):
        extra = ', '.join('%s=%s' % (k, v) for k, v in kwargs.items())
        if extra:
            extra = ', ' + extra

        instruction = "PUTDATA::coordinate(fileid=%d, group='%s', name='%s', debug=0, verbose=1 %s%s)" \
                      % (file_id, group, name, ", class='time'" if time else '', extra)
        rc = cpyuda.put_data(instruction.encode(), value)
        self.assertNotEqual(rc.error_code(), 0)


    def test_create_coordinate_fail_missing_attributes(self):
        file = 'test25.nc'
        file_id = self.test_creating_file_by_directory_keyword(file=file, close_file=False)

        self._put_dimension(file_id, '/a', 'x', length=3)

        value = np.arange(3, dtype=np.float64)

        # No label or title 
        self._put_coordinate_fail(file_id, '/a', 'x', value, units="m")

        # Label AND title
        self._put_coordinate_fail(file_id, '/a', 'x', value, units="m", label="label", title="title")

        # No units
        self._put_coordinate_fail(file_id, '/a', 'x', value, label="label")

        # Inconsistent count and data array
        start = ';'.join(str(i) for i in [0.0])
        increment = ';'.join(str(i) for i in [1.0])
        count = ';'.join(str(i) for i in [4])

        self._put_coordinate_fail(file_id, '/a', 'x', value, units="m", label="label", starts=start, increments=increment, counts=count)

#        # Inconsistent data array and start, increment 
#        self._put_dimension(file_id, '/a', 'y', length=3)
#        start = ';'.join(str(i) for i in [0.5])
#        increment = ';'.join(str(i) for i in [1.0])
# 
#        self._put_coordinate_fail(file_id, '/a', 'y', value, units="m", label="label", starts=start, increments=increment)

        self._close_file(file_id)
