from compare_bbox import find_match_detection

invalid_parking_spots = [('A9', 0.305729166666667, 0.425, 0.0260416666666667, 0.0787037037037037),
                         ('A16', 0.458333333333333, 0.310185185185185, 0.0260416666666667, 0.0787037037037037),
                         ('C9', 0.427083333333333, 0.449074074074074, 0.0260416666666667, 0.0694444444444444),
                         ('C16', 0.585416666666667, 0.319444444444444, 0.0260416666666667, 0.0601851851851852),
                         ('E9', 0.577083333333333, 0.467592592592593, 0.0260416666666667, 0.0925925925925926),
                         ('E16', 0.738541666666667, 0.328703703703704, 0.0260416666666667, 0.087962962962963),
                         ('G7', 0.758854166666667, 0.472222222222222, 0.0338541666666667, 0.138888888888889)]

def load_parking_lot_map(map_file): 
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

    return parking_lot_map

def print_dict(my_dict):
    for key, value in my_dict.items():
        print(f"key: {key}")
        print("value:", value)
        print("---")

def print_list(my_list):
    for item in my_list:
        print(item)

def compare_detections_with_map(validated_detections, map_file_path = r"C:\T3100\Projects\Parkinglot_usage_analyse\data\parking_lot_map.txt"):
    """
    Compares the validated detections with the parking lot map.
    Parameters:
        validated_detections (dict): A list of validated detections.
        parking_lot_map (list): A list of tuples containing the coordinates of parking spots.
    Returns:
        dict: A dictionary mapping each instance to the parking spot with the highest IoU.
    """
    parking_lot_map = load_parking_lot_map(map_file_path)
    matching_parking_spots = {}
    duplicate_parking_spots = {}
    detection_and_matched_spot = []

    #Find the matching parking spot and append it to matching_parking_spots or duplicate_parking_spots
    for detection in validated_detections:
        hole_detection = []
        #print(parking_lot_map)
        iou, matched_detection = find_match_detection(detection, parking_lot_map)
        if matched_detection is not None:
            #detection_and_matched_spot.append([detection, matched_detection])
            if matched_detection[0] in matching_parking_spots:
                duplicate_parking_spots[matched_detection[0]] = [matched_detection, iou, detection ]
            else:
                matching_parking_spots[matched_detection[0]] = [matched_detection, iou, detection ]

    """print("matching_parking_spots: ")
    print_list(matching_parking_spots)
    print("duplicate_parking_spots: ")
    print_list(duplicate_parking_spots)  """

    #search for the duplicated with higher Iou and swap es on the matching_parking_spots and duplicate_parking_spots lists
    for id_duplicate, duplicate in duplicate_parking_spots.items():
        for id_spot, parking_spot in matching_parking_spots.items():
            if id_duplicate == id_spot:
                if duplicate[1] > parking_spot[1]:
                    duplicate_parking_spots[id_duplicate] = parking_spot
                    matching_parking_spots[id_spot] = duplicate
                    parking_lot_map.remove(duplicate[0][:5])
                else:
                    parking_lot_map.remove(parking_spot[0][:5])

    # Look for the second higher iou parking spots for duplicates and add it to matching_parking_spots
    for id_duplicate, duplicate in duplicate_parking_spots.items():
        iou, matched_detection = find_match_detection(duplicate[2], parking_lot_map)
        if matched_detection is not None:
            matching_parking_spots[matched_detection[0]] = [matched_detection, iou, duplicate]

    #populating valid results
    validated_results = []
    for _, parking_spot in matching_parking_spots.items():
        validated_results.append(parking_spot[0])

    #deliting invalid parking spots
    for parking_spot in validated_results:
        for invalid_spot in invalid_parking_spots:
            if parking_spot[0] == invalid_spot[0]:
                validated_results.remove(parking_spot)
        
    print("removed_results: ")
    print_list(validated_results)
    return validated_results

    """
    to do: 
    si la bbox_det es muy grande y cubre dos parqueaderos entonces anular la detection, no se como hacer esto
    """

validated_detections = load_parking_lot_map(r"C:\T3100\raspberry_vnc_transfers\images_det\bbox_labels\2024-02-15_14-49-49.txt")
matching_parking_spots = compare_detections_with_map(validated_detections)