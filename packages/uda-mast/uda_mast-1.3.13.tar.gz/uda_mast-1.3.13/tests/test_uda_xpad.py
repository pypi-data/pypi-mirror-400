import pyuda

class TestUDAXpad():
    client = pyuda.Client()

    def test_get_tree(self):
        tagdata = self.client.get("XPADTREE::gettree(treename=Diagnostics / Techniques)", "")
        
        assert (hasattr(tagdata, 'parent_tag_id')
                and hasattr(tagdata, 'tag_id')
                and hasattr(tagdata, 'tag_id_max')
                and hasattr(tagdata, 'tag_name'))

        assert len(tagdata.tag_id) > 0

    def test_get_signal_tag_mapping(self):
        signal_tags = self.client.get("XPADTREE::getsignaltags(treename=Diagnostics / Techniques)", "")

        assert (hasattr(signal_tags, 'signal_id')
                and hasattr(signal_tags, 'tag_id'))

        assert len(signal_tags.tag_id) > 0

    def test_get_xpad_signals(self):
        sigdata_a_mast = self.client.get('XPADTREE::getsignals(signaltype=A, device=mast)', '')
        assert len(sigdata_a_mast.signal_alias) > 0

        sigdata_r_mastu = self.client.get('XPADTREE::getsignals(signaltype=R, device=mastu)', '')
        assert len(sigdata_r_mastu.signal_alias) > 0

