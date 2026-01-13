import pytest
import pyuda
import numpy as np

class TestUDASignals:
    client = pyuda.Client()

    def test_ida_signal(self):
        signal = self.client.get('amc_plasma current', 30420)

        assert signal.data is not None


    def test_nc_signal(self):
        signal = self.client.get('/XMA/LV/CC03', 29385)

        assert signal.data is not None

    def test_xdc_signal(self):
        signal = self.client.get('/xdc/ai/cpu1/b_c_p54', 40240)
        
        assert signal.data is not None


    def test_plugin_signal(self):
        signal = self.client.get('ANB_SW_FULL_POWER', 29385)

        assert signal.data is not None

    def test_signal_mapping(self):
        signal = self.client.get('XMA_LVCC03', 29385)

        assert signal.data is not None


    def test_meta_xml(self):
        signal = self.client.get('AMC_ERROR FIELD/B', 12272)
        
        assert signal.time.data[0] == pytest.approx(-0.1498)


    def test_composite_signal(self):
        signal = self.client.get('THOMSON/YAG/NE', 13002)

        assert signal.data is not None


    def test_meta_property(self):
        self.client.set_property(pyuda.Properties.META, True)
        signal = self.client.get('amc_plasma current', 30420)

        assert hasattr(signal, 'meta')

        self.client.set_property(pyuda.Properties.META, False)



    def test_get_mast_data_signal(self):
        signal = self.client.get('amc_plasma current', '$MAST_DATA/30420/LATEST/amc0304.20')

        assert signal.data is not None

    
    def test_server_exception(self):
        with pytest.raises(pyuda.ServerException):
            signal = self.client.get('i_dont_exist', 30420)
        
        
    def test_time_ordering(self):
        # Default for ayc_te is time first
        signal = self.client.get('ayc_te', 30420)    
        assert (signal.time_index == 0)
        assert (np.allclose(signal.time.data, signal.dims[0].data))
        assert (signal.data.shape[0] == signal.time.data.shape[0])

        # Reverse dims
        signal.reverse_dimension_order()
        assert (signal.time_index == 1)
        assert (np.allclose(signal.time.data, signal.dims[1].data))
        assert (signal.data.shape[1] == signal.time.data.shape[0])

        # Set time first
        signal.set_time_first()
        assert (signal.time_index == 0)
        assert (np.allclose(signal.time.data, signal.dims[0].data))
        assert (signal.data.shape[0] == signal.time.data.shape[0])

        # Set time last
        signal.set_time_last()
        assert (signal.time_index == 1)
        assert (np.allclose(signal.time.data, signal.dims[1].data))
        assert (signal.data.shape[1] == signal.time.data.shape[0])

        # Check when requesting via time_first, time_last keywords
        signal = self.client.get('ayc_te', 30420, time_first=True)    
        assert (signal.time_index == 0)
        assert (np.allclose(signal.time.data, signal.dims[0].data))
        assert (signal.data.shape[0] == signal.time.data.shape[0])

        signal = self.client.get('ayc_te', 30420, time_last=True)    
        assert (signal.time_index == 1)
        assert (np.allclose(signal.time.data, signal.dims[1].data))
        assert (signal.data.shape[1] == signal.time.data.shape[0])

    def test_uda_pass(self):
        uda_latest = self.client.get('ada_dalpha peak radius', 23702)
        uda_first = self.client.get('ada_dalpha peak radius', '23702/0')

        assert not (np.allclose(uda_latest.data, uda_first.data))

    def test_uda_batch(self):
        shot = 44550    
        sig_list = ['/AMC/PLASMA_CURRENT', '/AMC/ROGEXT/P1']
        sigs_test = self.client.get_batch(sig_list, shot)
        has_data = [True for d in sigs_test if d.data is not None] 
        assert not (False in has_data)

