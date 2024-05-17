#To do:
# -Test the application on real time fotos to find the best performant configuration of Recor_lenght and CAPTURE_INTERVAL. While doing this look for posible improvements to the parking lot class to enhance accuaracy. 
# - To look for the best performant configuration is only needed to change the RECORD_LENGHT global variable, the CAPTURE_INTERVAL will be automatically modified, so the report latency is always 15 min.
# - Posible improvements can be: Sometimes two detections in the same Frame are matched with the same parking spot. Right now the 2 detections are count as a duplicate of the same instace,
# so the system keeps only the better scoring detection and the other one is disregarded. But sometimes this detections are actually two different instances in two different spots close to each other, 
# so one detection is going missed. This can be improve by checking the score of the disregarded detection and if is confiable add this detection to the second best ioU matching parking spot, what is highly probably the correct spot 
# - Database improvemnt: Change the database to one that supports web applications, and change the databse structur. Currently only occupied spots are store in the database, this works with local database and the actual local UI. 
# But it´ll be better and more complete to save the hole parking spots list in the database. This is easy to do, but the the data analysis methods will need to properly modified.
# - Web dashboard: With a proper database, a web UI can be implementet without changing the system pipeline. The changes will be regarding the database insert and retrive methods, 
# and off course the data analisis methods that are based in the data base information and structur

import os
import time
import threading
from utils.camera import capture_image, preprocess_image
from object_detection.detection import perform_object_detection, draw_bounding_box
from object_detection.tracking import simple_tracking, consistency_tracking
from parking_lot_classes.parking_lot_class import ParkingLot
from database.database import *
from database.data_analysis import count_instances_per_timestamp
import cv2
import time
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

RECORD_LENGHT = 2                       #Change this to try different RECORD_LENGHT (n), and APTURE_INTERVAL (f) configrtations  [n=2 f=15; n=3 f=7.5; n=4 f=5; ... ]

if RECORD_LENGHT == 1:
    CAPTURE_INTERVAL = (15)(60)
elif not (1 <= RECORD_LENGHT <= 10):
    CAPTURE_INTERVAL = ((15)(60))/((RECORD_LENGHT-1))

# Function to analyze photos in real-time
def analyze_real_time_photos(parking_lot, image_dir):
    """
        - Funtion executes the system pipeline:
          1. Take real Time foto 
          2. Preproccces the image
          3. Perform object detection
          4. Perform tracking (Associate detection with parking lot map and performe tracking of occupied spots)
          5. Save current occupied spots into database  
        Parameters:
        - parking_lot (Object): A parking lot object containing the list of parking spots
        - image_dir (path): Path to temporary save the taken foto (it will be shortly after erased)
    """
    
    #Always running loop
    while True:
        # Start time to take execution time of one Frame
        start_time = time.time()   

        # Method to capture image returns image Path. Method located at "root/src/utils/camera.py"  
        image_path = capture_image(output_dir=image_dir)
        image_name = os.path.basename(image_path)
        image_timestamp = os.path.splitext(image_name)[0]
        
        # if an image has been successfully taken
        if image_path is not None:
            # Preprocess the captured image. Method located at "root/src/utils/camera.py"  
            preprocessed_image = preprocess_image(image_path)
            
            # if the image has been successfully edited
            if preprocessed_image is not None:
                # Perform object detection on the preprocessed image. Method located at "root/src/object_detection/detection.py"
                detections = perform_object_detection(preprocessed_image)
                print("detections", detections) 
                print("---")

                # Delete the captured image to ensure anonymity
                os.remove(image_path)

                # Assign detections, Populate the spots with the corresponding detection. Method located at "root/src/parking_lot_classes/parking_lot_class.py"
                parking_lot.populate_detections(detections, RECORD_LENGHT, image_timestamp)

                # Update the parking spots status, performing tracking with consistency check. Method located at "root/src/parking_lot_classes/parking_lot_class.py"
                parking_lot.update_spot_occupancy(RECORD_LENGHT, image_timestamp)

                #Get occupied spots to upload to the local database (SQLite)
                occupied_spots = parking_lot.get_occupied_spots()

                # Insert each occupied spot into the database
                for spot in occupied_spots:
                    spot_id = spot.spot_id
                    occupancy_status = spot.best_detection[0]                               #0 for occupied by bicycle,1 for occupied by Motorcycle
                    occupied_timestamp = spot.det_time
                    average_occupation_duration = spot.average_occupation
                    score = spot.best_detection[5]

                    # Insert the occupied spot into the database
                    insert_occupied_spot(spot_id, image_timestamp, occupancy_status, occupied_timestamp, average_occupation_duration, score)
                
                # This is for testing. Gets the best detection found for each ocuppied parking spot, than draw the detection-bboxes on the cv2-image and save it in the results folder.
                # This allow to visually see the detection results after tracking
                occupied_spots_bike, occupied_spots_moto = parking_lot.get_occupied_spots_best_detections()
                draw_bounding_box(preprocessed_image,occupied_spots_bike,os.path.join(ROOT_DIR, 'results', 'det_sample', image_name))
                
                # Calculate execution time
                execution_time = time.time() - start_time 
                print("image_name: ", image_name, "execution_time: ", execution_time)
                print("-" * 20)  

        time.sleep(CAPTURE_INTERVAL)


# Function to analyze a dictionary of pre-existing photos
def analyze_pre_existing_photos(parking_lot, image_dir):
    """
        - executes the system pipeline on existing photos (used during development):
          1. loops through each existing photo
          2. Preproccces the image
          3. Perform object detection
          4. Perform tracking (Associate detection with parking lot map and performe tracking of occupied spots)
          5. Save current occupied spots into database  
        Parameters:
        - parking_lot (Object): A parking lot object containing the list of parking spots
        - image_dir (path): Path to the existen fotos folder
    """
    #Loading pictures
    files = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

    #to take a sample of the preprocesing image  (for testing)
    save_preprocess_sample = True

    for file_name in files:
        # Start time to take execution time of one Frame
        start_time = time.time()  

        #Getting image path
        file_path = os.path.join(image_dir, file_name)
        file_timestamp = file_name[:-4]

        # Preprocess the captured image. Method located at "root/src/utils/camera.py"
        preprocessed_image = preprocess_image(file_path)

        # if the image has been successfully edited
        if preprocessed_image is not None:  
            #just for test porpuses. Save a sample of the preprocessed image on the result folder
            if save_preprocess_sample == True:
                cv2.imwrite(os.path.join(ROOT_DIR, 'results', 'preprocessed_image.jpg'), preprocessed_image)
                save_preprocess_sample = False
            
            # Perform object detection on the preprocessed image. Method located at "root/src/object_detection/detection.py"
            detections = perform_object_detection(preprocessed_image)
            print("detections", detections)
            print("---")
            
            # Assign detections, Populate the spots with the corresponding detection. Method located at "root/src/parking_lot_classes/parking_lot_class.py"
            parking_lot.populate_detections(detections, RECORD_LENGHT, file_timestamp)
            
            # Update the parking spots status, performing tracking with consistency check. Method located at "root/src/parking_lot_classes/parking_lot_class.py"
            parking_lot.update_spot_occupancy(RECORD_LENGHT,file_timestamp)

            
            current_timestamp = file_timestamp
            #Get occupied spots to upload to the local database (SQLite)
            occupied_spots = parking_lot.get_occupied_spots()
            # Insert each occupied spot into the database
            for spot in occupied_spots:
                spot_id = spot.spot_id
                occupancy_status = spot.best_detection[0]                               #0 for occupied by bicycle and 1 for occupied by Motorcycle
                occupied_timestamp = spot.det_time
                average_occupation_duration = spot.average_occupation
                score = spot.best_detection[5]

                # Insert the occupied spot into the database
                insert_occupied_spot(spot_id, current_timestamp, occupancy_status, occupied_timestamp, average_occupation_duration, score)

            # This is for testing. Gets the best detection found for each ocuppied parking spot, than draw the detection-bboxes on the cv2-image and save it in the results folder.
            # This allow to visually see the detection results after tracking
            occupied_spots_bike, occupied_spots_moto = parking_lot.get_occupied_spots_best_detections()
            draw_bounding_box(preprocessed_image,occupied_spots_bike,os.path.join(ROOT_DIR, 'results', 'det_sample', file_name))
            

            # Calculate execution time
            execution_time = time.time() - start_time 
            print("image_name: ", file_timestamp, "execution_time: ", execution_time)
            print("-" * 20)  


def main(take_photos=True):
    """
        - initialize Database parking lot class and calls the desire function of the system 
        Parameters:
        - take_photos (Boolean): True, to analize real time fotos. False, to analize already existent fotos
    """
    # Initialize the parking lot
    parking_lot = ParkingLot()

    # Populate coordinates from the parking lot map file
    map_file_path = os.path.join(ROOT_DIR,"data","parking_lot_map.txt")
    parking_lot.populate_coordinates_from_file(map_file_path)
    #print("Map: ",parking_lot.parking_lot_map )

    # Create the database if doesnt already exits
    create_database()

    # Now start the main pipeline
    if take_photos:
        # Define output directory for captured images
        image_dir = os.path.join(ROOT_DIR, "data")
        analyze_real_time_photos(parking_lot, image_dir)
    else:
        # Define images input directory
        image_dir = os.path.join(ROOT_DIR, "data", "images","29-02-2024")
        analyze_pre_existing_photos(parking_lot, image_dir)

# Entry point of the script
if __name__ == "__main__":
    main(take_photos=False)