import numpy as np
import pandas as pd

def signal_strength(point):
    lambda_wave = 1  # meter
    r = np.sqrt((point[:,0]**2 + point[:,1]**2 + point[:,2]**2))  # Calculate radius
    rssi = 20 * np.log10(4 * np.pi * r / lambda_wave)  # RSSI calculation
    return np.round(rssi)

# Function to generate points on a sphere
def points_for_sphere(r, theta, phi, offset_x=0, offset_y=0, offset_z=0):
    x = r * np.sin(theta) * np.cos(phi) + offset_x
    y = r * np.sin(theta) * np.sin(phi) + offset_y
    z = r * np.cos(theta) + offset_z
    return np.array([x, y, z])

def radius(point,ref_point):
    diff = point - ref_point
    radius_from_reference = np.sqrt(np.sum(diff**2))
    return radius_from_reference

def find_multiple_detection_strengths(point,station_1,station_2,station_3):
    rad_1 = radius(point,station_1)
    rad_2 = radius(point,station_2)
    rad_3 = radius(point,station_3)

    strength_1 = np.round(20 * np.log10(4 * np.pi * rad_1 ))
    strength_2 = np.round(20 * np.log10(4 * np.pi * rad_2 ))
    strength_3 = np.round(20 * np.log10(4 * np.pi * rad_3 ))


    return [strength_1,strength_2,strength_3]