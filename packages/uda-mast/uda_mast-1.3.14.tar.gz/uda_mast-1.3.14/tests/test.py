from pyuda import cpyuda

DIRECTORY = '/home/lkogan/mastcodes/uda/python/tests'
file = 'test1a.nc'

instruction = ("PUTDATA::open(filename=%s, directory=%s, conventions='Fusion-1.0', data_class='analysed data'"
    ", title='Test #1A', shot=123456, pass_number=789, date='02 April 2009', time='09:43'"
    ", status=1, comment='Comment for test #1A', code='put_test.py', version=99"
    ", xml='<xml>we can record whatever we want as XML</xml>', debug=0, verbose=0"
    ", /create)" % (file, DIRECTORY))

rc = cpyuda.put_data(instruction.encode())
print(rc.error_code())
print(rc.data())

file_id = rc.data()

instruction = "PUTDATA::close(fileid=%d, debug=0, verbose=0)" % file_id

rc = cpyuda.put_data(instruction.encode())
print(rc.error_code())
print(rc.data())
