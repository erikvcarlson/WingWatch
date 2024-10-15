import streamlit as st
import st_local_storage
from WingWatch.Equipment import station, antenna
from WingWatch.Intersections import tri
from WingWatch.Tools import point_check as pc
from WingWatch.Intersections.detection import Detection


st_ls = st_local_storage.StLocalStorage()

try:
    station_list = st_ls['stationList']
    if station_list == None:
        raise TypeError
    st.write("Used Old Storage")
except:
    station_list = []
    st_ls['stationList'] = station_list
    st.write("Intialized Storage")

## Generate a Station

station_name = st.text_input("Station Name",value="Default Station",max_chars=50,key='name_stat')
latStat = st.number_input("Latitude of Station: ",min_value = -90, max_value= 90,value = 41,key='lat_stat')
longStat = st.number_input("Longitude of Station: ",min_value = -180, max_value= 180,value = -71,key='long_stat')
clicked = st.button("Generate")

if clicked == 1:
    stat1 = station.Station(station_name,latStat,longStat) 
    station_list.append(stat1)
    st.write("Success")


#key = st.text_input("Key")
#value = st.text_input("Value")
#if st.button("Save"):
#    st_ls[key] = value

#if st.button("Delete"):
#    del st_ls[key]

#if key:
#    f"Current value of {key} is:"
#    st.write(st_ls[key])