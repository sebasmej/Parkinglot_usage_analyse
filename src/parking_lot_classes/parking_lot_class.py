# Posible improvements: In populate_detections method: read comment in line 149

import sys
import os
import copy
from datetime import datetime
import time
# Add the 'utils' directory to the Python path
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils"))
parking_lot_classes_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "parking_lot_classes"))
sys.path.append(utils_path)
sys.path.append(parking_lot_classes_path)
from parking_spot_class import ParkingSpot
from compare_bbox import find_match_detection
from logging_utils import configure_logging


# Configure logging
logger = configure_logging()

# Define global constant for invalid parking spots
INVALID_SPOTS_IDS = ['A9', 'A16', 'C9', 'C16', 'E9', 'E16', 'G9']

def biggest_score_detection(det_record):
    return max(det_record, key=lambda det: float(det[5]))

def lowest_score_detection(det_record):
    return min(det_record, key=lambda det: float(det[5]))

class ParkingLot:
    def __init__(self):
        self.columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.rows = {
            'A': range(1, 24),
            'B': range(1, 24),
            'C': range(1, 24),
            'D': range(1, 24),
            'E': range(1, 22),
            'F': range(1, 19),
            'G': range(3, 16),
            'H': range(5, 12)
        }
        self.bicycles_count = 0
        self.motorcycle_count = 0
        self.parking_spots = self.create_parking_spots()
        self.parking_lot_map = []

#----------------------------------------------------------------- Methods to populate detections and tracking instances ------------------------------------------------------------
        
    #Create the parking spots objects and assign the their spot id based on sel.columns and self.rows
    def create_parking_spots(self):
        parking_spots = []
        for col in self.columns:
            for row in self.rows[col]:
                spot_id = f"{col}{row}"
                parking_spot = ParkingSpot(spot_id)
                parking_spots.append(parking_spot)

        return parking_spots

    # Loads the parking lot map coordinates from a file.
    def populate_coordinates_from_file(self, filename):
        """
        Loads the parking lot map coordinates from a file. the coordinates are in yolo format the first column correspond to the parking lot id/label and the next four columns are the bbox coordinates
        Parameters:
            map_file (str): The path to the file containing parking lot map coordinates.
        Returns:
            list: A list of tuples, each tuple containing the coordinates of a parking spot.
        """
        with open(filename, 'r') as file:
            parking_lot_map = []
            lines = file.readlines()
            for line in lines:
                values = line.split()
                spot_id = values[0]
                coordinates = [float(coord) for coord in values[1:]]
                element = [spot_id] + coordinates
                parking_lot_map.append(element)
                spot = self.get_spot_by_id(spot_id)
                if spot:
                    spot.coordinates = tuple(coordinates)
                else:
                    # If the spot_id was not found, means that the map_file have different ids and need to be modify to correspond
                    logger.error(f"The id: {spot_id}, was not found in the parking lot class please check the map file to ensure the ids match")
            self.parking_lot_map = parking_lot_map

    def get_spot_by_id(self, spot_id):
        for spot in self.parking_spots:
            if spot.spot_id == spot_id:
                return spot
        return None

    def populate_detections(self, detections,RECORD_LENGHT, det_timestamp, iou_threshold =0.1, ):
        """
        - Populates parking spots with detections. 
        - This method iterates over the given list of detections and assigns each detection to the corresponding parking spot based on its spatial proximity (iou).
        - Also manages cases where two or more detections are assigned to the same parking spot (duplicates) in this case the detection with higher IOU will be assigned to the parking spot and the other one will be disregarded
        - if the detection is not founD in the map or not surpases the IoU threshold, than the detection will be disregard.
        Parameters:
        - detections (list): A list of detections to be assigned to parking spots.
        """
        iou_list = []
        # Make a deep copy of lists
        pending_detections = copy.deepcopy(detections)                                                                                                                                                                     
        for detection in pending_detections:
            if detection:
                # Match the detection with the Spot with the highst IoU (returns the matched spot coordinates and the IoU between the spot and the detection)
                max_iou, matched_coordinates = find_match_detection(detection, self.parking_lot_map)

                # If a match was found
                if matched_coordinates:
                    # This list is for testing and debugging it prints the detections, the matchend spot_id and the IoU between them (this help to choose the IoU threshold)
                    iou_list.append((max_iou, detection, matched_coordinates[0]))  

                    # Search for the sppot object using the spot_id  (matched_coordinates[0] = spot_id, matched_coordinates[rest] =  spot coordinates)
                    matched_spot = self.get_spot_by_id(matched_coordinates[0])

                    # If a spot object was found (almost always true)
                    if matched_spot:
                        
                        # If the IoU between detection and matched spot is lower than the threshold than the detection is an error
                        # This will normally not happen, because the parking lot is almost completely map so the detection will always be assign to a spot, but sometimes in the border of the screen a error detection is found, this hav a small IoU and is disregarded
                        if max_iou >= iou_threshold:
                            # Skip processing for invalid spots (detection errors)
                            #if matched_spot.spot_id in INVALID_SPOTS_IDS:   # Fors testing i am still population this invalid spots to see if some correct detection is being assig to this invalid spots, once this is proove include this part again in the code to save execution time
                                #continue
                            #matched Spot. 

                            if len(matched_spot.det_record) == 0:
                                #Timestamp for knowing when the spot was first occupied
                                matched_spot.det_time = det_timestamp           
                            
                            if not matched_spot.is_current:
                                #Add detection to the Spot det record
                                matched_spot.det_record.append(detection)
                                # mark the spot as current
                                matched_spot.is_current = True

                                if len(matched_spot.det_record) > RECORD_LENGHT:
                                    # Erase the worst detection from the detection list to mainting the fixed detection record lenght
                                    worst_detection = lowest_score_detection(matched_spot.det_record)
                                    matched_spot.det_record.remove(worst_detection)
                            else:
                                # If Spot was already marked as current it means that a second detection was matched to the same Spot (duplicate) 
                                # the detection with highst score will be added to the record and the duplicate will be erased
                                # here there is posibilities to improve the assigment process: 
                                # instead of disregard the detection, check first both confidence scores, if both are high than assign the second detection to the second best matching spot. instead of disregarding it.
                                # during testing i saw that good scoring detection were being disregard so this improvement will solve that
                                best_detection = biggest_score_detection((detection,matched_spot.det_record[-1]))
                                matched_spot.det_record[-1] = best_detection
                        else:
                            # Matched spot IoU not hight as threshold. Detection is probably an error detection
                            logger.info(f"No matching spot: IoU {max_iou} Spot_id: {matched_spot.spot_id} detection: {detection}")   
                    else: 
                        # If spotis not found by ID report error. This error is unlikely to happen
                        logger.error(f"No parking spot found for ID: {matched_coordinates[0]}")         
                else: 
                    # No matched spot. Detection is in the parking lot but not in a spot. Create new parking spot with special identifier "i"
                    logger.info(f"No matching parking spot found for detection: {detection}")     
          
        print("iou_list: ", iou_list)
                               
    def update_spot_occupancy(self, RECORD_LENGHT, det_timestamp):
        """
        - Updates the occupancy status of parking spots based on current and previous detections (tracking). It updates the 'is_occupied' attribute of each spot accordingly.
        - it also disregard detections assigned to the invalid parking spots
        - it update the parking lot bicycle and motorcycle count
        """
        for spot in self.parking_spots:
            # Skip processing for invalid spots
            if spot.spot_id in INVALID_SPOTS_IDS:
                continue

            #If a detection was currently matched with a spot
            if spot.is_current:
                # If the record lenght is equal to the RECORD_LENGHT, than the detections assigned to this spot are consistent, and the spot is marked as occupied
                if len(spot.det_record) == RECORD_LENGHT:
                    # The instance is consistent detected across the det record
                    spot.is_occupied = True
                    spot.best_detection = biggest_score_detection(spot.det_record)

            # If the spot was not currentl matched with a detection
            else:
                # if no detection was found for the spot but the det record is not empty, than erase one entry of the det record (the worst). 
                if not len(spot.det_record) == 0:
                    worst_detection = lowest_score_detection(spot.det_record)
                    spot.det_record.remove(worst_detection)

                    # If the det record is empty after erasing one entry, than the instance is constantly gone, and can be mark as not occupied
                    if len(spot.det_record) == 0:
                        spot.best_detection = None
                        if spot.is_occupied:
                            spot.is_occupied = False

                            # average_occupation duration calculation
                            start_time = time.mktime(time.strptime(spot.det_time, "%Y-%m-%d_%H-%M-%S"))
                            end_time = time.mktime(time.strptime(det_timestamp, "%Y-%m-%d_%H-%M-%S"))
                            #print("start_time: ", start_time, " end_time: ", end_time)
                            # Calculate duration in seconds
                            duration_seconds = end_time - start_time
                            if spot.average_occupation == 0:
                                spot.average_occupation = duration_seconds
                            else:
                                spot.average_occupation = (spot.average_occupation + duration_seconds) / 2
                        spot.det_time = None
            
            # This is just for testing and debugging, it prints the spots were some change was done
            if spot.is_current or len(spot.det_record) > 0:
                print(f"Spot ID: {spot.spot_id}")
                print(f"det_record: {spot.det_record}")
                print(f"best_detection: {spot.best_detection}")
                print(f"Is Occupied: {spot.is_occupied}")
                print(f"det_time: {spot.det_time}")
                print("-" * 20)  # Separator between spots 
            spot.is_current = False

#----------------------------------------------------------------- Get methods ---------------------------------------------------------------------------------------
    
    def get_occupied_spots(self):
        occupied_spots = []
        for spot in self.parking_spots:
            if spot.is_occupied:
                occupied_spots.append(spot)
        return occupied_spots

    def get_occupied_spots_ids(self):
        occupied_spots = [[],[]]
        for spot in self.parking_spots:
            if spot.is_occupied:
                if int(spot.best_detection[5]) == 0:
                    occupied_spots[0].append(spot.spot_id)
                elif int(spot.best_detection[5]) == 1:
                    occupied_spots[1].append(spot.spot_id)
        return occupied_spots
    
    def get_occupied_spots_best_detections(self):
        occupied_spots_moto = []
        occupied_spots_bike = []
        for spot in self.parking_spots:
            if spot.is_occupied:
                if int(spot.best_detection[5]) == 0:
                    occupied_spots_bike.append(spot.best_detection)
                elif int(spot.best_detection[5]) == 1:
                    occupied_spots_moto.append(spot.best_detection)
                
        return occupied_spots_bike, occupied_spots_moto

    # Just for Test and debugg. method print all parking spots on the parking lot
    def print_parking_spots(self, parking_spots):
        for spot in parking_spots:
            print(f"Spot ID: {spot.spot_id}")
            #print(f"Coordinates: {spot.coordinates}")
            print(f"det_record: {spot.det_record}")
            print(f"best_detection: {spot.best_detection}")
            print(f"Is Occupied: {spot.is_occupied}")
            #print(f"Neighbors: {spot.neighbors}")
            print("-" * 20)  # Separator between spots



def load_detection_from_file(map_file): 
    """
    Loads the parking lot map coordinates from a file. the coordinates are in yolo format the first column correspond to the parking lot id/label and the next four columns are the bbox coordinates
    Parameters:
        map_file (str): The path to the file containing parking lot map coordinates.
    Returns:
        list: A list of tuples, each tuple containing the coordinates of a parking spot.
    """
    parking_lot_map = []
    with open(map_file, 'r') as file:
        lines = file.readlines()

        for line in lines:
            values = line.split()
            parking_lot_map.append(values)

    return detections

# For testing and development the skript can be run from console being this the start point in that case
if __name__ == "__main__":
    detections = load_detection_from_file(r"C:\T3100\raspberry_vnc_transfers\images_det\bbox_labels\2024-02-15_14-57-24.txt")

    #Initialize
    parking_lot = ParkingLot()
    parking_lot.populate_coordinates_from_file(r"C:\T3100\Projects\Parkinglot_usage_analyse\data\parking_lot_map.txt")

    parking_lot.populate_detections(detections)

    parking_lot.update_spot_occupancy()
