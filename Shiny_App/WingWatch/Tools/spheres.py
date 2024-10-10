import numpy as np

def find_radius_from_vol(volume):
    radius = (3/4*volume*1/np.pi)**(1/3)
    return radius

def points_for_sphere(theta,phi,offset_x = 0,offset_y=0,offset_z=0,r=1):
    x = r*np.sin(theta) * np.cos(phi) + offset_x
    y = r*np.sin(theta) * np.sin(phi) + offset_y
    z = r*np.cos(theta)  + offset_z
    return np.array([x,y,z])