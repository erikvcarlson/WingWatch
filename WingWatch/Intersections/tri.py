from WingWatch.Intersections import montecarlo
#from WingWatch.Tools import line_intersection, tritrioverlap #deprecated 9/12/2024
from scipy.spatial import ConvexHull
from WingWatch.Tools import translation
import numpy as np
import scipy.spatial as ss
import WingWatch.Tools.point_check as pc
import trimesh
import pycork


def generate_station_shells(list_of_detections:list):
    station_shells = []

    #We use the first antenna in the passed data as a way to measure the offset in the geometries to the other antennas   
    ref_lat =list_of_detections[0].station.lat
    ref_long = list_of_detections[0].station.long
    ref_alt = list_of_detections[0].station.alt

    for i in range(len(list_of_detections)):
        station_of_interest = list_of_detections[i].station
        offset = translation.XYZ_distance(ref_lat,ref_long,ref_alt,station_of_interest.lat,station_of_interest.long,station_of_interest.alt)
                
        #antenna number of the detection is larger than the total number of antennas assigned to the station, skip it
        if list_of_detections[i].antenna-1 > len(station_of_interest.antennas): 
            continue
        
        station_shells.append(station_of_interest.provide_boundary(list_of_detections[i].antenna-1,list_of_detections[i].rssi,offset[0],offset[1],offset[2]))
    

        # for j in range(len(detections_on_station)):
        #     single_detection = detections_on_station[j]
        #     antenna_number_of_detection = single_detection[0] - 1
        #     #antenna number of the detection is larger than the total number of antennas assigned to the station, skip it
        #     if antenna_number_of_detection > len(station_of_interest.antennas): 
        #         continue
        #     station_shells.append(station_data[i][1].provide_boundary(station_data[i][0][j][0]-1,station_data[i][0][j][1],offset[0],offset[1],offset[2]))
        # #except:
        # #    pass

    return station_shells


def intersect_of_two_triangles(edges_T1,edges_T2):
    #potnetially deprecated - EC - 8/1/2024
    ## A1, B1, C1 = points_for_tri_TUR[station_3_indices[sols[i][0]]]
    ## A2, B2, C2 = points_for_tri_BRR[station_1_indices[sols[i][1]]]

    # Edges of T1
    #edges_T1 = [(A1, B1), (B1, C1), (C1, A1)]

    # Edges of T2
    #edges_T2 = [(A2, B2), (B2, C2), (C2, A2)]


    # Find intersections between T1 and T2
    intersections = []
    for edge1 in edges_T1:
        for edge2 in edges_T2:
            intersection = line_intersection(edge1[0], edge1[1], edge2[0], edge2[1])
            if intersection is not None:
                intersections.append(intersection)

    return intersections


def overlap_of_three_radiation_patterns(list_of_detections):
    '''
    station_1_boundary: provided boundary from a command such as 
        = SEL_Station.provide_boundary(0,-98,offset_X=offset_SEL[0],offset_Y=offset_SEL[1],offset_Z=offset_SEL[2]) 
    
    '''

    #we need to grab the boundary points for each of the shells at the defined RSSI
    station_shells = generate_station_shells(list_of_detections)
   
    #Once we have done that we can breakup the station shells data into three seperate components
    station_1_boundary = station_shells[0]
    station_2_boundary = station_shells[1]
    station_3_boundary = station_shells[2]

    #We then generate a ConvexHull Object for each of the stations, find the simplicies (I think this is wrong now that I think about it), and then grab the verticies which correspond to their simplices
    #The reason why I think this is wrong is because we end up with triangulations which cross through the hull. That is not all simplicies are faces 
    
    
    
    #station_1_hull = ConvexHull(station_1_boundary)
    #station_1_indices = station_1_hull.simplices
    #triangulation_station_1 = station_1_boundary[station_1_indices]

    #station_2_hull = ConvexHull(station_2_boundary)
    #station_2_indices = station_2_hull.simplices
    #triangulation_station_2 = station_2_boundary[station_2_indices]
    

    #station_3_hull = ConvexHull(station_3_boundary)
    #station_3_indices = station_3_hull.simplices
    #triangulation_station_3 = station_3_boundary[station_3_indices]
   

    #BACK ON TRACK WITH A NEW APPROACH 
    #We generate a mesh of each of the sources using the trimesh software package
    mesh = trimesh.convex.convex_hull(station_1_boundary)
    mesh_1 = trimesh.convex.convex_hull(station_2_boundary)
    mesh_2 = trimesh.convex.convex_hull(station_3_boundary)


    vertsA = mesh.vertices
    trisA = mesh.faces

    vertsB = mesh_1.vertices
    trisB = mesh_1.faces

    vertsC = mesh_2.vertices
    trisC = mesh_2.faces

    vertsD, trisD = pycork.intersection(vertsA, trisA,vertsB, trisB)

    vertsE, trisE = pycork.intersection(vertsD, trisD,vertsC, trisC)

    intersections = vertsE
    hull_of_intersections = ss.ConvexHull(vertsE)

    #potentially deprecated - EC - 8/1/2024
    # sols = []
    # for i in range(len(station_1_indices)):
    #     for j in range(len(station_2_indices)):
    #             tri_1 = station_1_boundary[station_1_indices[i]]
    #             tri_2 = station_2_boundary[station_2_indices[j]]
    #             test_sol_12 = tritrioverlap.triTriOverlapTest3d(tri_1[0], tri_1[1], tri_1[2], tri_2[0], tri_2[1], tri_2[2])
    #             if test_sol_12 == 1:
    #                 for k in range(len(station_3_indices)):
    #                     tri_3 = station_3_boundary[station_3_indices[k]]
    #                     test_sol_13 = tritrioverlap.triTriOverlapTest3d(tri_1[0], tri_1[1], tri_1[2], tri_3[0], tri_3[1], tri_3[2])
    #                     test_sol_23 = tritrioverlap.triTriOverlapTest3d(tri_2[0], tri_2[1], tri_2[2], tri_3[0], tri_3[1], tri_3[2])
    #                     if test_sol_13 == 1 and test_sol_23 == 1:
    #                         #print(i,j,k)
    #                         sols.append([i,j,k])
    # intersections = []
    # for i in range(len(sols)):
    #     A1, B1, C1 = station_1_boundary[station_1_indices[sols[i][0]]]
    #     A2, B2, C2 = station_2_boundary[station_2_indices[sols[i][1]]]
    #     A3, B3, C3 = station_3_boundary[station_3_indices[sols[i][2]]]

    #     # Edges of T1
    #     edges_T1 = [(A1, B1), (B1, C1), (C1, A1)]

    #     # Edges of T2
    #     edges_T2 = [(A2, B2), (B2, C2), (C2, A2)]

    #     # Edges of T3
    #     edges_T3 = [(A3, B3), (B3, C3), (C3, A3)]

    #     # Find intersections between T1 and T2
        
    #     for edge1 in edges_T1:
    #         for edge2 in edges_T2:
    #             intersection = line_intersection.line_intersection(edge1[0], edge1[1], edge2[0], edge2[1])
    #             if intersection is not None:
    #                 intersections.append(intersection)

    # intersections = np.row_stack(intersections)
    # hull_of_intersections = ss.ConvexHull(intersections)
    # a = np.mean(intersections[hull_of_intersections.vertices],axis=0)
    # b = np.std(intersections[hull_of_intersections.vertices],axis=0)
    return intersections,hull_of_intersections




