from WingWatch.Equipment import station
from WingWatch.Equipment import antenna
from WingWatch.Intersections import montecarlo
import pandas as pd
import numpy as np

def test_hello_world():
    """ Testing that I have a rough idea of what is going on"""
    x = 7
    expected = 7
    assert x == expected, ""


def test_motecarlo_intersection():    
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

    test_sol = montecarlo.montecarlo_intersection([[data_BR,BRR_Station]])

    assert np.array_equiv(expected , test_sol)
