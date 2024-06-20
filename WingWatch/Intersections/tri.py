from WingWatch.Intersections import montecarlo,tritrioverlap
from WingWatch.Tools import line_intersection
from scipy.spatial import ConvexHull

def overlap_of_three_radiation_patterns(station_1_boundary,station_2_boundary,station_3_boundary):
    '''
    station_1_boundary: provided boundary from a command such as 
        = SEL_Station.provide_boundary(0,-98,offset_X=offset_SEL[0],offset_Y=offset_SEL[1],offset_Z=offset_SEL[2]) 
    
    '''
    hull_BRR = ConvexHull(station_1_boundary)
    indices_BRR = hull_BRR.simplices
    triangulation_BRR = station_1_boundary[indices_BRR]

    hull_SEL = ConvexHull(station_2_boundary)
    indices_SEL = hull_SEL.simplices
    triangulation_SEL = station_2_boundary[indices_SEL]
    

    hull_TUR = ConvexHull(station_3_boundary)
    indices_TUR = hull_TUR.simplices
    triangulation_TUR = station_3_boundary[indices_TUR]
   
    sols = []
    for i in range(len(indices_TUR)):
        for j in range(len(indices_BRR)):
                tri_1 = points_for_tri_TUR[indices_TUR[i]]
                tri_2 = points_for_tri_BRR[indices_BRR[j]]
                test_sol_12 = tritrioverlap.triTriOverlapTest3d(tri_1[0], tri_1[1], tri_1[2], tri_2[0], tri_2[1], tri_2[2])
                if test_sol_12 == 1:
                    for k in range(len(indices_SEL)):
                        tri_3 = points_for_tri_SEL[indices_SEL[k]]
                        test_sol_13 = tritrioverlap.triTriOverlapTest3d(tri_1[0], tri_1[1], tri_1[2], tri_3[0], tri_3[1], tri_3[2])
                        test_sol_23 = tritrioverlap.triTriOverlapTest3d(tri_2[0], tri_2[1], tri_2[2], tri_3[0], tri_3[1], tri_3[2])
                        if test_sol_13 == 1 and test_sol_23 == 1:
                            print(i,j,k)
                            sols.append([i,j,k])

    return sols

def intersect_of_two_triangles(edges_T1,edges_T2):

    ## A1, B1, C1 = points_for_tri_TUR[indices_TUR[sols[i][0]]]
    ## A2, B2, C2 = points_for_tri_BRR[indices_BRR[sols[i][1]]]

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