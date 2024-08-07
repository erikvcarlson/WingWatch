import navpy 

def XYZ_distance(ref_lat:float,ref_long:float,ref_alt:float,off_lat:float,off_long:float,off_alt:float):
        #north is positive y
        #east is positive x
        #up is positive z
        navpy_output = navpy.lla2ned(off_lat,off_long,off_alt,ref_lat,ref_long,ref_alt)
        #out put of navpy is north, east, down. We need to convert this to east,north,up
        station_offset = [navpy_output[1],navpy_output[0],navpy_output[2]]

        return station_offset

def convert_back_to_lla(XYZ:list,ref_lat:float,ref_long:float,ref_alt:float):
        NED = [XYZ[1],XYZ[0],-XYZ[2]]
        lat,long,alt = navpy.ned2lla(NED,ref_lat,ref_long,ref_alt,latlon_unit='deg',alt_unit='m')
        return [lat,long,alt]