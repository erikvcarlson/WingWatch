from ipyleaflet import Map,Marker,basemaps
from ipywidgets import Layout  
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_widget  
from shiny.types import FileInfo
from WingWatch.Equipment import station,antenna
from WingWatch.Intersections import tri
from WingWatch.Tools import point_check as pc
from WingWatch.Intersections.detection import Detection
import pandas as pd
import sys
import pickle
import os
import time
import glob
import logging
import numpy as np


logger = logging.getLogger(__name__)
logging.basicConfig(filename='/home/app/example.log', encoding='utf-8', level=logging.DEBUG)



"""class MyObject:
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def __repr__(self):
        return f"MyObject(param1={self.param1}, param2={self.param2})"
"""

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card("Data Input"),
        ui.card(
            ui.card_header("Map"),
            output_widget("map")
        ),
        ui.card(
            ui.card_header("Detection Generator"),
            ui.input_select("select_stat_det_1", "Station 1",choices = list(glob.glob('*.pkl'))),
            ui.input_select("select_ant_det_1", "Antenna Number",choices = [1,2,3,4,5]),
            ui.input_numeric("stat_1_strength","Strength of Station 1 Detection",0),
            ui.input_select("select_stat_det_2", "Station 2",choices = list(glob.glob('*.pkl'))),
            ui.input_select("select_ant_det_2", "Antenna Number",choices = [1,2,3,4,5]),
            ui.input_numeric("stat_2_strength","Strength of Station 2 Detection",0),
            ui.input_select("select_stat_det_3", "Station 3",choices = list(glob.glob('*.pkl'))),
            ui.input_select("select_ant_det_3", "Antenna Number",choices = [1,2,3,4,5]),
            ui.input_numeric("stat_3_strength","Strength of Station 3 Detection",0),
            ui.input_task_button("Detect", "Go!"),
        ),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Station Creation Terminal"),
            ui.input_text("station_name", "Name of Station", "Station Name"),
            ui.input_numeric("lat_val_stat", "Latitude", 41, min=-90, max=90),
            ui.input_numeric("long_val_stat", "Longitude", -71, min=-180, max=180),
            ui.input_task_button("generate_station", "Generate"),
            ui.input_select("select_stat", "Select a Station",choices = list(glob.glob('*.pkl'))),
            ui.input_numeric("ant_name","Antenna Number",1,min=1),
            ui.input_file("pattern_entry","CSV for Pattern",accept='.csv'),
            ui.input_task_button("Assign_Pattern", "Assign Pattern"),
        ),
        ui.card("Map Properties and Layer Control"),
        ui.card("Tesserlation Visualizer")
    ),
)  

def server(input, output, session):
    @render_widget  
    def map():
        return Map(
        basemap=basemaps.Esri.WorldImagery,
        center=(41, -71),
        zoom=5,
        layout=Layout(width='500px', height='500px')
    ) 

    @ui.bind_task_button(button_id="generate_station")
    @reactive.extended_task
    async def write_station_out(stationName,latValStat,longValStat):
        Station_1 = station.Station(stationName,latValStat,longValStat)
        save_object_to_disk(Station_1,'/home/app/' + Station_1.name + '.pkl')
    

    @reactive.effect
    @reactive.event(input.generate_station, ignore_none=False)
    def handle_click():
        write_station_out(input.station_name(),float(input.lat_val_stat()),float(input.long_val_stat()))
        time.sleep(1)
        # Get a list of all *.pkl files
        file_list = glob.glob('*.pkl')
        # Remove the .pkl extension from each file name
        file_list_no_ext = [file[:-4] for file in file_list]

        ui.update_select("select_stat",choices = file_list_no_ext)
        ui.update_select("select_stat_det_1",choices = file_list_no_ext)
        ui.update_select("select_stat_det_2",choices = file_list_no_ext)
        ui.update_select("select_stat_det_3",choices = file_list_no_ext)



    @ui.bind_task_button(button_id="Assign_Pattern")
    @reactive.extended_task
    async def update_station_class(name,ant_number,pattern):
        try:
            
            name = str(name) + '.pkl'
            ant_number = int(ant_number)
            pattern = pd.read_csv(pattern)        
            Station_1 = load_object_from_disk(name)
            a1 = antenna.Antenna(ant_number,'test',0,0)
            a1.assign_pattern(pattern)
            Station_1.add_antenna(a1)
            save_object_to_disk(Station_1,'/home/app/' + Station_1.name + '.pkl')
        except Exception as err: 
            # logger.debug(type(name))
            # logger.debug(type(ant_number))
            # logger.debug(type(pattern))
            logger.error(err)

    @reactive.effect
    @reactive.event(input.Assign_Pattern, ignore_none=False)
    def handle_click():
        try:
            file: list[FileInfo] | None = input.pattern_entry()
            update_station_class(input.select_stat(), input.ant_name(), file[0]["datapath"])
            time.sleep(1)
        except Exception as err:
            logger.error(err)


    @ui.bind_task_button(button_id="Detect")
    @reactive.extended_task
    async def calc_intersect():
        try:
            logger.info("Loading Stations")
            nameStat1 = input.select_stat_det_1() + '.pkl'
            nameStat2 = input.select_stat_det_2() + '.pkl'
            nameStat3 = input.select_stat_det_3() + '.pkl'
            
            Station_1 = load_object_from_disk(nameStat1)
            Station_2 = load_object_from_disk(nameStat2)
            Station_3 = load_object_from_disk(nameStat3)
            logger.info("Stations Loaded Successfully")

            strength_1 = float(input.stat_1_strength())
            strength_2 = float(input.stat_2_strength())
            strength_3 = float(input.stat_3_strength())

            antenna_number_1 = input.select_ant_det_1()
            antenna_number_2 = input.select_ant_det_2()
            antenna_number_3 = input.select_ant_det_3()
            logger.info("Other variables saved successfully")

            det1 = Detection(Station_1,strength_1,antenna_number_1)
            det2 = Detection(Station_2,strength_2,antenna_number_2)
            det3 = Detection(Station_3,strength_3,antenna_number_3)

            logger.info("Detections Generated")
            data_to_send_through = [det1,det2,det3]

            intersections,hull_of_intersections = tri.overlap_of_three_radiation_patterns(data_to_send_through)

            pc.point_in_hull(np.array([293,211,27]),hull_of_intersections)

            logger.info("Function Completed Successfully")
        except Exception as err:
            logger.error(err)



    ##helper functions

    def save_object_to_disk(obj, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(obj, file)

    def load_object_from_disk(file_path):
        with open(file_path, 'rb') as file:
            return pickle.load(file)


app = App(app_ui, server)