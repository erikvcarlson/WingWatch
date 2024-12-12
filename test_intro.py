import numpy as np
from WingWatch.Tools import translation,rotation,point_check,spheres
import WingWatch.Intersections.physicalTrackLimiter as PTL
import pandas as pd
import numpy as np
import scipy.spatial as ss
import fake_data_gen_funcs as fdgc
import pytest

#FUNCTION SET TO BE TEST - TOOLS

def test_points_on_unit_sphere():
    #verify that points generated without offsets or varying radius lie on the unit sphere. Thus it satisfy x^2+y^2+z^2 = 1.
    theta = np.random.uniform(0, np.pi)
    phi = np.random.uniform(0, 2*np.pi)
    point = spheres.points_for_sphere(theta, phi)
    assert np.isclose(np.linalg.norm(point), 1)

def test_points_on_scaled_sphere():
    #verify that radius scaling works. The point should lie on a sphere of radius r
    r = np.random.uniform(1, 10)
    theta = np.random.uniform(0, np.pi)
    phi = np.random.uniform(0, 2*np.pi)
    point = spheres.points_for_sphere(theta, phi, r=r)
    assert np.isclose(np.linalg.norm(point), r)

def test_points_with_offset_sphere():
    #with offsets, check to make sure that each point is correctly shifted from the origin. 
    offset_x, offset_y, offset_z = np.random.uniform(-10, 10, size=3)
    theta = np.random.uniform(0, np.pi)
    phi = np.random.uniform(0, 2*np.pi)
    r = 1
    point = spheres.points_for_sphere(theta, phi, offset_x, offset_y, offset_z, r=r)
    shifted_point = point - np.array([offset_x, offset_y, offset_z])
    assert np.isclose(np.linalg.norm(shifted_point), r)

def test_known_values_on_sphere():
    theta = 0  # At the north pole
    phi = 0
    expected_point = np.array([0, 0, 1])
    assert np.allclose(spheres.points_for_sphere(theta, phi), expected_point)

    theta = np.pi / 2  # Equator
    phi = 0
    expected_point = np.array([1, 0, 0])
    assert np.allclose(spheres.points_for_sphere(theta, phi), expected_point)

def test_finding_radius_zero():
    expected = 0
    assert spheres.find_radius_from_vol(0) == expected  

def test_finding_radius_radius_1():
    expected = 1
    assert np.isclose(spheres.find_radius_from_vol(4/3 * np.pi), expected)  

def test_defined_distance():
    #the distance between two latitudes seperated by 1/60 of a degree is approximately 1 mile
    expected = np.array([0,1843,0])
    test_sol = np.round(translation.XYZ_distance(0,0,0,1/60,0,0))
    assert np.array_equiv(expected,test_sol)

def test_convert_ned_2_lla():
    #given no offset, the input lat,long and alt should be returned
    ref_lat = 10
    ref_long = 5
    ref_alt = 1 
    offset = [0,0,0]
    expected = [10,5,1]   
    assert np.isclose(translation.convert_back_to_lla(offset,ref_lat,ref_long,ref_alt), expected).all()


def test_east_rotation():
    expected = 0
    test_sol = rotation.bearing_to_standard_angle(90)
    assert expected == test_sol

def test_north_0_rotation():
    expected = 90
    test_sol = rotation.bearing_to_standard_angle(0)
    assert expected == test_sol

def test_north_360_rotation():
    expected = 90
    test_sol = rotation.bearing_to_standard_angle(360)
    assert expected == test_sol

def test_north_358_rotation():
    expected = 92
    test_sol = rotation.bearing_to_standard_angle(358)
    assert expected == test_sol

def test_cart_rot():
    expected = np.array([0,1,0])
    test_sol = rotation.cartesian_rotation(np.array([1,0,0]),90)
    assert np.array_equiv(expected,np.round(test_sol))

def test_point_inside_hull():
    points = np.random.rand(10, 3)  # Generate 10 random points in 3D space
    hull = ss.ConvexHull(points)
    # Pick a random point inside the convex hull (e.g., centroid)
    point_inside = np.mean(points, axis=0)
    assert point_check.point_in_hull(point_inside, hull)


def test_point_on_boundary():
    points = np.random.rand(10, 3)
    hull = ss.ConvexHull(points)
    # Pick a vertex of the convex hull, which lies on the boundary
    point_on_boundary = points[hull.vertices[0]]
    assert point_check.point_in_hull(point_on_boundary, hull)
 

def test_point_outside_hull():
    points = np.random.rand(10, 3)
    hull = ss.ConvexHull(points)
    # Pick a point that is outside the convex hull
    point_outside = np.max(points, axis=0) + np.array([1, 1, 1])  # Move the point further away
    assert not point_check.point_in_hull(point_outside, hull)
    

def test_point_in_2d_hull():
    points = np.random.rand(10, 2)  # Generate 2D points
    hull = ss.ConvexHull(points)
    # Pick a point inside the convex hull
    point_inside = np.mean(points, axis=0)
    assert point_check.point_in_hull(point_inside, hull)

#FUNCTION SET TO BE TEST - Calibration Data

def test_single_strength_at_point():
    # Read data from CSV
    df = pd.read_csv('Fake_Calibration_Data.csv')
    # Recalculate radius
    df['radius'] = np.sqrt(df.X**2 + df.Y**2 + df.Z**2)
    # Recalculate RSSI and compare
    calculated_rssi = np.round(20 * np.log10(4 * np.pi * df['radius']), 1)
    # Use np.isclose to compare the recalculated RSSI with the saved one
    comparison = np.isclose(calculated_rssi, df['RSSI'], atol=1)
    assert comparison.all() == True


def test_multi_radial_points_1_offset():
    assert fdgc.radius(np.array([2,2,2]),np.array([1,1,1])) == np.sqrt(3)

def test_multi_radial_points_1a_offset():
    assert fdgc.radius(np.array([2,0,0]),np.array([0,0,0])) == 2

def test_multi_radial_points_no_offset():
    assert fdgc.radius(np.array([0,0,0]),np.array([1,1,1])) == np.sqrt(3)

def test_multi_radial_points_neg_offset():
    assert fdgc.radius(np.array([-1,-1,-1]),np.array([1,1,1])) == 2*np.sqrt(3)

# Test cases for the function
def test_detection_strengths_basic():
    point = np.array([0, 0, 0])
    station_1 = np.array([1, 0, 0])
    station_2 = np.array([0, 1, 0])
    station_3 = np.array([0, 0, 1])
    
    result = fdgc.find_multiple_detection_strengths(point, station_1, station_2, station_3)
    
    assert len(result) == 3
    assert result[0] == pytest.approx(np.round(20 * np.log10(4 * np.pi * 1), 1))
    assert result[1] == pytest.approx(np.round(20 * np.log10(4 * np.pi * 1), 1))
    assert result[2] == pytest.approx(np.round(20 * np.log10(4 * np.pi * 1), 1))

def test_detection_strengths_different_distances():
    point = np.array([0, 0, 0])
    station_1 = np.array([2, 0, 0])
    station_2 = np.array([0, 3, 0])
    station_3 = np.array([0, 0, 4])
    
    result = fdgc.find_multiple_detection_strengths(point, station_1, station_2, station_3)
    
    rad_1 = 2
    rad_2 = 3
    rad_3 = 4
    
    assert result[0] == pytest.approx(np.round(20 * np.log10(4 * np.pi * rad_1)))
    assert result[1] == pytest.approx(np.round(20 * np.log10(4 * np.pi * rad_2)))
    assert result[2] == pytest.approx(np.round(20 * np.log10(4 * np.pi * rad_3)))

def test_detection_strengths_same_station():
    point = np.array([0, 0, 0])
    station_1 = np.array([1, 0, 0])
    station_2 = np.array([1, 0, 0])
    station_3 = np.array([1, 0, 0])
    
    result = fdgc.find_multiple_detection_strengths(point, station_1, station_2, station_3)
    
    rad_1 = 1
    rad_2 = 1
    rad_3 = 1
    
    assert result[0] == pytest.approx(np.round(20 * np.log10(4 * np.pi * rad_1)))
    assert result[1] == pytest.approx(np.round(20 * np.log10(4 * np.pi * rad_2)))
    assert result[2] == pytest.approx(np.round(20 * np.log10(4 * np.pi * rad_3)))

def test_detection_strengths_large_values():
    point = np.array([0, 0, 0])
    station_1 = np.array([1000, 1000, 1000])
    station_2 = np.array([2000, 2000, 2000])
    station_3 = np.array([3000, 3000, 3000])
    
    result = fdgc.find_multiple_detection_strengths(point, station_1, station_2, station_3)
    
    rad_1 = np.linalg.norm([1000, 1000, 1000])
    rad_2 = np.linalg.norm([2000, 2000, 2000])
    rad_3 = np.linalg.norm([3000, 3000, 3000])
    
    assert result[0] == pytest.approx(np.round(20 * np.log10(4 * np.pi * rad_1)))
    assert result[1] == pytest.approx(np.round(20 * np.log10(4 * np.pi * rad_2)))
    assert result[2] == pytest.approx(np.round(20 * np.log10(4 * np.pi * rad_3)))

def test_convert_ned_2_lla_0s():
    #given no offset, the input lat,long and alt should be returned
    ref_lat = 0
    ref_long = 0
    ref_alt = 0 
    offset = [0,0,0]
    expected = [ref_lat,ref_long,ref_alt]   
    assert np.isclose(translation.convert_back_to_lla(offset,ref_lat,ref_long,ref_alt), expected,atol=1e-6).all()

def test_convert_ned_2_lla_long_0():
    #given no offset, the input lat,long and alt should be returned
    ref_lat = 40
    ref_long = 0
    ref_alt = 0 
    offset = [0,0,0]
    expected = [ref_lat,ref_long,ref_alt]   
    assert np.isclose(translation.convert_back_to_lla(offset,ref_lat,ref_long,ref_alt), expected,atol=1e-6).all()

def test_convert_ned_2_lla_lat_0():
    #given no offset, the input lat,long and alt should be returned
    ref_lat = 0
    ref_long = 40
    ref_alt = 0 
    offset = [0,0,0]
    expected = [ref_lat,ref_long,ref_alt]   
    assert np.isclose(translation.convert_back_to_lla(offset,ref_lat,ref_long,ref_alt), expected,atol=1e-6).all()

#need to check ned2lla at the poles

#FUNCTION SET TO BE TEST - Track Constraints

def test_uncert_bubble_gen():
    point_cloud = PTL.flight_constraint_bubble(0, 0, 0, 1,1,2) #a sphere located at the origin with radius 1 with timestep 1 and velocity 2
    #this solution should be the same as a sphere located at the origin with radius 3
    r = 3
    theta = np.linspace(-np.pi,np.pi,30)
    phi = np.linspace(-2*np.pi,2*np.pi,30)

    expected_cloud = []
    for i in phi:
        for j in theta:       
            expected_cloud.append(spheres.points_for_sphere(i, j, r=r))

    point_cloud = np.row_stack(point_cloud)
    expected_cloud = np.row_stack(expected_cloud)
    assert np.isclose(point_cloud , expected_cloud).all()

def test_check_constraints_bubbles_should_be_smaller():
    r = 1
    theta = np.linspace(-np.pi,np.pi,30)
    phi = np.linspace(-2*np.pi,2*np.pi,30)

    region_1 = []
    for i in phi:
        for j in theta:       
            region_1.append(spheres.points_for_sphere(i, j, r=r))

    region_1 = np.row_stack(region_1)

    region_2 = []
    for i in phi:
        for j in theta:       
            region_2.append(spheres.points_for_sphere(i, j, r=r,offset_x=2))

    region_2 = np.row_stack(region_2)

    intersections,hull_of_intersections = PTL.check_constraints(region_1,region_2,max_speed=1,time_stamp_difference=1)
  
    assert intersections[:,0].max() <= 2 and intersections[:,0].min() >= 1




# def test_degenerate_case_colinear_points():
#     points = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0],[3, 0, 0]])  # Collinear points
#     hull = ss.ConvexHull(points)
#     point_outside = np.array([0, 1, 0])  # This point should be outside
#     assert not point_check.point_in_hull(point_outside, hull)


# def find_radius_from_vol(volume):
#     radius = (3/4*volume*1/np.pi)**(1/3)
#     return radius
'''
from WingWatch.Deprecated import tritrioverlap
from WingWatch.Equipment import station
from WingWatch.Equipment import antenna
from WingWatch.Intersections import montecarlo
from WingWatch.Tools import translation,rotation,point_check
import pandas as pd
import numpy as np
import scipy.spatial as ss
from math import isclose



def test_motecarlo_intersection_single_station():    
    BRR_Station = station.Station('BRR',41.1479, -71.5901)
    BRR_Comp_Data = pd.read_csv('tests/Fake_Calibration_Data.csv')

    a1 = antenna.Antenna('1','test',0,434)
    a1.assign_pattern(BRR_Comp_Data)
    a1.convert_to_lat_long(BRR_Station)
    BRR_Station.add_antenna(a1)



    expected = []
    data_BR = [[1,-92]]

    for i in range(len(data_BR)):
        if data_BR[i][0]-1 >= len(BRR_Station.antennas):
            continue  
        expected.append(BRR_Station.provide_boundary(data_BR[i][0]-1 ,data_BR[i][1]))

    extra, extra_1, test_sol = montecarlo.montecarlo_intersection([[data_BR,BRR_Station]],1)

    assert np.array_equiv(expected , test_sol)


def test_defined_distance():
    #the distance between two latitudes seperated by 1/60 of a degree is approximately 1 mile
    expected = np.array([0,1843,0])
    test_sol = np.round(translation.XYZ_distance(0,0,0,1/60,0,0))
    assert np.array_equiv(expected,test_sol)


def test_east_rotation():
    expected = 0
    test_sol = rotation.bearing_to_standard_angle(90)
    assert expected == test_sol

def test_north_0_rotation():
    expected = 90
    test_sol = rotation.bearing_to_standard_angle(0)
    assert expected == test_sol

def test_north_360_rotation():
    expected = 90
    test_sol = rotation.bearing_to_standard_angle(360)
    assert expected == test_sol

def test_north_358_rotation():
    expected = 92
    test_sol = rotation.bearing_to_standard_angle(358)
    assert expected == test_sol

def test_cart_rot():
    expected = np.array([0,1,0])
    test_sol = rotation.cartesian_rotation(np.array([1,0,0]),90)
    assert np.array_equiv(expected,np.round(test_sol))

def test_convert_back_to_lat_long_EW():
#the distance between two latitudes seperated by 1/60 of a degree is approximately 1 mile
    expected = np.array([0,0,0])
    test_sol = np.round(translation.convert_back_to_lla([0,1843,0],0,1/60,0))
    assert np.array_equiv(expected,test_sol)


def test_convert_back_to_lat_long_NS():
#the distance between two latitudes seperated by 1/60 of a degree is approximately 1 mile
    expected = np.array([0,0,0])
    test_sol = np.round(translation.convert_back_to_lla([1843,0,0],1/60,0,0))
    assert np.array_equiv(expected,test_sol)


def test_triangle_intersection_no_intersect():
   # Example usage
    p1 = np.array([0, 0, 0])
    q1 = np.array([1, 0, 0])
    r1 = np.array([0, 1, 0])
    p2 = np.array([0, 0, 1])
    q2 = np.array([1, 0, 1])
    r2 = np.array([0, 1, 1])

    test_sol = tritrioverlap.triTriOverlapTest3d(p1, q1, r1, p2, q2, r2)
    expected = 0 
    assert expected == test_sol


def test_triangle_intersection_intersect():
    #triangle 1(T1) will have verticies (V10,V11,V12)

    V10 = np.array([1,0,0])
    V11 = np.array([0,1,0])
    V12 = np.array([0,0,0])

    #triangle 2(T2) will have verticies (V20,V21,V22)

    V20 = np.array([1+0.5,0,0] )
    V21 = np.array([0,1,0])
    V22 = np.array([0+0.5,0,0])

    expected = 1
    test_sol = tritrioverlap.triTriOverlapTest3d(V10, V11, V12, V20, V21, V22)
    assert expected == test_sol


def points_on_unit_sphere(theta,phi,offset_x = 0,offset_y=0,offset_z=0):
    x = np.sin(theta) * np.cos(phi) + offset_x
    y = np.sin(theta) * np.sin(phi) + offset_y
    z = np.cos(theta)  +offset_z
    return np.array([x,y,z])


def test_points_on_unit_sphere():
    #Function to Test: Tools.point_check.point_in_hull
    #given a test point at (0,0,0) does exist in a sphere of radius 1
    expected =True

    
    offset_x = 0
    offset_y = 0 
    offset_z = 0
  
    theta = np.linspace(-np.pi,np.pi,30)
    phi = np.linspace(-2*np.pi,2*np.pi,30)

    points = []

    for i in phi:
        for j in theta:       
            points.append(points_on_unit_sphere(i,j))

    points = np.row_stack(np.array(points))
    
    #we can show that every point exists on the unit sphere by showing its radius from the origin is 1. 
    #note that python's floating point precision is only good to 16 digits, this we need to round to 15 digits. 

    radius_of_point = np.round(np.sqrt(np.sum([np.power(points[:,0],2),np.power(points[:,1],2),np.power(points[:,2],2)],axis=0)),15)

    test_sol = np.all(radius_of_point == 1)

    assert expected == test_sol 


def test_point_in_center_of_sphere():
    #Function to Test: Tools.point_check.point_in_hull
    #given a test point at (0,0,0) does exist in a sphere of radius 1
    
    expected =True

    test_point = np.array([0,0,0])
    
    theta = np.linspace(-np.pi,np.pi,30)
    phi = np.linspace(-2*np.pi,2*np.pi,30)

    points = []

    for i in phi:
        for j in theta:       
            points.append(points_on_unit_sphere(i,j))



    tess_sphere = ss.ConvexHull(points)

    test_sol = point_check.point_in_hull(test_point,tess_sphere)

    assert expected == test_sol 


def test_bearing_to_standard_angle():
    # Test standard angles
    assert rotation.bearing_to_standard_angle(0) == 90
    assert rotation.bearing_to_standard_angle(90) == 0
    assert rotation.bearing_to_standard_angle(180) == 270
    assert rotation.bearing_to_standard_angle(270) == 180
    
    # Test angles greater than 360
    assert rotation.bearing_to_standard_angle(450) == 0  # 450 - 360 = 90 -> standard = 0
    
    # Test negative angles
    assert rotation.bearing_to_standard_angle(-90) == 180
    assert rotation.bearing_to_standard_angle(-450) == 180  # -450 + 360 = -90 -> standard = 180

def test_cartesian_rotation():
    # Test rotating around z-axis with known angles
    
    data = np.array([[1, 0, 0]])
    
    # 90 degrees rotation should place the point on the y-axis
    rotated_data = rotation.cartesian_rotation(data, 90)
    
    rotated_data_X = rotated_data[0, 0]
    rotated_data_Y = rotated_data[0, 1]
    rotated_data_Z = rotated_data[0, 2]

    assert isclose(rotated_data_X, 0, abs_tol=1e-9)
    assert isclose(rotated_data_Y, 1, abs_tol=1e-9)
    assert isclose(rotated_data_Z, 0, abs_tol=1e-9)

    # 180 degrees rotation should place the point on the negative x-axis
    rotated_data = rotation.cartesian_rotation(data, 180)

    rotated_data_X = rotated_data[0, 0]
    rotated_data_Y = rotated_data[0, 1]
    rotated_data_Z = rotated_data[0, 2]


    assert isclose(rotated_data_X, -1, abs_tol=1e-9)
    assert isclose(rotated_data_Y, 0, abs_tol=1e-9)
    assert isclose(rotated_data_Z, 0, abs_tol=1e-9)

    # 270 degrees rotation should place the point on the negative y-axis
    rotated_data = rotation.cartesian_rotation(data, 270)
    
    rotated_data_X = rotated_data[0, 0]
    rotated_data_Y = rotated_data[0, 1]
    rotated_data_Z = rotated_data[0, 2]
 
    
    assert isclose(rotated_data_X, 0, abs_tol=1e-9)
    assert isclose(rotated_data_Y, -1, abs_tol=1e-9)
    assert isclose(rotated_data_Z, 0, abs_tol=1e-9)

    # 360 degrees rotation should bring it back to the original position
    rotated_data = rotation.cartesian_rotation(data, 360)

    rotated_data_X = rotated_data[0, 0]
    rotated_data_Y = rotated_data[0, 1]
    rotated_data_Z = rotated_data[0, 2]

    assert isclose(rotated_data_X, 1, abs_tol=1e-9)
    assert isclose(rotated_data_Y, 0, abs_tol=1e-9)
    assert isclose(rotated_data_Z, 0, abs_tol=1e-9)

    # Test rotating multiple points
    data = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    rotated_data = rotation.cartesian_rotation(data, 90)
    
    expected_rotated_data = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    
    assert np.allclose(rotated_data, expected_rotated_data, atol=1e-9)



'''

# def test_convert_ned_2_lla_0s():
#     #given no offset, the input lat,long and alt should be returned
#     ref_lat = 0
#     ref_long = 0
#     ref_alt = 0 
#     offset = [0,0,0]
#     expected = [ref_lat,ref_long,ref_alt]   
#     assert np.isclose(translation.convert_back_to_lla(offset,ref_lat,ref_long,ref_alt), expected).all()
