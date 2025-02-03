#from ipyleaflet import Map, basemaps, Marker, Circle,MarkerCluster
#from ipywidgets import Layout  
import plotly.express as px

from shiny import App, reactive, ui,render
from shinywidgets import output_widget, render_widget  
from shinywidgets import render_plotly
from WingWatch.Equipment import station, antenna
from WingWatch.Intersections import tri
from WingWatch.Tools import point_check as pc
from WingWatch.Intersections.detection import Detection
from WingWatch.Tools import translation
import WingWatch.Tools.spheres as sph
from WingWatch.Equipment import antenna as ant
import pandas as pd
import os
import time
import glob
import logging
import numpy as np
import pickle
import shutil
import scipy.spatial as ss
import base64
import json 
import asyncio 
import traceback

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(filename='/home/app/example.log', encoding='utf-8', level=logging.DEBUG)
lock = asyncio.Lock()

# Shiny app UI
app_ui = ui.page_fluid(
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
    ui.output_ui("handle_click"),
    ui.HTML("""
    <script>
    // Initialize IndexedDB
    const dbName = "RFShinyApp";
    const storeName = "StationInformation";

    function initDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(dbName, 1);
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(storeName)) {
                    db.createObjectStore(storeName, { keyPath: "key" });
                }
            };
            request.onsuccess = (event) => resolve(event.target.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }

    async function saveToDB(key, value) {
        const db = await initDB();
        const tx = db.transaction(storeName, "readwrite");
        const store = tx.objectStore(storeName);
        store.put({ key, value });
        return tx.complete;
    }

    async function loadFromDB(key) {
        const db = await initDB();
        const tx = db.transaction(storeName, "readonly");
        const store = tx.objectStore(storeName);
        return new Promise((resolve, reject) => {
            const request = store.get(key);
            request.onsuccess = () => resolve(request.result ? request.result.value : null);
            request.onerror = () => reject(request.error);
        });
    }

    async function listAllKeys() {
        const db = await initDB();
        const tx = db.transaction(storeName, "readonly");
        const store = tx.objectStore(storeName);
        return new Promise((resolve, reject) => {
            const keys = [];
            const request = store.openCursor();
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    keys.push(cursor.key);
                    cursor.continue();
                } else {
                    resolve(keys); // Resolve when the cursor is done
                }
            };
            request.onerror = (event) => reject(event.target.error);
        });
    }


    // Listen for Shiny messages
    Shiny.addCustomMessageHandler("save_to_indexeddb", async (message) => {
        await saveToDB(message.key, message.value);
        Shiny.setInputValue("save_status", "success");
    });

    Shiny.addCustomMessageHandler("load_from_indexeddb", async (message) => {
        try {
            const value = await loadFromDB(message.key);
            console.log("Loaded value from IndexedDB:", value); // Add this log
            Shiny.setInputValue("loaded_value", value, {priority: "event"});
        } catch (error) {
            console.error("Error loading from IndexedDB:", error); // Add error logging
            Shiny.setInputValue("loaded_value", null);
        }
    });

    Shiny.addCustomMessageHandler("list_keys", async (message) => {
        const keys = await listAllKeys();
        Shiny.setInputValue("all_keys", keys); // Send the list of keys to Shiny
    });

    </script>
    """),
)
# Shiny app server logic
def server(input,output,session):
    markers = reactive.value([])

    @reactive.effect
    async def startup_fn():
        await session.send_custom_message("list_keys", {})
        asyncio.sleep(0.1)
        logger.info("Triggered list_keys message handler in JavaScript")
        time.sleep(1)
        logger.info('Start-up Script Ran')
        
    @reactive.effect
    @reactive.event(input.all_keys)
    async def handle_list_keys():
        try:
            keys = input.all_keys()  # Retrieve the list of keys from IndexedDB
            logger.info(f"Retrieved keys from IndexedDB: {keys}")
            ui.update_select("select_stat", choices=keys)
            ui.update_select("select_stat_det_1", choices=keys)
            ui.update_select("select_stat_det_2", choices=keys)
            ui.update_select("select_stat_det_3", choices=keys)
            for key in keys:
                try:
                    logger.info(f"Processing key: {key}")

                    # Load the station data from IndexedDB
                    await load_from_indexeddb(key)

                    logger.info(f"Processing your mom's key.")
                    logger.info('Attempting to Grab Value')
                    logger.info(f'Value is {input.loaded_value.get()}')
                    # Wait until `loaded_value` updates
                    while input.loaded_value.get() is None:
                        await asyncio.sleep(0.1)
                        logger.info(f"Yo mamma's so fat...")

                    # Process the loaded value
                    process_loaded_value(input.loaded_value.get())

                    await asyncio.sleep(0.1)  # Small delay to allow the next loop iteration

                except Exception as err:
                    logger.error(f"Error during key processing: {err}")

        except Exception as outer_err:
            logger.error(f"Error in handle_list_keys: {outer_err}")
        
        logger.info('handle_list_keys function is complete.')
    

    # Use reactive context for loaded_value
    #@reactive.effect
    #@reactive.event(input.loaded_value)  # Make loaded_value reactive
    def process_loaded_value(loaded_value):
        """Processes the loaded station data."""
        logger.info("Entered process_loaded_value")
        try:
            if loaded_value is not None:
                Station = json.loads(loaded_value)
                logger.info(f"Loaded station data: {Station}")
                point = [Station['name'], Station['lat'], Station['long']]
                logger.info('Point for map generated')
                
                logger.info('Requesting markers value')
                current_markers = markers.get()

                logger.info(f'Markers Value Retrieved in process_loaded_value. The value is: {current_markers}')
                
                current_markers.append(point)  # Append new point
                markers.set(current_markers)

                logger.info(f'Markers Value after update: {current_markers}')
            else:
                logger.warning("Loaded value is None.")
        except Exception as err:
            logger.error(f"Error in process_loaded_value: {err}")


    @render_plotly
    @reactive.event(markers)
    def map():
        logger.info("Markers have changed, updating the map.")
        logger.info(f"The value of markers is: {markers.get()}") 
        if markers.get() != []:
            # Create a DataFrame with markers data
            df = pd.DataFrame(markers.get(), columns=['Name', 'Lat', 'Long'])
            fig = px.scatter_mapbox(
                df,
                lat="Lat",
                lon="Long",
                hover_name='Name',
                zoom=10
            )
            logger.info(f"Map updated with {len(markers.get())} markers.")
        else:
            # Create an empty DataFrame
            df = pd.DataFrame(columns=['Name', 'Lat', 'Long'])
            fig = px.scatter_mapbox(
                df,
                lat="Lat",
                lon="Long",
                hover_name="Name",
                zoom=9,
                center={"lat": 41, "lon": -71}
            )
            logger.info("Map updated with no markers (default center 41, -71).")
        
        # Set Mapbox token
        fig.update_layout(mapbox_style="open-street-map") 
        return fig

    
    @reactive.effect
    @reactive.event(input.generate_station, ignore_none=False,ignore_init= True)
    async def handle_click():
        #time.sleep(1)
        logger.info('The Station Generation Button was Clicked.')
                 
        logger.info('Intializing Station Function')
        logger.info(f'Station Parameters are;Station Name  = {input.station_name()}, Lat = {input.lat_val_stat()}, Long = {input.long_val_stat()}')
        Station_1 = station.Station(input.station_name(), float(input.lat_val_stat()), float(input.long_val_stat()))
        logger.info("Station Generated.")
        
        jsonstr1 = json.dumps(Station_1.__dict__) 
        
        logger.info("Station converted to JSON.")

        key = input.station_name()
        value = jsonstr1

        await save_to_indexeddb(key,value)
        await session.send_custom_message("list_keys", {})

        logger.info("Station Saved")
        time.sleep(1)

    @reactive.effect
    @reactive.event(input.Assign_Pattern, ignore_none=False,ignore_init= True)
    async def handle_click_assign_pattern():
        try:
            logger.info('Initialized the Assigning Pattern')
            file = input.pattern_entry()[0]["datapath"]
            #name = user_working_dir.get() + f'{input.select_stat()}.pkl'
            ant_number = int(input.ant_name())
            pattern = pd.read_csv(file)
            
            load_from_indexeddb(input.select_stat())
            
            Station_JSON = input.loaded_value()
            
            if not Station_JSON:
                logger.error(f"No data found for station: {key}")
                return

            station_data = json.loads(Station_JSON)

            # Recreate the Station object
            Station_1 = station.Station(name=station_data['name'],lat=station_data['lat'],long=station_data['long'],alt = station_data['alt'],antennas = station_data['antennas']) 

            asyncio.sleep(0.1)

            a1 = antenna.Antenna(ant_number, 'test', 0, 0)
            a1.assign_pattern(pattern)

            
            Station_1.add_antenna(a1)

            #we can't nest objects with indexeddb. To get around this, we will store each antenna as a string 
            for i in range(len(Station_1.antennas)): 
                if not isinstance(Station_1.antennas[i], str):
                    Station_1.antennas[i] = object_to_base64_string(Station_1.antennas[i])
        
            jsonstr1 = json.dumps(Station_1.__dict__) 
        
            logger.info("Station converted to JSON.")

            key = input.station_name()
            value = jsonstr1

            await save_to_indexeddb(key,value)
            asyncio.sleep(0.1)
            await session.send_custom_message("list_keys", {})
            asyncio.sleep(0.1)

            logger.info("Station Saved")
            logger.info(f"A new pattern was assigned to {Station_1.name}")

        except Exception as err:
            logger.error(err)

        time.sleep(1)

    @reactive.effect
    @reactive.event(input.Detect, ignore_none=False,ignore_init= True)
    def calc_intersect():
        try:
            logger.info("Loading Station 1")

            Station_1 = generate_station_object(input.select_stat_det_1.get())
            logger.info("Done Loading Station 1")
            logger.info("Loading Station 2 ")
            Station_2 = generate_station_object(input.select_stat_det_2.get())
            logger.info("Done Loading Station 2")
            logger.info("Loading Station 3")
            Station_3 = generate_station_object(input.select_stat_det_3.get())
            logger.info("Done Loading Station 3")
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

            # circle = Circle()
            # logger.info('Circle Initialized')
            # circle.location = (Detection_pos[0],Detection_pos[1])
            # logger.info("Position Assigned")
            
            # circle.radius = int(radius)

            # logger.info("Circle Given Radius")

            # circle.color = "green"
            # circle.fill_color = "green"

            # m = map.widget
            # m.add(circle)
            
            # pc.point_in_hull(np.array([293, 211, 27]), hull_of_intersections)
            # logger.info("Function Completed Successfully")
        except Exception as err:
            logger.error(err)

    async def save_to_indexeddb(key,value):
        await session.send_custom_message("save_to_indexeddb", {"key": key, "value": value})

    async def load_from_indexeddb(key):
        await session.send_custom_message("load_from_indexeddb", {"key": key})

    async def generate_station_object(name):
        load_from_indexeddb(input.select_stat_det_1.get())

        Station_JSON = input.loaded_value()

        if not Station_JSON:
            logger.error(f"No data found for station: {name}")
            return

        station_data = json.loads(Station_JSON)

        # Recreate the Station object
        Station_1 = station.Station(name=station_data['name'],lat=station_data['lat'],long=station_data['long'],alt = station_data['alt'],antennas = station_data['antennas']) 


        for i in range(len(Station_1.antennas)): 
            if not isinstance(Station_1.antennas[i], str):
                Station_1.antennas[i] = base64_string_to_object(Station_1.antennas[i])

        return Station_1


def object_to_base64_string(obj):
    """
    Converts a Python object to a Base64-encoded string via pickle serialization.
    
    Parameters:
        obj: The Python object to serialize.
    
    Returns:
        A Base64-encoded string representation of the object.
    """
    # Serialize the object to bytes using pickle
    pickle_bytes = pickle.dumps(obj)
    
    # Encode the bytes to a Base64 string
    base64_string = base64.b64encode(pickle_bytes).decode('utf-8')
    
    return base64_string


def base64_string_to_object(base64_string):
    """
    Converts a Base64-encoded string back to the original Python object via pickle deserialization.
    
    Parameters:
        base64_string: A Base64-encoded string representation of a serialized object.
    
    Returns:
        The deserialized Python object.
    """
    # Decode the Base64 string back to bytes
    pickle_bytes = base64.b64decode(base64_string)
    
    # Deserialize the bytes back to the original object
    obj = pickle.loads(pickle_bytes)
    
    return obj




app = App(app_ui,server)