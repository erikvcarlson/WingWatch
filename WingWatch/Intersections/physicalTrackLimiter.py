from WingWatch.Intersections.detection import Detection
from WingWatch.Intersections import tri
import trimesh
import pycork
from WingWatch.Tools import spheres
import numpy as np 
import scipy.spatial as ss
# I have a series of detections. From detection A to B the bird can only travel y distance. From detection B to C the bird can only travel y distance from B and 2y from A. I am guessing the pattern looks like this:

# A: x
# B: A + 1y
# C: A+ 2y; B + 1*y
# D: A + 3y; B + 2*y; C + 1*Y


def flight_constraint_bubble(center_x, center_y, center_z, radius_of_init_bubble,time_steps_between_dets,max_flight_speed_per_time_step):

    #generate a bubble which encapsulates the previous detection with the new detection
    
    theta = np.linspace(-np.pi,np.pi,30)
    phi = np.linspace(-2*np.pi,2*np.pi,30)

    #generate the points on that sphere
    points = []
    for i in phi:
        for j in theta:       
            points.append(spheres.points_for_sphere(i,j,offset_x=center_x,offset_y=center_y,offset_z=center_z,r = radius_of_init_bubble+max_flight_speed_per_time_step*time_steps_between_dets))
    
    return points


def grow_convex_hull(points, r):
    # Compute the convex hull
    hull = ss.ConvexHull(points)
    hull_points = points[hull.vertices]

    # Compute the centroid
    centroid = np.mean(hull_points, axis=0)

    # Grow each point of the convex hull outward
    grown_points = []
    for point in hull_points:
        direction_vector = point - centroid
        unit_vector = direction_vector / np.linalg.norm(direction_vector)
        new_point = point + r * unit_vector
        grown_points.append(new_point)

    return np.array(grown_points)

# we can write a recursive function which generates the spheres for each of these detections
#intersection is an associatative property 

def check_constraints(region_1,region_2,max_speed,time_stamp_difference):
    #region_1 is the old detection
    #region 2 in the new detection 

    rad_of_growth = max_speed * time_stamp_difference
    expanded_region = grow_convex_hull(region_1,rad_of_growth)

    #region_2 = ss.ConvexHull(region_2)
    #V1 = expanded_region.volume    
    #V2 = region_2.volume


    # if V1 > V2:
    #     radius_init = spheres.find_radius_from_vol(V2)
    #     region_n_points = flight_constraint_bubble(cx2,cy2,cz2,radius_init,time_stamp_difference,max_speed)
    #     region_m_points = region_1.points
    # else:
    #     radius_init = spheres.find_radius_from_vol(V1)
    #     region_n_points = flight_constraint_bubble(cx1,cy1,cz1,radius_init,time_stamp_difference,max_speed)
    #     region_m_points = region_2.points


    mesh1 = trimesh.convex.convex_hull(expanded_region)
    mesh2 = trimesh.convex.convex_hull(region_2)

    vertsA = mesh1.vertices
    trisA = mesh1.faces

    vertsB = mesh2.vertices
    trisB = mesh2.faces

    vertsD, trisD = pycork.intersection(vertsA, trisA,vertsB, trisB)

    intersections = vertsD
    hull_of_intersections = ss.ConvexHull(intersections,qhull_options='Q12')
  
    '''
    region_1 = ss.ConvexHull(region_1)
    region_2 = ss.ConvexHull(region_2)


    
    
    cx1 = np.mean(region_1.points[region_1.vertices,0])
    cy1 = np.mean(region_1.points[region_1.vertices,1])
    cz1 = np.mean(region_1.points[region_1.vertices,2])


    cx2 = np.mean(region_2.points[region_2.vertices,0])
    cy2 = np.mean(region_2.points[region_2.vertices,1])
    cz2 = np.mean(region_2.points[region_2.vertices,2])

    V1 = region_1.volume
    V2 = region_2.volume

    if V1 > V2:
        radius_init = spheres.find_radius_from_vol(V2)
        region_n_points = flight_constraint_bubble(cx2,cy2,cz2,radius_init,time_stamp_difference,max_speed)
        region_m_points = region_1.points
    else:
        radius_init = spheres.find_radius_from_vol(V1)
        region_n_points = flight_constraint_bubble(cx1,cy1,cz1,radius_init,time_stamp_difference,max_speed)
        region_m_points = region_2.points
    '''    
    #region_n = ss.ConvexHull(region_n_points)


    return intersections,hull_of_intersections