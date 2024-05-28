import pandas as pd
import numpy as np
from WingWatch.Tools import translation

def clean_motus_Tag_data(data_csv:str,calibration_tags_list,start_date="",end_date=""):
    """
    start_date = 'YYYY-MM-DD'
    end_date = 'YYYY-MM-DD'
    calibration_tags_list = list of ints = []
    """

    df_tags_uncleaned = pd.read_csv(data_csv,low_memory=False)

    df_tags_uncleaned['ts'] = pd.to_datetime(df_tags_uncleaned['ts'])
    df_tags_dated = df_tags_uncleaned[df_tags_uncleaned['ts'] < pd.to_datetime(end_date)]

    df_reduced_col = df_tags_dated[['tsCorrected','sig','port','recvDeployName','motusTagID','mfgID']]

    df_with_station_detections = df_reduced_col.dropna(axis=0)

    calibration_tags_only = df_with_station_detections[df_with_station_detections['motusTagID'].isin(calibration_tags_list)]

    port_uncleaned = calibration_tags_only["port"].to_list()
    port_cleaned = [int(string[-1]) for string in port_uncleaned]
    calibration_tags_only['port'] = port_cleaned

    return calibration_tags_only


def clean_gps_data_csv(data_csv:str):

    df_gps_uncleaned = pd.read_csv(data_csv)

    df_gps_reduced_col = df_gps_uncleaned[["Y","X","ele","time"]]
    df_gps_reduced_col['time'] = pd.to_datetime(df_gps_reduced_col['time']).astype(int) / 10**9

    return df_gps_reduced_col


def merge_gps_and_tag_data(tag_data,gps_data,stations_of_interest:list):
    
    stations_we_care_about = tag_data[tag_data['recvDeployName'].isin(stations_of_interest)]

    unique_time_stamps = np.unique(stations_we_care_about["tsCorrected"].to_numpy())

    df_uts = pd.DataFrame(unique_time_stamps,columns=['time'])

    a = df_uts.time.isin(gps_data['time'] )
    b = gps_data.time.isin(df_uts['time'] )

    df_gps_reduced_col_1 = gps_data[b]

    df_gps_reduced_col_1 = df_gps_reduced_col_1.rename(columns={"time":"tsCorrected"})

    merged_df = pd.merge(stations_we_care_about,df_gps_reduced_col_1 , on='tsCorrected', how='inner')


    return merged_df


def generate_antenna_station_calib_file(data_dataframe,station_of_interest,antenna,ref_lat,ref_long,ref_alt):

    station_dataframe = data_dataframe[data_dataframe.recvDeployName==station_of_interest]
    antenna_dataframe = station_dataframe[station_dataframe.port == antenna]





    return None