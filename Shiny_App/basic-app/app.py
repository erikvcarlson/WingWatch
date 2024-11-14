from ipyleaflet import Map, basemaps, Marker, Circle
from ipywidgets import Layout  
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_widget  
from WingWatch.Equipment import station, antenna
from WingWatch.Intersections import tri
from WingWatch.Tools import point_check as pc
from WingWatch.Intersections.detection import Detection
from WingWatch.Tools import translation
import WingWatch.Tools.spheres as sph
import pandas as pd
import os
import time
import glob
import logging
import numpy as np
import pickle
import shutil
import scipy.spatial as ss

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(filename='/home/app/example.log', encoding='utf-8', level=logging.DEBUG)


# Shiny app UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_numeric("user", "User Number", 1000, min=1000, max=9999),
        ui.input_task_button("user_select", "Go!"),      
        open="closed", 
        bg="#f8f8f8",    
        ),
    ui.layout_columns(
            ui.card(
            ui.card_header("Station Creation Terminal"),
            ui.input_text("station_name", "Name of Station", "Station Name"),
            ui.input_numeric("lat_val_stat", "Latitude", 41, min=-90, max=90),
            ui.input_numeric("long_val_stat", "Longitude", -71, min=-180, max=180),
            ui.input_task_button("generate_station", "Generate"),
            ui.input_select("select_stat", "Select a Station", choices=list()),
            ui.input_numeric("ant_name", "Antenna Number", 1, min=1),
            ui.input_file("pattern_entry", "CSV for Pattern", accept='.csv'),
            ui.input_task_button("Assign_Pattern", "Assign Pattern")
        ),
        ui.card(ui.card_header("Map"), output_widget("map")),
        ui.card(
            ui.card_header("Detection Generator"),
            ui.input_select("select_stat_det_1", "Station 1", choices=list()),
            ui.input_select("select_ant_det_1", "Antenna Number", choices=[1, 2, 3, 4, 5]),
            ui.input_numeric("stat_1_strength", "Strength of Station 1 Detection", 0),
            ui.input_select("select_stat_det_2", "Station 2", choices=list()),
            ui.input_select("select_ant_det_2", "Antenna Number", choices=[1, 2, 3, 4, 5]),
            ui.input_numeric("stat_2_strength", "Strength of Station 2 Detection", 0),
            ui.input_select("select_stat_det_3", "Station 3", choices=list()),
            ui.input_select("select_ant_det_3", "Antenna Number", choices=[1, 2, 3, 4, 5]),
            ui.input_numeric("stat_3_strength", "Strength of Station 3 Detection", 0),
            ui.input_task_button("Detect", "Go!")
        ),
    ),
    ui.layout_columns(
        ui.card("Data Input"),
        ui.card("Map Properties and Layer Control"),
        ui.card("Tesserlation Visualizer")
    ),
)

# Shiny app server logic
def server(input,output,session):
    
    user_working_dir = reactive.value()

    @reactive.effect
    def startup_modal():
        # Define the modal with a dismiss button
        logger.info('Showed Modal Message')
        ui.modal_show(
            ui.modal(
                ui.input_action_button("close_modal","Close"),
                ui.p('You are using a random user. If you would like to use a known user, use the user selection tool on the right.'),
                title="Welcome!",
                easy_close=True,
                footer=None
            )
        )

    @reactive.effect
    @reactive.event(input.close_modal)
    def startup_fn():
        ui.modal_remove()
        # Code to execute on startup
        user = np.random.randint(10000, 11000)
        
        new_dir = f'/tmp/users/{user}/'
        user_working_dir.set(new_dir)
        
        # Create directory if it doesn't exist
        if not os.path.exists(user_working_dir.get()):
            os.makedirs(user_working_dir.get())
            
        # Reactive output to provide choices for input_select based on user_working_dir
        stations_long = glob.glob(user_working_dir.get() + '*.pkl')
        stations = [os.path.splitext(os.path.basename(file))[0] for file in stations_long]
        time.sleep(1)
        logger.info('Directory Function Ran on Start-up')
        logger.info('Start-up Script Ran')
        logger.info(f'The current user directory is: {user_working_dir.get()}')


    # Function to handle user button click (user_select)
    @reactive.effect
    @reactive.event(input.user_select)  # React to button click
    def update_user_directory():
        # Get user input
        user = input.user()
       
        new_dir = f'/tmp/users/{user}/'
        user_working_dir.set(new_dir)
        
        # Create directory if it doesn't exist
        if not os.path.exists(user_working_dir.get()):
            os.makedirs(user_working_dir.get())
            
        # Reactive output to provide choices for input_select based on user_working_dir

        file_list =  glob.glob(user_working_dir.get() +'*.pkl')
        file_list_no_ext = [os.path.splitext(os.path.basename(file))[0] for file in file_list]
        ui.update_select("select_stat", choices=file_list_no_ext)
        ui.update_select("select_stat_det_1", choices=file_list_no_ext)
        ui.update_select("select_stat_det_2", choices=file_list_no_ext)
        ui.update_select("select_stat_det_3", choices=file_list_no_ext)


        time.sleep(1)
        logger.info('Directory Function Ran')

    @render_widget
    def map():
        m = Map(
            basemap=basemaps.Esri.WorldImagery,
            center=(41, -71),
            zoom=5,
            layout=Layout(width='500px', height='500px')
        )

        return m

    #@ui.bind_task_button()
    #@reactive.effect
    #@reactive.event(input.generate_station)
    @reactive.effect
    @reactive.event(input.generate_station, ignore_none=False,ignore_init= True)
    def handle_click():
        logger.info('The Station Generation Button was Clicked.')
        logger.info(f'The working directory for station generation is: {user_working_dir.get()}')

        write_station_out(input.station_name(), float(input.lat_val_stat()), float(input.long_val_stat()),user_working_dir.get())
        time.sleep(1)
        m = map.widget
        point = Marker(location=(input.lat_val_stat(), input.long_val_stat()), draggable=False)     
        m.add_layer(point)  
        file_list =  glob.glob(user_working_dir.get() +'*.pkl')
        file_list_no_ext = [os.path.splitext(os.path.basename(file))[0] for file in file_list]
        ui.update_select("select_stat", choices=file_list_no_ext)
        ui.update_select("select_stat_det_1", choices=file_list_no_ext)
        ui.update_select("select_stat_det_2", choices=file_list_no_ext)
        ui.update_select("select_stat_det_3", choices=file_list_no_ext)

    @reactive.effect
    @reactive.event(input.Assign_Pattern, ignore_none=False,ignore_init= True)
    def handle_click_assign_pattern():
        try:
            logger.info('Initialized the Assigning Pattern')
            file = input.pattern_entry()[0]["datapath"]
            name = user_working_dir.get() + f'{input.select_stat()}.pkl'
            ant_number = int(input.ant_name())
            pattern = pd.read_csv(file)
            Station_1 = load_object_from_disk(name)
            a1 = antenna.Antenna(ant_number, 'test', 0, 0)
            a1.assign_pattern(pattern)
            Station_1.add_antenna(a1)
            save_object_to_disk(Station_1, f'{user_working_dir.get()}{Station_1.name}.pkl')
            logger.info(f"A new pattern was assigned to {Station_1.name}")
        except Exception as err:
            logger.error(err)

        time.sleep(1)


    @reactive.effect
    @reactive.event(input.Detect, ignore_none=False,ignore_init= True)
    def calc_intersect():
        try:
            logger.info("Loading Stations")
            Station_1 = load_object_from_disk(user_working_dir.get() + f'{input.select_stat_det_1.get()}.pkl')
            Station_2 = load_object_from_disk(user_working_dir.get() + f'{input.select_stat_det_2.get()}.pkl')
            Station_3 = load_object_from_disk(user_working_dir.get() + f'{input.select_stat_det_3.get()}.pkl')
            logger.info("Stations Loaded Successfully")

            det1 = Detection(Station_1, float(input.stat_1_strength.get()), int(input.select_ant_det_1.get()) - 1)
            det2 = Detection(Station_2, float(input.stat_2_strength.get()), int(input.select_ant_det_2.get()) - 1)
            det3 = Detection(Station_3, float(input.stat_3_strength.get()), int(input.select_ant_det_3.get()) - 1)

            data_to_send_through = [det1, det2, det3]
            intersections, hull_of_intersections = tri.overlap_of_three_radiation_patterns(data_to_send_through)
            logger.info("Hull of Intersections Generated")

            V = ss.ConvexHull(hull_of_intersections.points)
            radius = sph.find_radius_from_vol(V.volume)

            logger.info("Radius of Volume Approximated")

            cx = np.mean(hull_of_intersections.points[hull_of_intersections.vertices,0])
            cy = np.mean(hull_of_intersections.points[hull_of_intersections.vertices,1])
            cz = np.mean(hull_of_intersections.points[hull_of_intersections.vertices,2])

            logger.info("Center of Hull Found")

            Detection_pos = translation.convert_back_to_lla([cx,cy,cz],Station_1.lat,Station_1.long,Station_1.alt)

            logger.info("Ready to Draw the Circle")

            circle = Circle()
            logger.info('Circle Initialized')
            circle.location = (Detection_pos[0],Detection_pos[1])
            logger.info("Position Assigned")
            
            circle.radius = int(radius)

            logger.info("Circle Given Radius")

            circle.color = "green"
            circle.fill_color = "green"

            m = map.widget
            m.add(circle)
            
            pc.point_in_hull(np.array([293, 211, 27]), hull_of_intersections)
            logger.info("Function Completed Successfully")
        except Exception as err:
            logger.error(err)


    @session.on_ended
    def cleanup():
        for dir_path in "/tmp/users/":
            # Ensure we only delete directories in the expected range
            if "/tmp/users/" in dir_path and "10000" <= dir_path.split('/')[-2] < "11000":
                try:
                    shutil.rmtree(dir_path)
                    print(f"Deleted directory: {dir_path}")
                except OSError as e:
                    print(f"Error deleting directory {dir_path}: {e}")

#helper function
def save_object_to_disk(obj, file_path):
    """Save an object to disk using pickle."""
    with open(file_path, 'wb') as file:
        pickle.dump(obj, file)

def load_object_from_disk(file_path):
    """Load an object from disk using pickle."""
    with open(file_path, 'rb') as file:
        return pickle.load(file)

def write_station_out(stationName, latValStat, longValStat,working_dir):
        logger.info('Intializing Station Function')
        logger.info(f'Station Parameters are;Station Name  = {stationName}, Lat = {latValStat}, Long = {longValStat}')
        Station_1 = station.Station(stationName, latValStat, longValStat)
        logger.info("Station Generated.")
        try:
            logger.info(f'Current Working Directory: {working_dir}')
        except Exception as err:
            logger.error(err)

        filename = working_dir + f'{Station_1.name}.pkl'
        save_object_to_disk(Station_1, filename)


app = App(app_ui,server)