import numpy as np


def montecarlo_intersection(station_data:list):
    """
    Args:
        station_data: A list of nested lists containing the data for each station
        site which is to be intersected. For example, 

        station_data = [[data_BR,BRR_Station],[data_SEL,SEL_Station],[data_BIT,TUR_Station]]
        
        where:

        data_BR = [[1,-92]]
        data_SEL = [[1,-98]]
        data_BIT = [[1,-81]]
    """

    station_shells = []

    for i in range(len(station_data)):
        for j in range(len(station_data[i][0])):
            if station_data[i][0][j][0]-1 >= len(station_data[i][1].antennas): #check to make sure that the port number is not larger than the number of antennas assigned to that port
                continue
        station_shells.append(station_data[i][1].provide_boundary(station_data[i][0][j][0]-1,station_data[i][0][j][1]))

    return station_shells