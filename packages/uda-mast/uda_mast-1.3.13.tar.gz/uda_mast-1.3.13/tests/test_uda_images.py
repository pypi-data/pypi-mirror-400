import pyuda

class TestUDAImages():
    client = pyuda.Client()

    def test_get_ipx_black_white(self):
        rir = self.client.get_images('rir', 29976)

        assert len(rir.frames) > 0

        assert hasattr(rir.frames[0], 'k')

        assert (rir.frames[0].k.shape[0] == rir.height and rir.frames[0].k.shape[1] == rir.width)


    def test_get_ipx_color(self):
        rco = self.client.get_images('rco', 29976)

        assert len(rco.frames) > 0

        assert (hasattr(rco.frames[0], 'r')
                and hasattr(rco.frames[0], 'g')
                and hasattr(rco.frames[0], 'b')
                and hasattr(rco.frames[0], 'raw'))

        assert (rco.frames[0].r.shape[0] == rco.height and rco.frames[0].r.shape[1] == rco.width
                and rco.frames[0].g.shape[0] == rco.height and rco.frames[0].g.shape[1] == rco.width
                and rco.frames[0].b.shape[0] == rco.height and rco.frames[0].b.shape[1] == rco.width
                and rco.frames[0].raw.shape[0] == rco.height and rco.frames[0].raw.shape[1] == rco.width)

    def test_get_ipx_frame_range(self):
        first_frame = 100
        last_frame = 200

        rir = self.client.get_images('rir', 29976, first_frame=first_frame, last_frame=last_frame)

        assert len(rir.frames) == (last_frame - first_frame + 1)

    def test_get_ipx_single_frame(self):
        rir = self.client.get_images('rir', 29976, frame_number=100)

        assert len(rir.frames) == 1

    def test_get_ipx_frame_stride(self):
        rir = self.client.get_images('rir', 29976, stride=10)

        assert len(rir.frames) == 259

    def test_get_rcc(self):
        rcc = self.client.get_images('rcc', 29795)

        assert len(rcc.frames) > 0

        assert hasattr(rcc.frames[0], 'k')

        assert (rcc.frames[0].k.shape[0] == rcc.height and rcc.frames[0].k.shape[1] == rcc.width)

    def test_get_rcc_frame_range(self):
        first_frame = 50
        last_frame = 100

        rcc = self.client.get_images('rcc', 29976, first_frame=first_frame, last_frame=last_frame)

        assert len(rcc.frames) == (last_frame - first_frame + 1)

    def test_get_rcc_single_frame(self):
        rcc = self.client.get_images('rcc', 29976, frame_number=100)

        assert len(rcc.frames) == 1

    def test_get_rcc_frame_stride(self):
        rcc = self.client.get_images('rcc', 29976, stride=10)

        assert len(rcc.frames) == 13

    
