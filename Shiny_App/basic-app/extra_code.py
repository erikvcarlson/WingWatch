            for key in keys:
                try:
                    logger.info(f"Processing key: {key}")

                    # Load the station data from IndexedDB
                    await load_from_indexeddb(key)

                    logger.info(f"Processing your mom's key.")
                    logger.info('Attempting to Grab Value')
                    await asyncio.sleep(1)
                    logger.info(f'Value is {input.loaded_value.get()}')
                    # Wait until `loaded_value` updates
                    while input.loaded_value.get() is None:
                        await asyncio.sleep(0.1)
                        logger.info(f"Yo mamma's so fat...")

                    # Process the loaded value
                    process_loaded_value(input.loaded_value.get())

                    await asyncio.sleep(0.1)  # Small delay to allow the next loop iteration

                except Exception as err:
                    logger.exception(f"Error during key processing:")
        logger.info("Entered load_singular_station_for_map")




        try:
            if input.loaded_value() is not [None]:
                Station = json.loads(input.loaded_value())
                logger.info(f"Loaded station data: {Station}")
                point = [Station['name'], Station['lat'], Station['long']]
                logger.info("Point for map generated")    
                fig = fig_store.get()
                logger.info("Retrived active map")
                fig.add_trace(px.scatter_mapbox(lat=[Station['lat']],lon=[Station['long']],hovertext=[Station['name']]).data[0])
                logger.info("Added Station Point")          
                # Update the stored figure
                fig_store.set(fig)
                logger.info('Updated Figure; Map should run next')
                try:
                    keys_for_loading = keys_for_loading[1:]
                except:
                    pass
        except Exception as err:
            logger.error(f"Error in load_singular_station_for_map: {err}")









    @reactive.calc
    def callForStationtoLoadMap():
        logger.info('Calling for a station to be loaded')
        try:
            with reactive.isolate():
                if input.loaded_value.get() is not None:
                    Station = json.loads(input.loaded_value())
                    logger.info(f"Loaded station data: {Station}")
                logger.info('Station Called; Should be heading to load_singular_station_for_map next')
        except:
            logger.exception('callForStationtoLoadMap Traceback: ')
        return Station

    @reactive.effect()
    @reactive.event(input.all_keys)
    async def load_singular_station_for_map(ignore_init = False):
        logger.info('Load Singular_Station_Called')
        for key in input.all_keys():
            logger.info(f'In Loop. The value of the key is: {key}')
            await load_from_indexeddb(key)
            asyncio.wait(0.1)            
            callForStationtoLoadMap()
