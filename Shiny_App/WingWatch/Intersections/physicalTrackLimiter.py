from WingWatch.Intersections.detection import Detection
from WingWatch.Intersections import tri
import trimesh
from WingWatch.Tools import spheres
import numpy as np 
import scipy.spatial as ss
from scipy.spatial.distance import cdist

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
    
    #I only want to grow the smaller region.
    
                  
    region_1_hull = ss.ConvexHull(region_1)
    region_2_hull = ss.ConvexHull(region_2)

    if region_1_hull.volume >= region_2_hull.volume:
        expanded_region = grow_convex_hull(region_2,rad_of_growth)
        region_static = region_1
    elif region_2_hull.volume > region_1_hull.volume:
        expanded_region = grow_convex_hull(region_1,rad_of_growth)
        region_static = region_2

    mesh1 = trimesh.convex.convex_hull(expanded_region)
    mesh2 = trimesh.convex.convex_hull(region_static)




    # Parameters of the box
    x_min, x_max = -30000, 30000 #this needs to be sufficiently large as to not accidently effect the result of the translational accuracy. 
    y_min, y_max = -30000, 30000
    z_min, z_max = 0, 30000
    step = 5000  # Change this value for finer or coarser granularity

    above_ground_boundary = tri.generate_box_surface_points(x_min, x_max, y_min, y_max, z_min, z_max, step)

    mesh_above_ground = trimesh.convex.convex_hull(above_ground_boundary)
    
    #vertsA = mesh1.vertices
    #trisA = mesh1.faces

    #vertsB = mesh2.vertices
    #trisB = mesh2.faces
    #this is a temp fix to fix a case where the new regions do not overlap. If they do not overlap, I am just returning the larger region
    
    mesh3 = trimesh.boolean.intersection([mesh1,mesh2,mesh_above_ground])
    
    
    intersections = mesh3.vertices
    hull_of_intersections = ss.ConvexHull(intersections,qhull_options='Q12')
    #intersections = expanded_region
    #hull_of_intersections = ss.ConvexHull(intersections,qhull_options='Q12')
        
    return intersections,hull_of_intersections



def check_constraints_two_region(region_1,region_2,region_3,max_speed,time_stamp_difference):

    #region_1 is the oldest detection
    #region_2 is the old detection
    #region 3 in the new detection 

    #I only want to grow the smaller region.
    
                  
    region_1_hull = ss.ConvexHull(region_1)
    region_2_hull = ss.ConvexHull(region_2)

    if region_1_hull.volume >= region_2_hull.volume:
        rad_of_growth = max_speed * time_stamp_difference
        expanded_region = grow_convex_hull(region_2,rad_of_growth)
        region_static = region_1
    elif region_2_hull.volume > region_1_hull.volume:
        rad_of_growth = max_speed * time_stamp_difference
        expanded_region = grow_convex_hull(region_1,rad_of_growth)
        region_static = region_2

    mesh1 = trimesh.convex.convex_hull(expanded_region)
    mesh2 = trimesh.convex.convex_hull(region_static)
    mesh3 = trimesh.convex.convex_hull(region_3)
    mesh4 = trimesh.boolean.intersection([mesh1,mesh2,mesh3])
    intersections = mesh3.vertices
    hull_of_intersections = ss.ConvexHull(intersections,qhull_options='Q12')
    return intersections,hull_of_intersections


def weighted_center_approach(region_1,loc_ant1,loc_ant2,loc_ant3):


    # loc_ant1 presumably a list
    # det1_ss detection signal strengh 
    # det2_ss detection signal strengh

    
    rss_combined = np.zeros(len(region_1))
    for i, point in enumerate(region_1.points):
        distances1 = cdist([point], loc_ant1)[0]
        distances2 = cdist([point], loc_ant2)[0]
        distances3 = cdist([point], loc_ant3)[0]
        
        # Weight inversely proportional to distance
        weights1 = det1_ss / (distances1 + 1e-6)
        weights2 = det2_ss / (distances2 + 1e-6)
        weights3 = det3_ss / (distances3 + 1e-6)
        
        # Combined RSS weight
        rss_combined[i] = np.sum(weights1) + np.sum(weights2) + np.sum(weights3)

    # Find the point with maximum likelihood
    max_index = np.argmax(rss_combined)
    most_likely_point = region_1[max_index]

    return 