from ipyleaflet import Map,Marker,basemaps
from ipywidgets import Layout  
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_widget  

app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card(),
        ui.layout_columns(
            
            ui.card(
            ui.card_header("Map Properties"),
            ui.input_numeric("lat_val", "Latitude", 41, min=-90, max=90),
            ui.input_numeric("long_val", "Longitude", -71, min=-180, max=180),
            ui.input_numeric("zoom_val", "Zoom", 5, min=1, max=12),
            ),
            ui.card(
                ui.card_header("Generate a New Station"),
                ui.input_numeric("new_stat_lat_val", "Latitude", 40, min=-90, max=90),
                ui.input_numeric("new_stat_long_val", "Longitude", 70, min=-180, max=180),
                ui.input_action_button("gen_stat", "Generate")  
            ),
        ),

        output_widget("map")
    )
)  

def server(input, output, session):
    @render_widget  
    def map():
        return Map(
        basemap=basemaps.Esri.WorldImagery,
        center=(input.lat_val(), input.long_val()),
        zoom=input.zoom_val(),
        layout=Layout(width='80%', height='500px')
    ) 
     
 
    # # @reactive.event(input.gen_stat)
    # # def _():
    # #     ui.notification_show(
    # #         "This text will disappear after 2 seconds.",
    # #         duration=2,
    # #     )
    # @reactive.effect
    # @reactive.event(input.gen_stat)
    # def _():
    #     loc = (input.new_stat_lat_val,input.new_stat_long_val)
    #     update_marker(map.widget, loc)

    # #helper function
    # def update_marker(map: Map, loc: tuple):
    #     map.add_layer(Marker(location=loc, draggable=False))

app = App(app_ui, server)