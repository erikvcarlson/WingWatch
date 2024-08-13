from ipyleaflet import Map,Marker,basemaps
from ipywidgets import Layout  
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_widget  
from WingWatch.Equipment import station
import sys

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card("Data Input"),
        ui.card(
            ui.card_header("Map"),
            output_widget("map")
        ),
        ui.card("Detection Generator"),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Station Creation Terminal"),
            ui.input_text("station_name", "Name of Station", ""),
            ui.input_numeric("lat_val_stat", "Latitude", 41, min=-90, max=90),
            ui.input_numeric("long_val_stat", "Longitude", -71, min=-180, max=180),
            ui.input_action_button("generate_station", "Generate")
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

    @reactive.calc
    def generate_station():
        Station_1 = station.Station(input.station_name,input.lat_val_stat,input.long_val_stat)
        sys.stdout.write('Station Created ' + str(Station_1.name))
        return Station_1

app = App(app_ui, server)