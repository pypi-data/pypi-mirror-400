import mast.geom as mastgeom
import pyuda
import pytest
import numpy as np
from collections import namedtuple

class CylindricalCoordinate():
    def __init__(self, r, z, phi):
        self.r = r
        self.z = z
        self.phi = phi

class CartesianCoordinate():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class TestUDAGeometry():
    client = pyuda.Client()
    test_shot = 50000

    def check_cartesian_transform(self, cylindrical_coord, cartesian_coord, 
                                  rel=1e-6, 
                                  x_attr='x', y_attr='y', z_attr='z',
                                  r_attr='r', phi_attr='phi'):
        assert (hasattr(cartesian_coord, x_attr) and hasattr(cartesian_coord, y_attr) and hasattr(cartesian_coord, z_attr))
        assert (hasattr(cylindrical_coord, r_attr) and hasattr(cylindrical_coord, z_attr) and hasattr(cylindrical_coord, phi_attr))

        if r_attr == 'r' and phi_attr == 'phi' and z_attr == 'z': 
            x, y, z = mastgeom.geometryUtils.cylindrical_cartesian(cylindrical_coord, phi_degrees=True)
            assert (cartesian_coord.x == pytest.approx(x, rel=rel) and cartesian_coord.y == pytest.approx(y, rel=rel) and cartesian_coord.z == pytest.approx(z, rel=rel))
        else:
            Point3DCyl = namedtuple('Point3DCyl', ['r', 'z', 'phi'])
            x, y, z = mastgeom.geometryUtils.cylindrical_cartesian(Point3DCyl(r=getattr(cylindrical_coord, r_attr), 
                                                                              z=getattr(cylindrical_coord, z_attr), 
                                                                              phi=getattr(cylindrical_coord, phi_attr)), phi_degrees=True)
            assert (getattr(cartesian_coord, x_attr) == pytest.approx(x, rel=rel) 
                    and getattr(cartesian_coord, y_attr) == pytest.approx(y, rel=rel) 
                    and getattr(cartesian_coord, z_attr) == pytest.approx(z, rel=rel))


    def test_get_pfcoil(self):
        pfcoil = self.client.geometry('/magnetics/pfcoil', self.test_shot)

        assert (hasattr(pfcoil.data["p4_lower/data/geom_elements"], 'centreR')
                and hasattr(pfcoil.data["p4_lower/data/geom_elements"], 'centreZ')
                and hasattr(pfcoil.data["p4_lower/data/geom_elements"], 'dR')
                and hasattr(pfcoil.data["p4_lower/data/geom_elements"], 'dZ'))

        assert isinstance(pfcoil, mastgeom.geomEfitElements.GeomEfitElements)
        

    def test_get_pickup(self):
        pickup = self.client.geometry('/magnetics/pickup', self.test_shot)
        
        assert (hasattr(pickup.data['centrecolumn/t2/b_c2_p54/data/coordinate'], 'r') 
                and hasattr(pickup.data['centrecolumn/t2/b_c2_p54/data/coordinate'], 'z')
                and hasattr(pickup.data['centrecolumn/t2/b_c2_p54/data/coordinate'], 'phi'))

        assert isinstance(pickup, mastgeom.geomPickup.GeomPickup)


    def test_get_pickup_element(self):
        pickup = self.client.geometry('/magnetics/pickup/centrecolumn/t2/b_c2_p54', self.test_shot)
        
        assert (hasattr(pickup.data['coordinate'], 'r') 
                and hasattr(pickup.data['coordinate'], 'z')
                and hasattr(pickup.data['coordinate'], 'phi'))

        assert isinstance(pickup, mastgeom.geomPickup.GeomPickup)


    def test_get_mirnov(self):
        mirnov = self.client.geometry('/magnetics/mirnov', self.test_shot)
        
        assert (hasattr(mirnov.data['centrecolumn/m_c_t09/data/coordinate'], 'r') 
                and hasattr(mirnov.data['centrecolumn/m_c_t09/data/coordinate'], 'z')
                and hasattr(mirnov.data['centrecolumn/m_c_t09/data/coordinate'], 'phi'))

        assert isinstance(mirnov, mastgeom.geomPickup.GeomPickup)


    def test_get_fluxloop(self):
        fluxloop = self.client.geometry('/magnetics/fluxloops', self.test_shot)
        
        assert (hasattr(fluxloop.data['centrecolumn/f_c_a12/data/coordinate'], 'r') 
                and hasattr(fluxloop.data['centrecolumn/f_c_a12/data/coordinate'], 'z'))

        assert isinstance(fluxloop, mastgeom.geomFluxloops.GeomFluxloops)


    def test_get_passive(self):
        passive = self.client.geometry('/passive/efit', self.test_shot)
        
        assert (hasattr(passive.data['centrecolumn/data'], 'centreR') 
                and hasattr(passive.data['centrecolumn/data'], 'centreZ')
                and hasattr(passive.data['centrecolumn/data'], 'dR')
                and hasattr(passive.data['centrecolumn/data'], 'dZ')
                and hasattr(passive.data['centrecolumn/data'], 'shapeAngle1')
                and hasattr(passive.data['centrecolumn/data'], 'shapeAngle2'))

        assert isinstance(passive, mastgeom.geomEfitElements.GeomEfitElements)


    def test_get_limiter(self):
        limiter = self.client.geometry('/limiter/efit', self.test_shot)
        
        assert (hasattr(limiter.data, 'R') 
                and hasattr(limiter.data, 'Z'))

        assert isinstance(limiter, mastgeom.geomEfitLimiter.GeomEfitLimiter)


    def test_get_rogowskis(self):
        rogowskis = self.client.geometry('/magnetics/rogowskis', self.test_shot)
        
        assert (hasattr(rogowskis.data['pfcoils/r_dpu_2/data'], 'contains')
                and hasattr(rogowskis.data["ip/r_a2_2/data/path_seg1"], 'R')
                and hasattr(rogowskis.data["ip/r_a2_2/data/path_seg1"], 'Z'))

        assert isinstance(rogowskis, mastgeom.geomRog.GeomRog)


    def test_get_halo(self):
        halo = self.client.geometry('/magnetics/halo', self.test_shot)
        
        assert (hasattr(halo.data['colosseum/upper/h_cu_01/data/geometry'], 'r')
                and hasattr(halo.data['colosseum/upper/h_cu_01/data/geometry'], 'z')
                and hasattr(halo.data['colosseum/upper/h_cu_01/data/geometry'], 'phiStart')
                and hasattr(halo.data['colosseum/upper/h_cu_01/data/geometry'], 'phiEnd'))

        assert isinstance(halo, mastgeom.geomHaloSaddle.GeomHaloSaddle)


    def test_get_saddle(self):
        saddle = self.client.geometry('/magnetics/saddlecoils', self.test_shot)
        
        assert (hasattr(saddle.data['centrecolumn/upper/s_ccu_210a/data/geometry'], 'widthAng')
                and hasattr(saddle.data['centrecolumn/upper/s_ccu_210a/data/geometry'], 'cornerRadius')
                and hasattr(saddle.data['centrecolumn/upper/s_ccu_210a/data/geometry'], 'area')
                and hasattr(saddle.data['centrecolumn/upper/s_ccu_210a/data/geometry'], 'height'))

        assert isinstance(saddle, mastgeom.geomHaloSaddle.GeomHaloSaddle)


    def test_get_bolo(self):
        bolo = self.client.geometry('/bolo', self.test_shot)
        
        assert (hasattr(bolo.data["sxdl/slits/data"][0]['centre_point'], 'r')
                and hasattr(bolo.data["sxdl/slits/data"][0]['centre_point'], 'z')
                and hasattr(bolo.data["sxdl/slits/data"][0]['centre_point'], 'phi'))

        assert isinstance(bolo, mastgeom.geomBolo.GeomBolo)

    def test_get_langmuir_probes(self):
        lp = self.client.geometry('/langmuirprobes', self.test_shot)
        
        assert (hasattr(lp.data["4LC17/data/coordinate"], 'r')
                and hasattr(lp.data["4LC17/data/coordinate"], 'z')
                and hasattr(lp.data["4LC17/data/coordinate"], 'phi'))

        assert isinstance(lp, mastgeom.geomLangmuir.GeomLangmuir)

        # Test convert to s-coord
        lp.convert_r_z_to_s()

        assert (hasattr(lp.data["4LC17/data/coordinate"], 's'))

    def test_get_elm(self):
        elm = self.client.geometry('/magnetics/elmcoils', self.test_shot)
        
        assert (hasattr(elm.data['lower/elm_s12l/data/geometry'], 'turns_r')
                and hasattr(elm.data['lower/elm_s12l/data/geometry'], 'turns_phi')
                and hasattr(elm.data['lower/elm_s12l/data/geometry'], 'turns_z'))

    def test_get_old_config_version(self):
        mirnov = self.client.geometry('/magnetics/mirnov', self.test_shot)
        mirnov_old = self.client.geometry('/magnetics/mirnov', self.test_shot, version_config=0.2)

        assert mirnov.data['centrecolumn/m_c_t09/data'].version != mirnov_old.data['centrecolumn/m_c_t09/data'].version

        assert mirnov_old.data['centrecolumn/m_c_t09/data'].version == '0.2'

    def test_get_old_cal_version(self):
        lp = self.client.geometry('/langmuirprobes', self.test_shot)
        lp_old = self.client.geometry('/langmuirprobes', self.test_shot, version_config=0.1, version_cal=0.1)

        assert lp.data['4LC14/data'].version != lp_old.data['4LC14/data'].version

        assert lp_old.data['4LC14/data'].version == 0.1


    def test_calibration(self):
        # Array calibration
        pfcoil = self.client.geometry('/magnetics/pfcoil', self.test_shot)
        pfcoil_nocal = self.client.geometry('/magnetics/pfcoil', self.test_shot, no_cal=True)

        assert (pfcoil.data["p4_upper/data/geom_elements"].centreZ != pytest.approx(pfcoil_nocal.data["p4_upper/data/geom_elements"].centreZ))

        # Scalar calibration
        pickup = self.client.geometry('/magnetics/pickup', self.test_shot)
        pickup_nocal = self.client.geometry('/magnetics/pickup', self.test_shot, no_cal=True)

        assert (pickup.data["centrecolumn/t1/b_c1_p01/data/coordinate"].z != pytest.approx(pickup_nocal.data["centrecolumn/t1/b_c1_p01/data/coordinate"].z))

        # Array of variables calibration
        bolo = self.client.geometry('/bolo', self.test_shot)
        bolo_nocal = self.client.geometry('/bolo', self.test_shot, no_cal=True)

        all_centre_z = [data['centre_point'].z for data in bolo.data["sxdl/slits/data"]]
        all_centre_z_nocal = [data['centre_point'].z for data in bolo_nocal.data["sxdl/slits/data"]]

        assert (all_centre_z != pytest.approx(all_centre_z_nocal))
    
        # Array calibration on element
        pfcoil = self.client.geometry('/magnetics/pfcoil/p4_upper', self.test_shot)
        pfcoil_nocal = self.client.geometry('/magnetics/pfcoil/p4_upper', self.test_shot, no_cal=True)

        assert (pfcoil.data["geom_elements"].centreZ != pytest.approx(pfcoil_nocal.data["geom_elements"].centreZ))

        # Scalar calibration on element
        pickup = self.client.geometry('/magnetics/pickup/centrecolumn/t1/b_c1_p01', self.test_shot)
        pickup_nocal = self.client.geometry('/magnetics/pickup/centrecolumn/t1/b_c1_p01', self.test_shot, no_cal=True)

        assert (pickup.data["coordinate"].z != pytest.approx(pickup_nocal.data["coordinate"].z))

        # Array of variables calibration on element
        #  bolo = self.client.geometry('/bolo/sxdl/slits', self.test_shot)
        #  bolo_nocal = self.client.geometry('/bolo/sxdl/slits', self.test_shot, no_cal=True)
        #
        # all_centre_z = [data['centre_point'].z for data in bolo.data]
        # all_centre_z_nocal = [data['centre_point'].z for data in bolo_nocal.data]
        #assert (all_centre_z != pytest.approx(all_centre_z_nocal))


    def test_cylindrical_cartesian(self):

        coordinate = CylindricalCoordinate(1.0, 1.0, 0.0)
        x,y,z = mastgeom.geometryUtils.cylindrical_cartesian(coordinate, phi_degrees=True)
        assert (x == pytest.approx(1.0) and y == pytest.approx(0.0) and z == pytest.approx(1.0))

        coordinate = CylindricalCoordinate(1.0, 1.0, 90.0)
        x,y,z = mastgeom.geometryUtils.cylindrical_cartesian(coordinate, phi_degrees=True)
        assert (x == pytest.approx(0.0) and y == pytest.approx(1.0) and z == pytest.approx(1.0))

        coordinate = CylindricalCoordinate(1.0, 1.0, 180.0)
        x,y,z = mastgeom.geometryUtils.cylindrical_cartesian(coordinate, phi_degrees=True)
        assert (x == pytest.approx(-1.0) and y == pytest.approx(0.0) and z == pytest.approx(1.0))

        coordinate = CylindricalCoordinate(1.0, 1.0, 270.0)
        x,y,z = mastgeom.geometryUtils.cylindrical_cartesian(coordinate, phi_degrees=True)
        assert (x == pytest.approx(0.0) and y == pytest.approx(-1.0) and z == pytest.approx(1.0))

        coordinate = CylindricalCoordinate(1.0, 1.0, -90.0)
        x,y,z = mastgeom.geometryUtils.cylindrical_cartesian(coordinate, phi_degrees=True)
        assert (x == pytest.approx(0.0) and y == pytest.approx(-1.0) and z == pytest.approx(1.0))


    def test_cartesian_cylindrical(self):

        coordinate = CartesianCoordinate(1.0, 0.0, 1.0)
        r,z,phi = mastgeom.geometryUtils.cartesian_cylindrical(coordinate, phi_degrees=True)
        assert ( r == pytest.approx(1.0) and z == pytest.approx(1.0) and phi == pytest.approx(0.0) )

        coordinate = CartesianCoordinate(0.0, 1.0, 1.0)
        r,z,phi = mastgeom.geometryUtils.cartesian_cylindrical(coordinate, phi_degrees=True)
        assert ( r == pytest.approx(1.0) and z == pytest.approx(1.0) and phi == pytest.approx(90.0) )

        coordinate = CartesianCoordinate(-1.0, 0.0, 1.0)
        r,z,phi = mastgeom.geometryUtils.cartesian_cylindrical(coordinate, phi_degrees=True)
        assert ( r == pytest.approx(1.0) and z == pytest.approx(1.0) and phi == pytest.approx(180.0) )

        coordinate = CartesianCoordinate(0.0, -1.0, 1.0)
        r,z,phi = mastgeom.geometryUtils.cartesian_cylindrical(coordinate, phi_degrees=True)
        assert ( r == pytest.approx(1.0) and z == pytest.approx(1.0) and phi == pytest.approx(270.0) )

    
    def test_unit_vector_to_br_bz_bphi(self):

        orientation = {'unit_vector': CylindricalCoordinate(0.707106, 0.707106, 0.0)}
        br_frac, bz_frac, bphi_frac = mastgeom.geometryUtils.vector_to_bR_bZ_bPhi(orientation)
        assert (br_frac == pytest.approx(0.5) and bz_frac == pytest.approx(0.5) and bphi_frac == pytest.approx(0.0) )

        orientation = {'unit_vector': CylindricalCoordinate(0.0, 0.707106, 0.707106)}
        br_frac, bz_frac, bphi_frac = mastgeom.geometryUtils.vector_to_bR_bZ_bPhi(orientation)
        assert ( br_frac == pytest.approx(0.0) and bz_frac == pytest.approx(0.5) and bphi_frac == pytest.approx(0.5) )

        orientation = {'unit_vector': CylindricalCoordinate(0.0, 0.707106, -0.707106)}
        br_frac, bz_frac, bphi_frac = mastgeom.geometryUtils.vector_to_bR_bZ_bPhi(orientation)
        assert ( br_frac == pytest.approx(0.0) and bz_frac == pytest.approx(0.5) and bphi_frac == pytest.approx(-0.5) )


    def test_length_poloidal_projection(self):
        length = 1.0

        orientation = {'unit_vector': CylindricalCoordinate(np.sqrt(0.5), np.sqrt(0.5), 0.0)}
        pol_length = mastgeom.geometryUtils.length_poloidal_projection(length, orientation)
        assert pol_length == pytest.approx(1.0)

        orientation = {'unit_vector': CylindricalCoordinate(0.0, np.sqrt(0.5), np.sqrt(0.5))}
        pol_length = mastgeom.geometryUtils.length_poloidal_projection(length, orientation)
        assert pol_length == pytest.approx(np.sqrt(0.5))

        orientation = {'unit_vector': CylindricalCoordinate(0.0, np.sqrt(0.5), -np.sqrt(0.5))}
        pol_length = mastgeom.geometryUtils.length_poloidal_projection(length, orientation)
        assert pol_length == pytest.approx(np.sqrt(0.5))

        orientation = {'unit_vector': CylindricalCoordinate(0.0, 0.0, 1.0)}
        pol_length = mastgeom.geometryUtils.length_poloidal_projection(length, orientation)
        assert pol_length == pytest.approx(0.0)

    def test_unit_vector_to_poloidal_angle(self):
        r = 1.0
        z = 0.0
        angle_clockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(r, z, convention="clockwise")
        assert angle_clockwise == pytest.approx(0.0)
        angle_anticlockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(r, z, convention="anticlockwise")
        assert angle_anticlockwise == pytest.approx(0.0)

        r = 0.0
        z = 1.0
        angle_clockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(r, z, convention="clockwise")
        assert angle_clockwise == pytest.approx(270.0)
        angle_anticlockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(r, z, convention="anticlockwise")
        assert angle_anticlockwise == pytest.approx(90.0)
        
        r = -1.0
        z = 0.0
        angle_clockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(r, z, convention="clockwise")
        assert angle_clockwise == pytest.approx(180.0)
        angle_anticlockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(r, z, convention="anticlockwise")
        assert angle_anticlockwise == pytest.approx(180.0)

        r = 0.0
        z = -1.0
        angle_clockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(r, z, convention="clockwise")
        assert angle_clockwise == pytest.approx(90.0)
        angle_anticlockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(r, z, convention="anticlockwise")
        assert angle_anticlockwise == pytest.approx(270.0)



    def test_coordinate_transforms(self):

        # Underlying data is cartesian
        bolo_cart = self.client.geometry('/bolo', self.test_shot, cartesian_coords=True)
        bolo_cyl = self.client.geometry('/bolo', self.test_shot, cylindrical_coords=True)

        self.check_cartesian_transform(bolo_cyl.data['sxdl/slits/data'][0]['centre_point'], bolo_cart.data['sxdl/slits/data'][0]['centre_point'])

        elm_cart = self.client.geometry('/magnetics/elmcoils', self.test_shot, cartesian_coords=True)
        elm_cyl = self.client.geometry('/magnetics/elmcoils', self.test_shot, cylindrical_coords=True)

        self.check_cartesian_transform(elm_cyl.data['lower/elm_s12l/data/geometry'],
                                       elm_cart.data['lower/elm_s12l/data/geometry'],
                                       x_attr='turns_x', y_attr='turns_y', z_attr='turns_z',
                                       r_attr='turns_r', phi_attr='turns_phi')
                                       

        # Underlying data is cylindrical
        pickup_cart = self.client.geometry('/magnetics/pickup', self.test_shot, cartesian_coords=True)
        pickup_cyl = self.client.geometry('/magnetics/pickup', self.test_shot, cylindrical_coords=True)

        self.check_cartesian_transform(pickup_cyl.data['centrecolumn/t2/b_c2_p54/data/coordinate'], pickup_cart.data['centrecolumn/t2/b_c2_p54/data/coordinate'])
        
        halo_cart = self.client.geometry('/magnetics/halo', self.test_shot, cartesian_coords=True)
        halo_cyl = self.client.geometry('/magnetics/halo', self.test_shot, cylindrical_coords=True)

        self.check_cartesian_transform(halo_cyl.data['colosseum/upper/h_cu_01/data/coilPath'], halo_cart.data['colosseum/upper/h_cu_01/data/coilPath'], rel=1e-5)

        saddle_cart = self.client.geometry('/magnetics/saddlecoils', self.test_shot, cartesian_coords=True)
        saddle_cyl = self.client.geometry('/magnetics/saddlecoils', self.test_shot, cylindrical_coords=True)

        self.check_cartesian_transform(saddle_cyl.data['centrecolumn/upper/s_ccu_210a/data/centre'], saddle_cart.data['centrecolumn/upper/s_ccu_210a/data/centre'])

        langmuir_cart = self.client.geometry('/langmuirprobes', self.test_shot, cartesian_coords=True)
        langmuir_cyl = self.client.geometry('/langmuirprobes', self.test_shot, cylindrical_coords=True)

        self.check_cartesian_transform(langmuir_cyl.data['4LC17/data/coordinate'], langmuir_cart.data['4LC17/data/coordinate'])
    
        # Underlying data is cylindrical, no cartesian transform available
        with pytest.raises(NotImplementedError):
            passive = self.client.geometry('/passive/efit', self.test_shot, cartesian_coords=True)

        with pytest.raises(NotImplementedError):
            limiter = self.client.geometry('/limiter/efit', self.test_shot, cartesian_coords=True)

        with pytest.raises(NotImplementedError):
            fluxloops = self.client.geometry('/magnetics/fluxloops', self.test_shot, cartesian_coords=True)

        with pytest.raises(NotImplementedError):
            rogowskis = self.client.geometry('/magnetics/rogowskis', self.test_shot, cartesian_coords=True)


    def test_poloidal_angle(self):
        pickup_unit_vector = self.client.geometry('/magnetics/pickup', self.test_shot)
        assert (hasattr(pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/orientation/unit_vector'], 'r')
                and hasattr(pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/orientation/unit_vector'], 'z')
                and hasattr(pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/orientation/unit_vector'], 'phi')
                and hasattr(pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/geometry'], 'length'))

        pickup_pol_clockwise = self.client.geometry('/magnetics/pickup', self.test_shot, poloidal="clockwise")
        assert (hasattr(pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'poloidal_angle')
                and hasattr(pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'poloidal_convention')
                and hasattr(pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'bRFraction')
                and hasattr(pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'bZFraction')
                and hasattr(pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'bPhiFraction')
                and hasattr(pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/geometry'], 'length_poloidal'))

        pickup_pol_anticlockwise = self.client.geometry('/magnetics/pickup', self.test_shot, poloidal="anticlockwise")
        assert (hasattr(pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'poloidal_angle')
                and hasattr(pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'poloidal_convention')
                and hasattr(pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'bRFraction')
                and hasattr(pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'bZFraction')
                and hasattr(pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'], 'bPhiFraction')
                and hasattr(pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/geometry'], 'length_poloidal'))

        angle_clockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/orientation/unit_vector'].r,
                                                        pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/orientation/unit_vector'].z, 
                                                        convention="clockwise")
        assert angle_clockwise == pytest.approx(pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'].poloidal_angle)

        angle_anticlockwise = mastgeom.geometryUtils.unit_vector_to_poloidal_angle(pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/orientation/unit_vector'].r,
                                                            pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/orientation/unit_vector'].z, 
                                                            convention="anticlockwise")
        assert angle_anticlockwise == pytest.approx(pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'].poloidal_angle)


        br,bz,bphi = mastgeom.geometryUtils.vector_to_bR_bZ_bPhi(pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/orientation'])
        assert (pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'].bRFraction == pytest.approx(br)
                and pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'].bZFraction == pytest.approx(bz)
                and pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'].bPhiFraction == pytest.approx(bphi))

        assert (pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'].bRFraction == pytest.approx(br)
                and pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'].bZFraction == pytest.approx(bz)
                and pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/orientation'].bPhiFraction == pytest.approx(bphi))

        pol_length = mastgeom.geometryUtils.length_poloidal_projection(pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/geometry'].length, pickup_unit_vector.data['centrecolumn/t2/b_c2_p54/data/orientation'])
        assert (pickup_pol_clockwise.data['centrecolumn/t2/b_c2_p54/data/geometry'].length_poloidal == pytest.approx(pol_length))
        assert (pickup_pol_anticlockwise.data['centrecolumn/t2/b_c2_p54/data/geometry'].length_poloidal == pytest.approx(pol_length))
        
    
    def test_convert_vertices(self):
        passive = self.client.geometry('/passive/efit', self.test_shot)
        passive.convert_to_vertices()
        assert hasattr(passive.data['p4_case_upper/data'], 'vertices')

        pfcoils = self.client.geometry('/magnetics/pfcoil', self.test_shot)
        pfcoils.convert_to_vertices()
        assert hasattr(pfcoils.data['p4_upper/data/geom_elements'], 'vertices')

        assert (passive.data['p4_case_lower/data'].vertices.shape[0] == len(passive.data['p4_case_lower/data'].dR)
                and passive.data['p4_case_lower/data'].vertices.shape[1] == 4
                and passive.data['p4_case_lower/data'].vertices.shape[2] == 2)
    
        passive.convert_to_vertices(close_shapes=True)
        assert hasattr(passive.data['p4_case_upper/data'], 'vertices')
        assert (passive.data['p4_case_lower/data'].vertices.shape[0] == len(passive.data['p4_case_lower/data'].dR)
                and passive.data['p4_case_lower/data'].vertices.shape[1] == 5
                and passive.data['p4_case_lower/data'].vertices.shape[2] == 2)


        assert (pfcoils.data['p4_upper/data/geom_elements'].vertices.shape[0] == len(pfcoils.data['p4_upper/data/geom_elements'].dR)
                and pfcoils.data['p4_upper/data/geom_elements'].vertices.shape[1] == 4
                and pfcoils.data['p4_upper/data/geom_elements'].vertices.shape[2] == 2)

        pfcoils.convert_to_vertices(close_shapes=True)
        assert hasattr(pfcoils.data['p4_upper/data/geom_elements'], 'vertices')
        assert (pfcoils.data['p4_upper/data/geom_elements'].vertices.shape[0] == len(pfcoils.data['p4_upper/data/geom_elements'].dR)
                and pfcoils.data['p4_upper/data/geom_elements'].vertices.shape[1] == 5
                and pfcoils.data['p4_upper/data/geom_elements'].vertices.shape[2] == 2)

    def test_list_groups(self):
        groups = self.client.listGeomGroups(shot=self.test_shot)

        assert len(groups.geomgroup) > 0


    def test_list_signals(self):
        all_signals = self.client.listGeomSignals(shot=self.test_shot)

        assert len(all_signals.signal_alias) > 0

        pickup_signals = self.client.listGeomSignals(shot=self.test_shot, group='/magnetics/pickup')

        pickup_named = [s for s in pickup_signals.signal_alias if s.startswith('/magnetics/pickup')]

        assert len(pickup_signals.signal_alias) == len(pickup_named)


    def test_signal_mapping(self):

        # By group
        test_group = self.client.geometry_signal_mapping(shot=44072, geom_group='/magnetics/pickup')

        assert (hasattr(test_group, 'geom_signal_name')
                and hasattr(test_group, 'geom_signal_shortname')
                and hasattr(test_group, 'uda_signal_name')
                and hasattr(test_group, 'uda_signal_status'))

        # By geom signal shortname
        test_geomsignal = self.client.geometry_signal_mapping(shot=44072, geom_signal='b_o1_n08')

        assert len(test_geomsignal.uda_signal_name) == 1

        # By geom signal full name
        test_geomsignal = self.client.geometry_signal_mapping(shot=44072, geom_signal='/magnetics/pickup/outervessel/t1/b_o1_n08')

        assert len(test_geomsignal.uda_signal_name) == 1

        # By uda name 
        test_udasignal = self.client.geometry_signal_mapping(shot=45315, uda_signal='XMC/ACQ216_202/CH05')

        assert len(test_udasignal.geom_signal_name) == 1
