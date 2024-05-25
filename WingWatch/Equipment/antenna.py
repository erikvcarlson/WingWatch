import pandas as pd
import numpy as np
import math 
from scipy import spatial

class Antenna: 
    def __init__(self,name,ant_type,orientation,freq):
        self.name = name #string
        self.ant_type = ant_type #antenna type, generally yagi or omni 
        self.orientation = orientation # in units of degrees, 0 degrees is North 
        self.frequency = freq # frequency is megahertz 
    def assign_pattern(self,pattern):
        # the pattern variable is going to be a pandas dataframe read in from our calibration data
        # Define the rotation angle in degrees,use zero for an omni
        theta = self.orientation

        # Convert degrees to radians
        theta = np.deg2rad(theta)

        # Calculate sine and cosine of the rotation angle
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        # Apply rotation matrix to X and Y
        new_x = pattern['X'] * cos_theta - pattern['Y'] * sin_theta
        new_y = pattern['X'] * sin_theta + pattern['Y'] * cos_theta
        
        rotated_df = pd.DataFrame({'X': new_x,'Y': new_y,'Z': pattern['Z'],'RSSI': pattern['RSSI']})

        self.rad_pattern = rotated_df
    def convert_to_lat_long(self,station):
        # Earth radius (mean radius in meters)
        earth_radius = 6371000  # Approximate value for the Earth's mean radius

        # Convert station's latitude and longitude from degrees to radians
        lat1 = math.radians(station.lat)
        lon1 = math.radians(station.long)

        # Calculate new latitude and longitude using DataFrame columns
        lat2 = lat1 + (self.rad_pattern['Y']/ earth_radius)
        lon2 = lon1 + (self.rad_pattern['X'] / (earth_radius * math.cos(lat1)))
        # Convert back to degrees and add the results as new columns
        self.rad_pattern['Latitude'] = np.degrees(lat2)
        self.rad_pattern['Longitude'] = np.degrees(lon2)