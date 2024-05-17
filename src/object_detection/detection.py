import cv2
import numpy as np
import os
import time
from ultralytics import YOLO
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.logging_utils import configure_logging

models_root_dir = r"C:\T3100\Projects\Parkinglot_usage_analyse\models"

# Configure logging
logger = configure_logging()

#Method to convert bounding box coordinates to yolo format
def convert_to_yolo(bbox, image_width, image_height):
    # Extract coordinates
    x_min, y_min, x_max, y_max = bbox
    # Calculate box width, height, and center coordinates
    box_width = x_max - x_min
    box_height = y_max - y_min
    center_x = x_min + (box_width / 2)
    center_y = y_min + (box_height / 2)
    # Normalize coordinates between 0 and 1
    center_x /= image_width
    center_y /= image_height
    box_width /= image_width
    box_height /= image_height

    return center_x, center_y, box_width, box_height

def perform_object_detection(
    image,
    model_path= os.path.join(models_root_dir, 'yolov5n6_m1280_e70.pt'), 
    confidence_threshold=0.1,
    imgz=1280,
    iou_threshold = 0.3
):
    """
    Performs object detection on the input image and return the detection results
    Parameters:
        image: The input image as a NumPy array (OpenCV format)
    Returns:
        list of tuples: Each tuple represent a detection, containing the class ID, bbox coordinates in yolo format (x_center, y_center), box width, box height, and score.
    """
    try:
        start_time = time.time() 

        # Load a model
        model = YOLO(model_path) 

        img_height, img_width, _ = image.shape

        # Perform detection on the masked_frame
        results = model.predict(image,conf=confidence_threshold, iou = iou_threshold, imgsz=imgz)[0]              #[0] in the first elemnt is the boxes data results

        detection_results = []
        # Write one line for each detection
        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            center_x, center_y, box_width, box_height = convert_to_yolo((x1,y1,x2,y2),img_width,img_height)

            # Append the detection results to the list
            detection_results.append((int(class_id), center_x, center_y, box_width, box_height, score))
        
        detection_time = time.time() - start_time                   #To calculate Speed pro image

        # Log successful image capture at the INFO level
        logger.info(f"Detections performe successfully on image, detection time: {detection_time}")

        return detection_results
    except Exception as e:
        # Log the error at the ERROR level
        logger.error(f"Error occurred while performing detection on image: {e}")
        return None
    

def draw_bounding_box(image, detections, save_path):
    if detections:
        for detection in detections:
            if detection:
                category = int(detection[0])
                yolo_coords = list(map(float, detection[1:5]))

                image_height, image_width, _ = image.shape

                center_x, center_y, box_width, box_height = yolo_coords
                x_min = int((center_x - box_width / 2) * image_width)
                y_min = int((center_y - box_height / 2) * image_height)
                x_max = int((center_x + box_width / 2) * image_width)
                y_max = int((center_y + box_height / 2) * image_height)

                color = (0, 255, 0)  # default: green
                if category == 0:
                    color = (0, 0, 255)  # red
                elif category == 1:
                    color = (255, 0, 0)  # blue

                cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, 2)
    cv2.imwrite(save_path, image)

#just for testing
if __name__ == "__main__":
    image_dir = "C:\\T3100\\Projects\\Parkinglot_usage_analyse\\data\\images\\preprocessed_image.jpg"
    save_path = os.path.join("C:\T3100\Projects\Parkinglot_usage_analyse\data\images","detection_box_test.jpg")
    image = cv2.imread(image_dir)
    detections = [(0, 0.4371708869934082, 0.6258915653935185, 0.0465179443359375, 0.08762173122829861, 0.17621420323848724),
                  (0, 0.42473773956298827, 0.646580731427228, 0.10778293609619141, 0.13537428114149305, 0.11965024471282959)
                  ]

    draw_bounding_box(image,detections,save_path)

