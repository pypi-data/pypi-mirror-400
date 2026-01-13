import unittest
from unittest.mock import MagicMock
import pyuda
from pyuda import cpyuda
import numpy as np


class Result:
    def __init__(self):
        pass

    def data(self):
        return 0

    def error_code(self):
        return 0

put_mock = MagicMock(return_value=Result())
cpyuda.put_data = put_mock

from mast.mast_client import MastClient

DIRECTORY = '/home/lkogan/mastcodes/uda/python/tests'
VERBOSE = True
DEBUG = True


class PutTests(unittest.TestCase):

    def test_creating_client(self):
        client = pyuda.Client()
        mast_client = MastClient(client)
        return mast_client

    def test_create_file(self):
        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        mast_client.put('test.nc', directory=DIRECTORY, step_id='create', title='Test',
                        data_class='raw data', conventions='Fusion-1.0', debug=DEBUG,
                        verbose=VERBOSE, shot=12345)
        instruction = "PUTDATA::open(filename=test.nc, shot=12345, data_class='raw data', conventions='Fusion-1.0', directory='%s', title='Test', debug=1, verbose=1, /create)" % DIRECTORY
        
        put_mock.assert_called_once_with(instruction.encode())

    def test_update_file(self):
        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        mast_client.put('test.nc', directory=DIRECTORY, step_id='update', title='Test',
                        data_class='raw data', conventions='Fusion-1.0', debug=DEBUG,
                        verbose=VERBOSE, shot=12345)
        instruction = "PUTDATA::open(filename=test.nc, shot=12345, data_class='raw data', conventions='Fusion-1.0', directory='%s', title='Test', debug=1, verbose=1, /update)" % DIRECTORY
        put_mock.assert_called_once_with(instruction.encode())

    def test_add_device(self):
        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        mast_client.put('dataq1', file_id=0, step_id='device', serial="abc123", type="def456", id='identity #1',
                        resolution=16, range=[100.0, 200], channels=32, debug=DEBUG, verbose=VERBOSE)
        instruction = b"PUTDATA::device(fileid=0, channels=32, device='dataq1', id='identity #1', range='100.0;200', resolution=16, serial='abc123', type='def456', debug=1, verbose=1)"
        put_mock.assert_called_once_with(instruction)

    def test_add_attribute(self):
        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        mast_client.put(3.1415927, file_id=0, step_id='Attribute', group='/a', name='floatscalar', debug=DEBUG, verbose=VERBOSE)
        instruction = b"PUTDATA::attribute(fileid=0, group='a', name='floatscalar', debug=1, verbose=1)"
        put_mock.assert_called_once_with(instruction, data=3.1415927)

    def test_add_dimension(self):
        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        mast_client.put(1, file_id=0, step_id='dimension', group='/a', name='unit', debug=DEBUG, verbose=VERBOSE)
        instruction = b"PUTDATA::dimension(fileid=0, length=1, group='a', name='unit', debug=1, verbose=1)"
        put_mock.assert_called_once_with(instruction)

    def test_add_unlimited_dimension(self):
        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        mast_client.put(file_id=0, step_id='dimension', group='/a', name='unit', unlimited=True, debug=DEBUG, verbose=VERBOSE)
        instruction = b"PUTDATA::dimension(fileid=0, group='a', name='unit', debug=1, verbose=1, /unlimited)"
        put_mock.assert_called_once_with(instruction)

    def test_add_coordinate(self):
        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float64)
        mast_client.put(data, file_id=0, step_id='coordinate', group='/a', name='y', label='y-label', units='m',
                        debug=DEBUG, verbose=VERBOSE)
        instruction = b"PUTDATA::coordinate(fileid=0, group='a', label='y-label', name='y', units='m', debug=1, verbose=1)"
        put_mock.assert_called_once_with(instruction, data=data)

    def test_add_coordinate_using_start_increment_count(self):
        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        starts      = 0.0
        increments  = 0.5
        counts      = 3
        mast_client.put(starts=starts, increments=increments, counts=counts, file_id=0, step_id='coordinate',
                        group='/a', name='m', debug=DEBUG, verbose=VERBOSE)
        instruction = b"PUTDATA::coordinate(fileid=0, starts=0.0, increments=0.5, counts=3, group='a', name='m', debug=1, verbose=1)"
        put_mock.assert_called_once_with(instruction)

        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        starts      = [0.0, 10.0, 20.0]
        increments  = [0.5, 0.1, 1.0]
        counts      = [3, 5, 2]
        mast_client.put(starts=starts, increments=increments, counts=counts, file_id=0, step_id='coordinate',
                        group='/a', name='m', debug=DEBUG, verbose=VERBOSE)
        instruction = b"PUTDATA::coordinate(fileid=0, starts=0.0;10.0;20.0, increments=0.5;0.1;1.0, counts=3;5;2, group='a', name='m', debug=1, verbose=1)"
        put_mock.assert_called_once_with(instruction)

    def test_add_variable(self):
        put_mock.reset_mock()
        mast_client = self.test_creating_client()
        mast_client.put(2.0, file_id=0, step_id='variable', group='/a', name='double', dimensions='x', label="test",
                        debug=DEBUG, verbose=VERBOSE)
        instruction = b"PUTDATA::variable(fileid=0, dimensions='x', group='a', label='test', name='double', debug=1, verbose=1)"
        put_mock.assert_called_once_with(instruction, data=2.0)

