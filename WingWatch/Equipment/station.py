import pandas as pd
import numpy as np
import math 
from scipy import spatial
from WingWatch.Equipment import antenna as ant
import warnings



class Station:
    def __init__(self,name,lat,long,alt=0):
        self.name = name #Station name - string
        self.lat = lat # Latitude of the station - float 
        self.long = long # Longitude of the station - float
        self.alt = alt
        self.antennas = [] #list of antennas to store antenna objects assigned to the station
        
    def add_antenna(self, antenna, antenna_number=None):
        # Default to appending if no specific number is given
        if antenna_number is None:
            antenna_number = len(self.antennas)

        if not isinstance(antenna, ant.Antenna):
            print("Invalid antenna object. Please provide an Antenna instance.")
            return
        
        if antenna_number >= len(self.antennas):
            # Create a new list with the necessary size, copying over existing values
            new_antennas = [None] * (antenna_number)
            
            # Copy existing antennas into the new list
            for i in range(len(self.antennas)):
                new_antennas[i] = self.antennas[i]

            # Replace the old list with the new one
            self.antennas = new_antennas

        # Add the antenna at the specified index
        self.antennas[antenna_number-1] = antenna
        print(f"{antenna.name} added to {self.name}'s antennas at position {antenna_number}.")


    def list_antennas(self):
        #mostly meant for debugging and information
        #simply iterates over the antennas added to the antenna list and prints the name of the antenna and the frequency 
        print(f"{self.name}'s antennas:")
        for antenna in self.antennas:
            print(f"{antenna.name} ({antenna.frequency} MHz)")
    
    def myround(self,n): #round to the first non-zero decimal place
        if n == 0:
            return 0
        sgn = -1 if n < 0 else 1
        scale = int(-math.floor(math.log10(abs(n))))
        if scale <= 0:
            scale = 1
        factor = 10**scale
        return sgn*math.floor(abs(n)*factor)/factor


    def provide_boundary(self,antenna_number,RSSI_Thresh,offset_X = 0, offset_Y = 0,offset_Z = 0):
        #antenna_number - int - which antenna number are we generating a geometry for?
        #RSSI_Thresh - int - the RSSI (dBm) of the detection we are looking to generate a border for
        #offset_X - float - the East-West offset from the reference station in meters. Default is 0m
        #offset_Y - float - the North-South offset from the referecne station in meters. Default is 0m 
        

        xy = self.antennas[antenna_number].rad_pattern[self.antennas[antenna_number].rad_pattern.RSSI == RSSI_Thresh]


        #if the calibration data does not contain the exact detected rssi for that antenna, we will iterate over weaker detections strengths until xy is not empty.
        #in theory, I don't actually think the number of iterations is that large as we should automatically just filter to the next calibration strength present in the data
        #I might need to increase this a value from not empyty to something slightly larger as Convex hull requires a certain number of points to work 
        
        if xy.empty == True:
            increase_by_val = 0

            while xy.empty == True:
                list_of_data_frame_values_less_than_target_val = self.antennas[antenna_number].rad_pattern[self.antennas[antenna_number].rad_pattern.RSSI < RSSI_Thresh]
                list_of_data_frame_values_less_than_target_val = list_of_data_frame_values_less_than_target_val.RSSI.drop_duplicates().sort_values()
                xy = self.antennas[antenna_number].rad_pattern[self.antennas[antenna_number].rad_pattern.RSSI == list_of_data_frame_values_less_than_target_val.iloc[increase_by_val]]
                difference = self.myround(list_of_data_frame_values_less_than_target_val.iloc[increase_by_val] - RSSI_Thresh)
                increase_by_val = increase_by_val + 1
            warnings.warn("Using a weaker signal than detected. Use denser calibration data to avoid this error. The RSSI was " + str(difference) + ' units weaker.')
        
        x = xy.X + offset_X
        y = xy.Y + offset_Y
        z = xy.Z + offset_Z
        xyz = np.column_stack((np.array(x).T,np.array(y).T,np.array(z).T))
        hull = spatial.ConvexHull(xyz, incremental=False, qhull_options='Qt')
        hull_indices = hull.vertices

        boundary_x = []
        boundary_y = []
        boundary_z = []
        for i in range(len(hull_indices)):
            index = hull_indices[i]
            boundary_x.append(xyz[index, 0].astype('float64'))
            boundary_y.append(xyz[index, 1].astype('float64'))
            boundary_z.append(xyz[index, 2].astype('float64'))
        # return a Nx3 numpy array with the points which make the complex hull (boundary) of points which contain the
        # points with a signal strength greater than or equal to the threshold 
        return np.column_stack((np.array(boundary_x).T,np.array(boundary_y).T,np.array(boundary_z).T))