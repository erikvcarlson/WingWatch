import navpy 
import numpy as np 

def XYZ_distance(ref_lat:float,ref_long:float,ref_alt:float,off_lat:float,off_long:float,off_alt:float):
        #north is positive y
        #east is positive x
        #up is positive z
        navpy_output = navpy.lla2ned(off_lat,off_long,off_alt,ref_lat,ref_long,ref_alt)
        #out put of navpy is north, east, down. We need to convert this to east,north,up
        station_offset = [navpy_output[1],navpy_output[0],navpy_output[2]]

        return station_offset

def convert_back_to_lla(XYZ:list,ref_lat:float,ref_long:float,ref_alt:float):
        #fix for values near null island, the number of zeros is not entirely pulled out of ass, it corresponds to an error of 10cm which is much smaller than the size of the wavelength... might need to change if > 3 GHz transmitters become popular

        if np.abs(ref_lat) <= 1e-7:
                ref_lat = (np.sign(ref_lat) + (ref_lat == 0)) * 1e-7
        if np.abs(ref_long) <= 1e-7:
                ref_long = (np.sign(ref_long) + (ref_long == 0)) * 1e-7
        if np.abs(ref_alt) <= 1e-7:
                ref_alt = (np.sign(ref_alt) + (ref_alt == 0)) * 1e-7

        NED = [XYZ[1],XYZ[0],-XYZ[2]]

        if np.abs(NED[0]) <= 1e-7:
                NED[0] = (np.sign(NED[0]) + (NED[0] == 0)) * 1e-7
        if np.abs(NED[1]) <= 1e-7:
                NED[1] = (np.sign(NED[1]) + (NED[1] == 0)) * 1e-7
        if np.abs(NED[2]) <= 1e-7:
                NED[2] = (np.sign(NED[2]) + (NED[2] == 0)) * 1e-7

        lat,long,alt = navpy.ned2lla(NED,ref_lat,ref_long,ref_alt,latlon_unit='deg',alt_unit='m')
        return [lat,long,alt]