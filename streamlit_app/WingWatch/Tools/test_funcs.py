import numpy as np

def points_on_unit_sphere(theta,phi,offset_x = 0,offset_y=0,offset_z=0):
    #do I need to write a test function for this? 
    x = np.sin(theta) * np.cos(phi) + offset_x
    y = np.sin(theta) * np.sin(phi) + offset_y
    z = np.cos(theta)  +offset_z
    return np.array([x,y,z])
