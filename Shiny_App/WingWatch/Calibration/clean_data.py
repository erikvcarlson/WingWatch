import pandas as pd
import numpy as np
from WingWatch.Tools import translation

def clean_motus_Tag_data(data_csv:str,calibration_tags_list,start_date="",end_date=""):
    """
    args:
    data_csv: str; The filepath to the CSV file containing tag data. The 
    function assumes the CSV file uses commas (",") as the delimeter. 

    calibration_tags_list: list; A list of integers containing the Motus Tag ID #. Note this is NOT
    the manufacturer's ID number.  
    
    start_date: str; Not implemented yet. The start date (YYYY-MM-DD) of when the current station configuration started. 3
    Used when wanting to exclude data before a station was moved or upgraded to its current configuration.

    end_date: str; Not implemented yet. The end date (YYYY-MM-DD) of when the station left the configuration of question. 
    Used when wanting to exclude data after a station was moved or upgraded to a new configuration.
   

    returns:
    calibration_tags_only: pandas.DataFrame; A pandas dataframe containing the mostly cleaned tag data. The dataframe has the following 
    columns:
    
    tsCorrected: pandas.DateTime: Unix Epoch Time of the tag detection as taken from the station
    sig: int: The signal strength of the recieved tag detection. (dBm for CTT detections)
    port: int: The port number for which the detection was recieved. Incrementing starting at n=1
    motusTagID:int: The Motus Tag Id of the detected tag.
    mfgID: str: The manufacturer's tag id for the detected tag.

    """

    df_tags_uncleaned = pd.read_csv(data_csv,low_memory=False)

    df_tags_uncleaned['ts'] = pd.to_datetime(df_tags_uncleaned['ts'])
    df_tags_dated = df_tags_uncleaned[df_tags_uncleaned['ts'] < pd.to_datetime(end_date)]

    df_reduced_col = df_tags_dated[['tsCorrected','sig','port','recvDeployName','motusTagID','mfgID']]

    #recvDeployName is the human readable name of the reciever and recv is the serial number 

    df_with_station_detections = df_reduced_col.dropna(axis=0)

    calibration_tags_only = df_with_station_detections[df_with_station_detections['motusTagID'].isin(calibration_tags_list)]

    port_uncleaned = calibration_tags_only["port"].to_list()
    port_cleaned = [int(string[-1]) for string in port_uncleaned]
    calibration_tags_only['port'] = port_cleaned

    return calibration_tags_only


def clean_gps_data_csv(data_csv:str):
    """
    args:
    data_csv: str; The filepath to the CSV file containing GPS data. The 
    function assumes the CSV file uses commas (",") as the delimeter. 

    returns:
    df_gps_reduced_col: pandas.DataFrame; A pandas dataframe containing the
    cleaned GPS data. The dataframe has the following columns:

    Y: float: latitude of the GPS Point
    X: float: longitude of the GPS Point
    ele: float: The elevation (ASL) of the GPS point
    time:int: The timestamp of the GPS point in Unix Epoch in seconds (?)

    """

    df_gps_uncleaned = pd.read_csv(data_csv)

    df_gps_reduced_col = df_gps_uncleaned[["Y","X","ele","time"]]
    df_gps_reduced_col['time'] = pd.to_datetime(df_gps_reduced_col['time']).astype(int) / 10**9

    return df_gps_reduced_col


def merge_gps_and_tag_data(tag_data,gps_data,stations_of_interest:list):
    """
    args:
    tag_data: pandas.DataFrame; 

    gps_data: pandas.DataFrame;

    stations_of_interest: list; A list of strings containing the names of the stations as they exisit in the 
    recvDeployName column of the tag_data dataframe.

    returns:
    merged_df: pandas.DataFrame; A pandas dataframe containing the
    time-collated tag and GPS data. The dataframe has the following columns:

    #add the dataframe column ouputs here
    """


    
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
    """
    args:
    data_dataframe: pandas.DataFrame; Merged Cleaned Tag and Cleaned GPS dataframes

    station_of_interest: string;

    antenna: int; 

    ref_lat: float;

    ref_long: float;

    ref_alt: float; 

    returns:
    resultant_calibration_file: pandas.DataFrame;  

    #add the dataframe column ouputs here
    """



    station_dataframe = data_dataframe[data_dataframe.recvDeployName==station_of_interest]
    antenna_dataframe = station_dataframe[station_dataframe.port == antenna]
    result = antenna_dataframe.apply(lambda row: translation.XYZ_distance(ref_lat, ref_long, ref_alt, row['Y'], row['X'], row['ele']), axis=1)
    XYZ_dataframe = pd.DataFrame(result.to_list(),columns=['X','Y','Z'])
    XYZ_dataframe['RSSI'] = antenna_dataframe['sig'].to_list()

    resultant_calibration_file = XYZ_dataframe

    return resultant_calibration_file