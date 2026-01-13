import os
import numpy as np

from mast.mast_client import MastClient


FILE = 'test.nc'
DIRECTORY = os.path.abspath(os.path.curdir)
VERBOSE = True
DEBUG = True


def delete_file(file_name):
    try:
        os.remove(file_name)
    except FileNotFoundError:
        pass


client = MastClient(None)

delete_file(os.path.join(DIRECTORY, FILE))

client.put(FILE, directory=DIRECTORY, step_id='create', title='Test #21', data_class ='raw data',
           conventions='Fusion-1.0', debug=DEBUG, verbose=VERBOSE, shot=12345)

assert(client.put_file_id >= 0)

# Put dimensions and coordinates

client.put(1, step_id='dimension', group='/a', name='scalar', debug=DEBUG, verbose=VERBOSE)
client.put(4, step_id='dimension', group='/a', name='x', debug=DEBUG, verbose=VERBOSE)
client.put(2, step_id='dimension', group='/a', name='y', debug=DEBUG, verbose=VERBOSE)
client.put(unlimited=True, step_id='dimension', group='/a', name='time', debug=DEBUG, verbose=VERBOSE)

client.put([1, 2, 3, 4], step_id='coordinate', group='/a', name='x',label="test coord", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put([1.0, 2.0],      step_id='coordinate', group='/a', name='y',label="test coord", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put([0.0, 0.1, 0.2, 0.3, 0.4, 0.5], step_id='coordinate', group='/a', name='time', coord_class='time',label="test coord", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)

# Put devices

client.put('abc123', step_id='device', serial="abc321", type="def456", id='identity #1', resolution=16,
           range=[100.0, 200], channels=32, debug=DEBUG, verbose=VERBOSE)

# Put scalar variables

client.put(np.float32(3), step_id='variable', group='/a', name='float_scalar', dimensions='scalar',
           scale=10.0, offset=-1.0, units='m.A N*s-kg', label='test label', comment='test comment', device='abc123',
           channel=1, debug=DEBUG, verbose=VERBOSE, notstrict=True, compression=1)

client.put(np.float64(3),      step_id='variable', group='/a', name='double_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.int8(3),         step_id='variable', group='/a', name='byte_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.int16(3),        step_id='variable', group='/a', name='short_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.int32(3),        step_id='variable', group='/a', name='int32_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.int64(3),        step_id='variable', group='/a', name='int64_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.uint16(3),       step_id='variable', group='/a', name='ushort_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.uint32(3),       step_id='variable', group='/a', name='ulong_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.uint64(3),       step_id='variable', group='/a', name='ulong64_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.complex64(3 + 1j),  step_id='variable', group='/a', name='complex_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.complex128(3 + 1j), step_id='variable', group='/a', name='dcomplex_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put("scalarstring", step_id='variable', group='/a', name='string_scalar', dimensions='scalar', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(1, step_id='variable', name='int_non_np', group='/a', dimensions='scalar', units='N/A', label='version_fibre', comment='test')

# # Put 1D variables

client.put(np.arange(4, dtype=np.float32), step_id='variable', group='/a', name='float_1d', dimensions='x',
           scale=10.0, offset=-1.0, units='m.A N*s-kg', label='test label', comment='test comment', device='abc123',
           channel=1, debug=DEBUG, verbose=VERBOSE, notstrict=True, compression=1)

client.put(np.arange(4, dtype=np.float64),      step_id='variable', group='/a', name='double_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.arange(4, dtype=np.int8),         step_id='variable', group='/a', name='byte_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.arange(4, dtype=np.int16),        step_id='variable', group='/a', name='short_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.arange(4, dtype=np.int32),        step_id='variable', group='/a', name='int32_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.arange(4, dtype=np.int64),        step_id='variable', group='/a', name='int64_1d_error', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.arange(4, dtype=np.int64),        step_id='variable', group='/a', name='int64_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, errors='int64_1d_error', compression=1)
client.put(np.arange(4, dtype=np.uint16),       step_id='variable', group='/a', name='ushort_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.arange(4, dtype=np.uint32),       step_id='variable', group='/a', name='ulong_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.arange(4, dtype=np.uint64),       step_id='variable', group='/a', name='ulong64_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.arange(4, dtype=np.complex64),    step_id='variable', group='/a', name='complex_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.arange(4, dtype=np.complex128),   step_id='variable', group='/a', name='dcomplex_1d', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(["a", "string", "array", " here is "], step_id='variable', group='/a', name='string_array', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put([1.3, 1.5, 1.7, 1.8], step_id='variable', group='/a', name='float_1d_from_list', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)

fltarr_1d = np.arange(4, dtype=np.float32) * 0.3e-7
scale, offset = client.calculate_packing_factors(np.min(fltarr_1d), np.max(fltarr_1d), 16)
client.put(fltarr_1d, step_id='variable', group='/a', name='packtest_float', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, 
           packdata=16, offset=offset, scale=scale)

dblarr_1d = np.arange(4, dtype=np.float64) * 1.2e-13
scale, offset = client.calculate_packing_factors(np.min(dblarr_1d), np.max(dblarr_1d), 16)
client.put(dblarr_1d, step_id='variable', group='/a', name='packtest_double', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, 
           packdata=16, offset=offset, scale=scale)

# 
fltarr8_1d = np.arange(4, dtype=np.float32) * 0.78e-7
scale, offset = client.calculate_packing_factors(np.min(fltarr8_1d), np.max(fltarr8_1d), 8)
client.put(fltarr8_1d, step_id='variable', group='/a', name='packtest8_float', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, 
           packdata=16, offset=offset, scale=scale)

dblarr8_1d = np.arange(4, dtype=np.float64) * 1.8e-13
scale, offset = client.calculate_packing_factors(np.min(dblarr8_1d), np.max(dblarr8_1d), 8)
client.put(dblarr8_1d, step_id='variable', group='/a', name='packtest8_double', dimensions='x', label="test", units="m", debug=DEBUG, verbose=VERBOSE, 
           packdata=16, offset=offset, scale=scale)

# Put 3D variables

client.put(np.ones((4, 2, 6), dtype=np.float32), step_id='variable', group='/a', name='float_3d', dimensions=['x', 'y', 'time'],
           scale=10.0, offset=-1.0, units='m.A N*s-kg', label='test label', comment='test comment', device='abc123', range=[0.0, 3.0],
           channel=1, debug=DEBUG, verbose=VERBOSE, notstrict=True, compression=1)

client.put(np.ones((4, 2, 6), dtype=np.float64),      step_id='variable', group='/a', name='double_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.ones((4, 2, 6), dtype=np.int8),         step_id='variable', group='/a', name='byte_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.ones((4, 2, 6), dtype=np.int16),        step_id='variable', group='/a', name='short_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.ones((4, 2, 6), dtype=np.int32),        step_id='variable', group='/a', name='int32_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.ones((4, 2, 6), dtype=np.int64),        step_id='variable', group='/a', name='int64_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.ones((4, 2, 6), dtype=np.uint16),       step_id='variable', group='/a', name='ushort_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.ones((4, 2, 6), dtype=np.uint32),       step_id='variable', group='/a', name='ulong_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.ones((4, 2, 6), dtype=np.uint64),       step_id='variable', group='/a', name='ulong64_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.ones((4, 2, 6), dtype=np.complex64),    step_id='variable', group='/a', name='complex_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)
client.put(np.ones((4, 2, 6), dtype=np.complex128),   step_id='variable', group='/a', name='dcomplex_3d', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, compression=1)

fltarr_3d = np.arange(4*2*6, dtype=np.float32).reshape((4,2,6)) * 0.3e-7
scale, offset = client.calculate_packing_factors(np.min(fltarr_3d), np.max(fltarr_3d), 16)
client.put(fltarr_3d, step_id='variable', group='/a', name='packtest3d_float', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, 
           packdata=16, offset=offset, scale=scale)

dblarr_3d = np.arange(4*2*6, dtype=np.float64).reshape((4,2,6)) * 12.9e5
scale, offset = client.calculate_packing_factors(np.min(dblarr_3d), np.max(dblarr_3d), 16)
client.put(dblarr_3d, step_id='variable', group='/a', name='packtest3d_double', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, 
           packdata=16, offset=offset, scale=scale)

fltarr8_3d = np.arange(4*2*6, dtype=np.float32).reshape((4,2,6)) * 0.6e-7
scale, offset = client.calculate_packing_factors(np.min(fltarr8_3d), np.max(fltarr8_3d), 8)
client.put(fltarr8_3d, step_id='variable', group='/a', name='packtest3d8_float', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, 
           packdata=16, offset=offset, scale=scale)

dblarr8_3d = np.arange(4*2*6, dtype=np.float64).reshape((4,2,6)) * 12.9e34
scale, offset = client.calculate_packing_factors(np.min(dblarr8_3d), np.max(dblarr8_3d), 8)
client.put(dblarr8_3d, step_id='variable', group='/a', name='packtest3d8_double', dimensions=['x', 'y', 'time'], label="test", units="m", debug=DEBUG, verbose=VERBOSE, 
           packdata=16, offset=offset, scale=scale)

# Put attributes at various different levels

client.put('Notes at global attribute level', step_id='attribute', group='/', name='notes')
client.put('Notes on group a', step_id='attribute', group='/a', name='notes')
client.put('Notes on variable /a/double_scalar', step_id='attribute', group='/a', varname='double_scalar', name='notes')
client.put(1, step_id='attribute', group='/a', name='scalar_int_attribute')
client.put(1.0, step_id='attribute', group='/a', name='scalar_double_attribute')
client.put([1, 2, 3], step_id='attribute', group='/a', name='array_int_attribute')
client.put([1.0, 2.0, 3.0], step_id='attribute', group='/a', name='array_double_attribute')

#client.put(np.int32(2), step_id='attribute', group='/', name='status')

client.put(step_id='close', status=2, debug=DEBUG, verbose=VERBOSE)

# Reopen for update
client.put(FILE, directory=DIRECTORY, step_id='update', title='Test #21 Updated', data_class ='raw data',
           conventions='Fusion-1.0', debug=DEBUG, verbose=VERBOSE, shot=12345)

client.put(step_id='close', file_id=client.put_file_id, debug=DEBUG, verbose=VERBOSE)

