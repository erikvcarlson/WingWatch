from ipyleaflet import Map, basemaps
from ipywidgets import Layout  
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_widget  
from WingWatch.Equipment import station, antenna
from WingWatch.Intersections import tri
from WingWatch.Tools import point_check as pc
from WingWatch.Intersections.detection import Detection
import pandas as pd
import os
import time
import glob
import logging
import numpy as np
import pickle
import shutil
from fastapi import FastAPI, Request, Response
from starlette.middleware.sessions import SessionMiddleware
import uuid
import threading

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(filename='/home/app/example.log', encoding='utf-8', level=logging.DEBUG)

# FastAPI app with session management middleware
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Constants
MAX_AGE = 30 * 24 * 60 * 60  # 30 days in seconds

# Utility Functions
def generate_session_id():
    """Generate a unique session ID."""
    return str(uuid.uuid4())

def get_session_id(request: Request, response: Response):
    """Retrieve or generate a session ID and store it in a cookie."""
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = generate_session_id()
        response.set_cookie(key='session_id', value=session_id, max_age=MAX_AGE, httponly=True)
    return session_id

def get_temp_dir(session_id):
    """Create or return the temp directory for a session."""
    temp_dir = f'/tmp/{session_id}/'
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir

def save_object_to_disk(obj, file_path):
    """Save an object to disk using pickle."""
    with open(file_path, 'wb') as file:
        pickle.dump(obj, file)

def load_object_from_disk(file_path):
    """Load an object from disk using pickle."""
    with open(file_path, 'rb') as file:
        return pickle.load(file)

def save_user_data(obj, session_id, filename):
    """Save user data to a session-specific temp directory."""
    temp_dir = get_temp_dir(session_id)
    file_path = os.path.join(temp_dir, filename)
    save_object_to_disk(obj, file_path)

def cleanup_temp_dir():
    """Clean up temp directories older than 30 days."""
    current_time = time.time()
    for dirpath, dirnames, _ in os.walk('/tmp/'):
        for dirname in dirnames:
            dir_full_path = os.path.join(dirpath, dirname)
            if os.path.isdir(dir_full_path):
                creation_time = os.path.getctime(dir_full_path)
                if current_time - creation_time > MAX_AGE:
                    shutil.rmtree(dir_full_path)
                    logger.info(f"Removed old directory: {dir_full_path}")

def schedule_cleanup():
    """Schedule the cleanup task to run daily."""
    while True:
        cleanup_temp_dir()
        time.sleep(24 * 60 * 60)  # Sleep for one day

# Shiny app UI
app_ui = ui.page_fluid(
    ui.layout_columns(
        ui.card("Data Input"),
        ui.card(ui.card_header("Map"), output_widget("map")),
        ui.card(
            ui.card_header("Detection Generator"),
            ui.input_select("select_stat_det_1", "Station 1", choices=list(glob.glob('*.pkl'))),
            ui.input_select("select_ant_det_1", "Antenna Number", choices=[1, 2, 3, 4, 5]),
            ui.input_numeric("stat_1_strength", "Strength of Station 1 Detection", 0),
            ui.input_select("select_stat_det_2", "Station 2", choices=list(glob.glob('*.pkl'))),
            ui.input_select("select_ant_det_2", "Antenna Number", choices=[1, 2, 3, 4, 5]),
            ui.input_numeric("stat_2_strength", "Strength of Station 2 Detection", 0),
            ui.input_select("select_stat_det_3", "Station 3", choices=list(glob.glob('*.pkl'))),
            ui.input_select("select_ant_det_3", "Antenna Number", choices=[1, 2, 3, 4, 5]),
            ui.input_numeric("stat_3_strength", "Strength of Station 3 Detection", 0),
            ui.input_task_button("Detect", "Go!")
        ),
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Station Creation Terminal"),
            ui.input_text("station_name", "Name of Station", "Station Name"),
            ui.input_numeric("lat_val_stat", "Latitude", 41, min=-90, max=90),
            ui.input_numeric("long_val_stat", "Longitude", -71, min=-180, max=180),
            ui.input_task_button("generate_station", "Generate"),
            ui.input_select("select_stat", "Select a Station", choices=list(glob.glob('*.pkl'))),
            ui.input_numeric("ant_name", "Antenna Number", 1, min=1),
            ui.input_file("pattern_entry", "CSV for Pattern", accept='.csv'),
            ui.input_task_button("Assign_Pattern", "Assign Pattern")
        ),
        ui.card("Map Properties and Layer Control"),
        ui.card("Tesserlation Visualizer")
    ),
)

# Shiny app server logic
def server(input, output, session):
    session_id = get_session_id(session.request, session.response)

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
    async def write_station_out(stationName, latValStat, longValStat):
        Station_1 = station.Station(stationName, latValStat, longValStat)
        filename = f'{Station_1.name}.pkl'
        save_user_data(Station_1, session_id, filename)

    @reactive.effect
    @reactive.event(input.generate_station, ignore_none=False)
    def handle_click():
        write_station_out(input.station_name(), float(input.lat_val_stat()), float(input.long_val_stat()))
        time.sleep(1)
        file_list = glob.glob('*.pkl')
        file_list_no_ext = [file[:-4] for file in file_list]
        ui.update_select("select_stat", choices=file_list_no_ext)
        ui.update_select("select_stat_det_1", choices=file_list_no_ext)
        ui.update_select("select_stat_det_2", choices=file_list_no_ext)
        ui.update_select("select_stat_det_3", choices=file_list_no_ext)

    @ui.bind_task_button(button_id="Assign_Pattern")
    @reactive.extended_task
    async def update_station_class(name, ant_number, pattern):
        try:
            name = f'{name}.pkl'
            ant_number = int(ant_number)
            pattern = pd.read_csv(pattern)
            Station_1 = load_object_from_disk(name)
            a1 = antenna.Antenna(ant_number, 'test', 0, 0)
            a1.assign_pattern(pattern)
            Station_1.add_antenna(a1)
            save_object_to_disk(Station_1, f'/home/app/{Station_1.name}.pkl')
            logger.info(f"A new pattern was assigned to {Station_1.name}")
        except Exception as err:
            logger.error(err)

    @reactive.effect
    @reactive.event(input.Assign_Pattern, ignore_none=False)
    def handle_click():
        try:
            file = input.pattern_entry()[0]["datapath"]
            update_station_class(input.select_stat(), input.ant_name(), file)
            time.sleep(1)
        except Exception as err:
            logger.error(err)

    @ui.bind_task_button(button_id="Detect")
    @reactive.extended_task
    async def calc_intersect(select_stat_det_1_str, select_stat_det_2_str, select_stat_det_3_str,
                             stat_1_strength_float, stat_2_strength_float, stat_3_strength_float,
                             select_ant_det_1_int, select_ant_det_2_int, select_ant_det_3_int):
        try:
            logger.info("Loading Stations")
            Station_1 = load_object_from_disk(f'{select_stat_det_1_str}.pkl')
            Station_2 = load_object_from_disk(f'{select_stat_det_2_str}.pkl')
            Station_3 = load_object_from_disk(f'{select_stat_det_3_str}.pkl')
            logger.info("Stations Loaded Successfully")

            det1 = Detection(Station_1, float(stat_1_strength_float), int(select_ant_det_1_int) - 1)
            det2 = Detection(Station_2, float(stat_2_strength_float), int(select_ant_det_2_int) - 1)
            det3 = Detection(Station_3, float(stat_3_strength_float), int(select_ant_det_3_int) - 1)

            data_to_send_through = [det1, det2, det3]
            intersections, hull_of_intersections = tri.overlap_of_three_radiation_patterns(data_to_send_through)
            logger.info("Hull of Intersections Generated")
            pc.point_in_hull(np.array([293, 211, 27]), hull_of_intersections)
            logger.info("Function Completed Successfully")
        except Exception as err:
            logger.error(err)

# FastAPI integration
@app.get("/")
async def main(request: Request, response: Response):
    session_id = get_session_id(request, response)
    # Shiny App
    shiny_app = App(app_ui, server)
    shiny_app.server.session['session_id'] = session_id
    return {"message": "Session ID passed to Shiny", "session_id": session_id}

# Start cleanup in a separate thread
cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
cleanup_thread.start()


