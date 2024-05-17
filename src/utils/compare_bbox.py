def calculate_iou(bbox_detection, bbox_ground):
    """
    Calculate Intersection over Union (IoU) between two bounding boxes.
    Parameters:
    - box_: Tuple (x1, y1, width, height) representing the first bounding box.
    Returns:
    - iou: Intersection over Union (IoU) value.
    """
    # Extract coordinates from the bounding box tuples
    # Assuming these variables are initially stored as strings
    x1_str, y1_str, w1_str, h1_str = bbox_detection
    x2_str, y2_str, w2_str, h2_str = bbox_ground
    # Convert the string variables to floats
    x1, y1, w1, h1 = float(x1_str), float(y1_str), float(w1_str), float(h1_str)
    x2, y2, w2, h2 = float(x2_str), float(y2_str), float(w2_str), float(h2_str)
    # Calculate coordinates of intersection rectangle
    x1_iou = max(x1 , x2)
    y1_iou = max(y1, y2)
    x2_iou = min(x1+w1,x2+w2)
    y2_iou = min(y1+h1,y2+h2)
    
    # calculate width and height of the intersection rectangle
    w_iou = x2_iou - x1_iou
    h_iou = y2_iou - y1_iou
    # If there is no intersection -> iou=0
    if (w_iou <= 0) or (h_iou <= 0):
        iou_area = 0
    else:
        iou_area = w_iou * h_iou

    # Calculate areas of the bounding boxes and the intersection
    area_bbox_detections = w1 * h1
    area_bbox_truth = w2 * h2
    union_area = float(area_bbox_detections + area_bbox_truth - iou_area)
    # Calculate IoU
    iou = iou_area / union_area 

    #print("x1 :", x1, " x2: ",x2, " iou: ",iou, " w_iou: ",w_iou, " h_iou: ", h_iou)
    return iou  

def find_match_detection(det, image_detections):
    """
    compares a detection with a list of detections and find a match (a match is the detection with the higher iou)
    - if no match was found returns max_iou = 0 and matched_detection = None
    Parameters:
    det (tuple): (class_id, center_x, center_y, box_width, box_height, score).
    image_detections (tuple list): each tupple contains (class_id, center_x, center_y, box_width, box_height, score).
    Returns:
    - the matched detection and the corresponding iou.
    """
    # Compare the detections
    max_iou = 0
    matched_detection = None
    for detection in image_detections:
        iou = calculate_iou(det[1:5], detection[1:5])
        if iou > max_iou:
                max_iou = iou
                matched_detection = detection

    return max_iou, matched_detection

#Just for testing   
if __name__ == "__main__":
    det1= (0, 0.4371708869934082, 0.6258915653935185, 0.0465179443359375, 0.08762173122829861, 0.17621420323848724)
    det2= (0, 0.42473773956298827, 0.646580731427228, 0.10778293609619141, 0.13537428114149305, 0.11965024471282959)   
    print("iou: ", calculate_iou(det1[1:5], det2[1:5]))
