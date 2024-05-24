class Station:
    def __init__(self,name,lat,long):
        self.name = name #Station name - string
        self.lat = lat # Latitude of the station - float 
        self.long = long # Longitude of the station - float
        self.antennas = [] #list of antennas to store antenna objects assigned to the station
    def add_antenna(self, antenna):
        #check if the item we are adding to the antenna list is an antenna, and then add it to the antenna list
        #return an error if the item is invalid. 
        if isinstance(antenna, Antenna):
            self.antennas.append(antenna)
            print(f"{antenna.name} added to {self.name}'s antennas.")
        else:
            print("Invalid antenna object. Please provide an Antenna instance.")
    def list_antennas(self):
        #mostly meant for debugging and information
        #simply iterates over the antennas added to the antenna list and prints the name of the antenna and the frequency 
        print(f"{self.name}'s antennas:")
        for antenna in self.antennas:
            print(f"{antenna.name} ({antenna.frequency} MHz)")
    def provide_boundary(self,antenna_number,RSSI_Thresh,offset_X = 0, offset_Y = 0,offset_Z = 0):
        #antenna_number - int - which antenna number are we generating a geometry for?
        #RSSI_Thresh - int - the RSSI (dBm) of the detection we are looking to generate a border for
        #offset_X - float - the East-West offset from the reference station in meters. Default is 0m
        #offset_Y - float - the North-South offset from the referecne station in meters. Default is 0m 
        
        xy = self.antennas[antenna_number].rad_pattern[self.antennas[antenna_number].rad_pattern.RSSI == RSSI_Thresh]
        
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