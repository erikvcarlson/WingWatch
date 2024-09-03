from ipyleaflet import Map,Marker,basemaps
from ipywidgets import Layout  
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_widget  
from WingWatch.Equipment import station,antenna
import pandas as pd
import sys
import pickle
import os
import time
import glob


class MyObject:
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def __repr__(self):
        return f"MyObject(param1={self.param1}, param2={self.param2})"


app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card("Data Input"),
        ui.card(
            ui.card_header("Map"),
            output_widget("map")
        ),
        ui.card(
            ui.card_header("Detection Generator"),
            ui.input_select("select_stat_det", "Select a Station",choices = list(glob.glob('*.pkl'))),
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
        ui.update_select("select_stat_det",choices = file_list_no_ext)



    @ui.bind_task_button(button_id="Assign_Pattern")
    @reactive.extended_task
    async def update_station_class(name,ant_number,pattern):
        
        name = str(name) + '.pkl'
        os.system('echo ' + name + '>> debug_file.txt')
        ant_number = int(ant_number)
        os.system('echo ' + str(ant_number) + '>> debug_file.txt')
        pattern = pd.read_csv(pattern)
        os.system('echo "pattern read in" >> debug_file.txt')
        Station_1 = load_object_from_disk(name)
        a1 = antenna.Antenna(ant_number,'test',0,0)
        a1.assign_pattern(pattern)
        Station_1.add_antenna(a1)
        save_object_to_disk(Station_1,'/home/app/' + Station_1.name + '_updated.pkl')


    @reactive.effect
    @reactive.event(input.Assign_Pattern, ignore_none=False)
    def handle_click():
        update_station_class(input.select_stat(), input.ant_name(),input.pattern_entry())
        time.sleep(1)
          
    ##helper functions

    def save_object_to_disk(obj, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(obj, file)

    def load_object_from_disk(file_path):
        with open(file_path, 'rb') as file:
            return pickle.load(file)


app = App(app_ui, server)