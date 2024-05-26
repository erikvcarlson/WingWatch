from WingWatch.Equipment import station
from WingWatch.Equipment import antenna
from WingWatch.Intersections import montecarlo
from WingWatch.Tools import translation,rotation
import pandas as pd
import numpy as np


def test_motecarlo_intersection_single_station():    
    BRR_Station = station.Station('BRR',41.1479, -71.5901)
    BRR_Comp_Data = pd.read_csv('Fake_Calibration_Data.csv')

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

    extra, test_sol = montecarlo.montecarlo_intersection([[data_BR,BRR_Station]],1)

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