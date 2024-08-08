from WingWatch.Deprecated import tritrioverlap
from WingWatch.Equipment import station
from WingWatch.Equipment import antenna
from WingWatch.Intersections import montecarlo
from WingWatch.Tools import translation,rotation,point_check
import pandas as pd
import numpy as np
import scipy.spatial as ss





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



'''
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

'''