import pytest
import pyuda
from mast.mast_client import MastClient

class TestUDAPutGet:
    get_client = pyuda.Client()
    put_client = MastClient(None)

    def test_put_get_fails(self):
        shotnum = 40315

        self.put_client.put('test_put_get.nc', directory='./',  step_id='create',
                            conventions='Fusion-1.1', shot=shotnum,
                            data_class='analysed data', title='Test',
                            pass_number=0, status=1,
                            verbose=True, debug=True)
        
        try:
            xma = self.get_client.get('i_dont_exist', shotnum)
        except pyuda.UDAException:
            pass
    
        self.put_client.put(step_id='close')

        
