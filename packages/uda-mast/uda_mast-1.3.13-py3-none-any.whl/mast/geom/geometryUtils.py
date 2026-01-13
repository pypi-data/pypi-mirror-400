import operator
import numpy as np
from shapely.geometry import LineString,Polygon,Point, MultiLineString
import shapely.affinity


"""
Utilities for geometry manipulations, that are useful across geometry manipulation classes.
"""

def unit_vector_to_poloidal_angle(R, Z, convention="anticlockwise"):
    """
    Take a unit vector in cylindrical co-ordinates
    and calculate the "poloidal angle".
    :param R: R element
    :param Z: Z element
    :param convention: clockwise or anticlockwise: direction in which poloidal angle increases from x-axis
    :return: poloidal angle in degrees
    """
    theta = np.arctan2(Z, R) * 180.0 / np.pi

    # Make it go from 0 -> 2pi
    if theta < 0:
        theta = 360 + theta

    if convention == "clockwise" and theta > 0.0:
        theta = 360 - theta

    return theta


def vector_to_bR_bZ_bPhi(orientation):
    """
    Take a unit vector in cylindrical co-ordinates
    and calculate the fraction of the vector
    that is in the R and Z directions.
    :param orientation : orientation element, containing unit vector in direction of measurement
    :return: (bRFraction, bZFraction, bPhiFraction)
    """
    # First, calculate how much is toroidal/poloidal
    norm = (np.fabs(orientation["unit_vector"].phi)
            + np.fabs(orientation["unit_vector"].r)
            + np.fabs(orientation["unit_vector"].z))
    bPhiFraction = orientation["unit_vector"].phi/norm
    bZFraction = orientation["unit_vector"].z/norm
    bRFraction = orientation["unit_vector"].r/norm

    return bRFraction, bZFraction, bPhiFraction


def length_poloidal_projection(length, orientation):
    """
    Using the unit vector describing the orientation
    of the object, calculate the projection of the
    length of the object in the poloidal plane.
    :param length: length of object
    :param orientation: orientation of the object
    :return: projected length
    """
    angle_to_poloidal_plane = np.arcsin(orientation["unit_vector"].phi)
    fraction_poloidal_plane = np.cos(angle_to_poloidal_plane)

    new_length = length*fraction_poloidal_plane

    if np.isclose(new_length, 0.0):
        new_length = 0.0

    return new_length


def cylindrical_cartesian(coordinate, phi_degrees=True):
    """
    Take cylindrical coordinate and translate to cartesian coordinate
    :param coordinate: coordinate node.
    :return: [x,y,z]
    """
    phi = coordinate.phi

    if phi_degrees:
        phi = coordinate.phi * np.pi/180.0

    x = coordinate.r * np.cos(phi)
    y = coordinate.r * np.sin(phi)
    z = coordinate.z

    return [x,y,z]


def cartesian_cylindrical(coodrinate, phi_degrees=False):
    """

    :param coodrinate:
    :return:
    """

    r = np.sqrt(coodrinate.x * coodrinate.x + coodrinate.y * coodrinate.y)
    z = coodrinate.z

    phi = np.arctan2(coodrinate.y,  coodrinate.x)

    if phi_degrees:
        phi = phi * 180.0 / np.pi

    if phi < 0 and phi_degrees:
        phi = 360 + phi
    elif phi < 0 and not phi_degrees:
        phi = 2 * np.pi + phi

    return [r,z,phi]


def project_3dxyz_to_2drz(vec):
    """Project an array (x, y, z) to (r, z). From J. Lovell"""
    return np.asarray([np.hypot(*vec[:2]), vec[2]])


def find_intersection_rz(line_start, line_end, boundary):

    # Line
    try:
        start_3d = np.asarray([line_start.x, line_start.y, line_start.z])
        end_3d = np.asarray([line_end.x, line_end.y, line_end.z])
        start_2d = project_3dxyz_to_2drz(start_3d)
        end_2d = project_3dxyz_to_2drz(end_3d)
    except:
        start_2d = np.asarray([line_start.r, line_start.z])
        end_2d = np.asarray([line_end.r, line_end.z])

    line = LineString([start_2d, end_2d])

    # Boundary
    try:
        coordTuple = list(zip(boundary.R, boundary.Z))
    except AttributeError:
        coordTuple = list(zip(boundary.r, boundary.z))
    polygonBoundary = Polygon(coordTuple)

    # Intersections
    intersectLine = polygonBoundary.intersection(line)

    if isinstance(intersectLine, MultiLineString):
        # Retrieve the longest Linestring, to deal with cases where the
        # shape doubles back on itself
        intersectLine = max(intersectLine.geoms, key=operator.attrgetter('length'))

    intersect_points = []

    try:
        for coord in intersectLine.coords:
            intersect_points.append(coord)
    except NotImplementedError:
        print("Intersection with boundary could not be found")
        pass

    return intersect_points


def find_intersection_xy(line_start, line_end, bound_r_outer, bound_r_inner=None):

    # Line
    try:
        start_2d = np.asarray([line_start.x, line_start.y])
        end_2d = np.asarray([line_end.x, line_end.y])
       # end_2d = np.asarray([line_end.x + (line_end.x - line_start.x) * 100, line_end.y + (line_end.y - line_start.y) * 100])
    except AttributeError:
        start_xyz = cylindrical_cartesian(line_start)
        end_xyz = cylindrical_cartesian(line_end)
        start_2d = np.asarray([start_xyz[0], start_xyz[1]])
        end_2d = np.asarray([end_xyz[0], end_xyz[1]])

    # Polygon to intersect
    circleR = Point(0,0).buffer(1)
    circle_outer = shapely.affinity.scale(circleR, bound_r_outer, bound_r_outer)

    if bound_r_inner is not None:
        # We are looking for intersection with a ring rather than a circle:
        # so make it from the big and little circles
        circle_inner = shapely.affinity.scale(circleR, bound_r_inner, bound_r_inner)
        circle = circle_outer - circle_inner
    else:
        # Just a circle
        circle = circle_outer

    # Get LOS to intersect with
    line = LineString([start_2d, end_2d])
    intersectLine = circle.intersection(line)

    intersect_points_xy = []

    try:
        for coord in intersectLine.coords:
            intersect_points_xy.append(coord)
    except NotImplementedError:
        try:
            firstline = intersectLine.geoms[0]
            for coord in firstline.coords:
                intersect_points_xy.append(coord)
        except NotImplementedError:
            print("Intersection with XY boundary could not be found")

    return intersect_points_xy


def find_intersection_2d(line_start, line_end, boundary, rz=True):

    """
    Find the intersection between a line and boundary in a 2D plane
    This function assumes axi-symmetry for the boundary
    :param line_start: Start of the line, either in 3d line_start.x, line_start.y, line_start.z or 2d line_start.r, line_start.z
    :param line_end: End of the line, either in 3d line_start.x, line_start.y, line_start.z or 2d line_start.r, line_start.z
    :param boundary: Limiting boundary in 2d, R,Z coordinates boundary.r, boundary.z
    :param rz: If set to True, the intersection in R,Z plane is found. If False the intersection in x-y plane is found.
    :return:
    """

    ###################
    # R, Z intersection
    ###################

    # Line
    try:
        start_3d = np.asarray([line_start.x, line_start.y, line_start.z])
        end_3d = np.asarray([line_end.x, line_end.y, line_end.z])
        start_2d = project_3dxyz_to_2drz(start_3d)
        end_2d = project_3dxyz_to_2drz(end_3d)
    except:
        start_2d = np.asarray([line_start.r, line_start.z])
        end_2d = np.asarray([line_end.r, line_end.z])

    line = LineString([start_2d, end_2d])

    # Boundary
    try:
        coordTuple = list(zip(boundary.R, boundary.Z))
    except AttributeError:
        coordTuple = list(zip(boundary.r, boundary.z))
    polygonBoundary = Polygon(coordTuple)

    # Intersections
    intersectLine = polygonBoundary.intersection(line)

    intersect_points = []

    try:
        for coord in intersectLine.coords:
            intersect_points.append(coord)
    except NotImplementedError:
        print("Intersection with boundary could not be found")
        pass

    # If we wanted the intersection in the R-Z plane, this is it
    if rz:
        return intersect_points

    ######################
    # x-y plane intersection
    # This is more complicated since it's really a 3D problem...
    # 1. Work out the radii at which we want to find LOS intersections.
    #    Where the LOS is in the same x-y plane, can just use inner and outer R-values of the limiter at that Z-height
    #
    #    Otherwise, there will be the outboard limiting surface, at the first intersection of the LOS
    #    And there will be the inboard limiting surface, at the second intersection of the LOS
    #    This will need adjusting for cases where the LOS misses the centre column and is not in the same x-y plane.
    #
    # 2. Find intersection of LOS with outer circle - inner circle
    #######################

    if len(intersect_points) == 0 and not np.isclose(line_start.z, line_end.z, atol=0.0005):
        return []

    # Work out the boundary to intersect with
    # We want the outer limiter boundary - inner boundary to give us the 'ring' that excludes the centre column
    if np.isclose(line_start.z, line_end.z, atol=0.0005):
        # If the los is in the same plane, we only need to check the boundary at this height
        # At this z-value find intersect with boundary of horizontal line at z=line_start.z
        line_z = LineString([(0.0, line_end.z), (100.0, line_end.z)])
        intersect = polygonBoundary.intersection(line_z)
        boundR_inner = intersect.coords[0][0]
        boundR_outer = intersect.coords[1][0]
    else:
        # Otherwise, we need to work out where the intersection is in the x-y plane at the appropriate Z-height
        if intersect_points[0][0] < intersect_points[1][0]:
            boundR_outer = intersect_points[1][0]
            boundR_inner = intersect_points[0][0]
        else:
            boundR_outer = intersect_points[0][0]
            boundR_inner = intersect_points[1][0]

    circleR = Point(0,0).buffer(1)
    circle_outer = shapely.affinity.scale(circleR,boundR_outer,boundR_outer)

    if boundR_inner is not None:
        circle_inner = shapely.affinity.scale(circleR,boundR_inner,boundR_inner)
        circle = circle_outer - circle_inner
    else:
        circle = circle_outer

    # Get LOS to intersect with. Extend line_end to make sure it will cover full radius
    try:
        start_2d = np.asarray([line_start.x, line_start.y])
        end_2d = np.asarray([line_end.x + (line_end.x-line_start.x)*100, line_end.y + (line_end.y-line_start.y)*100])
    except:
        start_3d = np.asarray([line_start.r, line_start.z, line_start.phi])
        end_3d = np.asarray([line_end.r, line_end.z, line_start.phi])
            # to do...

    line = LineString([start_2d, end_2d])
    intersectLine = circle.intersection(line)

    intersect_points_xy = []

    try:
        for coord in intersectLine.coords:
            intersect_points_xy.append(coord)
    except NotImplementedError:
        try:
            firstline = intersectLine.geoms[0]
            for coord in firstline.coords:
                intersect_points_xy.append(coord)
        except NotImplementedError:
            print("Intersection with XY boundary could not be found")

    return intersect_points_xy


def find_point_2d_line(linestart, lineend, x=None, y=None):
    try:
        x1 = linestart.x
        y1 = linestart.y
        x2 = lineend.x
        y2 = lineend.y
    except AttributeError:
        x1 = linestart.r
        y1 = linestart.z
        x2 = lineend.r
        y2 = lineend.z

    try:

        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1

        if x is not None:
            y = m * x + c
            return (x,y)

        if y is not None:
            x = y - m * x
            return (x, y)
    except ZeroDivisionError:
        return None


def find_point_3d_line(linepoint, linedir, x=None, y=None, z=None):

    point = None

    if x is None and y is None and z is None:
        return point

    if (x is not None and linedir[0] == 0) or (y is not None and linedir[1] == 0) or (z is not None and linedir[2] == 0):
        return point

    if x is not None:
        t = (x - linepoint[0]) / linedir[0]
    elif y is not None:
        t = (y - linepoint[1]) / linedir[1]
    else:
        t = (z - linepoint[2]) / linedir[2]

    point = [ linepoint[0] + t * linedir[0],
              linepoint[1] + t * linedir[1],
              linepoint[2] + t * linedir[2] ]

    if np.isclose(point[0], 0.0):
        point[0] = 0.0
    if np.isclose(point[1], 0.0):
        point[1] = 0.0
    if np.isclose(point[2], 0.0):
        point[2] = 0.0


    return point


def calculate_tangency_radius(detector_centre, aperture_centre):
    """
    Calculate the tangency radius of the line of sight of a
    tangentially-viewing pinhole detector.

    The line of sight is assumed to go from the centre of the detector
    throught the centre of the aperture.
    :param detector_centre: the centre point of the detector in Cartesian
        coordinates, as an object with x, y, z attibutes.
    :param aperture_centre: the centre point of the aperture through
        which the detector observes, as an object with x, y, z attributes.
    :return: the tangency radius in the same units as x, y and z.
    """
    detector_centre = np.asarray([detector_centre.x, detector_centre.y, detector_centre.z])
    aperture_centre = np.asarray([aperture_centre.x, aperture_centre.y, aperture_centre.z])
    sightline_vector = aperture_centre - detector_centre
    sightline_unit_vector = sightline_vector / np.linalg.norm(sightline_vector)
    detector_unit_vector = detector_centre / np.linalg.norm(detector_centre)
    costheta = detector_unit_vector.dot(sightline_unit_vector)
    sintheta = np.sqrt(1 - costheta**2)
    rtan = np.linalg.norm(detector_centre) * sintheta
    return rtan
