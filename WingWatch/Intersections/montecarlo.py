import numpy as np
from shapely.geometry import Point, Polygon
from WingWatch.Tools import translation

def montecarlo_intersection(station_data:list,test:bool=0):
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


    ref_lat = station_data[0][1].lat
    ref_long = station_data[0][1].long
    ref_alt = station_data[0][1].alt

    for i in range(len(station_data)):
        offset = translation.XYZ_distance(ref_lat,ref_long,ref_alt,station_data[i][1].lat,station_data[i][1].long,station_data[i][1].alt)
        for j in range(len(station_data[i][0])):
            if station_data[i][0][j][0]-1 >= len(station_data[i][1].antennas): #check to make sure that the port number is not larger than the number of antennas assigned to that port
                continue
        
        station_shells.append(station_data[i][1].provide_boundary(station_data[i][0][j][0]-1,station_data[i][0][j][1],offset[0],offset[1],offset[2]))


    station_shells_stacked = np.row_stack(station_shells)


    # Define the range for x and y values
    x_values_hull = station_shells_stacked[:,0]
    y_values_hull = station_shells_stacked[:,1]
    z_values_hull = station_shells_stacked[:,2]

    x_min, x_max = np.min(x_values_hull), np.max(x_values_hull)
    y_min, y_max = np.min(y_values_hull), np.max(y_values_hull)
    z_min, z_max = np.min(z_values_hull), np.max(z_values_hull)

    # Generate 1e5 (100,000) random 2D points
    num_points = int(1e5)
    x_values = np.random.uniform(x_min, x_max, num_points)
    y_values = np.random.uniform(y_min, y_max, num_points)
    z_values = np.random.uniform(z_min, z_max, num_points)

    # Combine x and y values into 2D points
    points = np.column_stack((x_values, y_values,z_values))

    # Example usage:
    #hull_vertices = [(0, 0), (0, 1), (1, 1), (1, 0)]
    #point_to_check = (25000, 0.5)

    result_nested_list = [] 

    for j in station_shells:
        result_nested_list.append([is_point_inside_hull(j, x) for x in points])


    result_nested_list = np.column_stack(result_nested_list)

    index_map = np.all(result_nested_list,axis=1)

    if test == 0:
        return points,index_map
    elif test == 1:
        return points,index_map,station_shells


def is_point_inside_hull(hull_vertices, point):
    hull_polygon = Polygon(hull_vertices)
    point = Point(point)
    return hull_polygon.contains(point)