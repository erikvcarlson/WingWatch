import sys
sys.path.insert(1, '/home/user/Research/base-WingWatch')

from WingWatch.Equipment import station
from WingWatch.Equipment import antenna
from WingWatch.Intersections import montecarlo
from WingWatch.Tools import translation
from WingWatch.Calibration import clean_data

import pandas as pd
import numpy as np


cleaned_gps_data = clean_data.clean_gps_data_csv("GPS_Data_apr17_aug30_aug31_sep18_sep26_sep27_First.csv")
cleaned_tag_data = clean_data.clean_motus_Tag_data("allTagsAll390.csv",start_date="",end_date='2022-05-26',calibration_tags_list=[57265,57951,57952])

SOI = ['SE_Light_434','Black_Rock_434','BIWF_Turbine1']
SOI_Lat = [41.1534,41.1479,41.1418]
SOI_Long = [-71.5521,-71.5901,-71.5302]
SOI_Alt = [20,20,20]



data_dataframe = clean_data.merge_gps_and_tag_data(cleaned_tag_data,cleaned_gps_data,stations_of_interest=SOI)



for i in range(len(SOI)):
    for j in range(5):
        temp_data_frame = clean_data.generate_antenna_station_calib_file(data_dataframe,station_of_interest=SOI[i],antenna=j+1,ref_lat = SOI_Lat[i], ref_long = SOI_Long[i], ref_alt = SOI_Alt[i])
        temp_data_frame.to_csv(SOI[i] + '_' + str(j) + '_calib.csv')