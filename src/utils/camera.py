import subprocess
import os
import time
import cv2
import numpy as np

from utils.logging_utils import configure_logging

# Configure logging
logger = configure_logging()

def capture_image(output_dir):
    """
    Captures an image using the camera and saves it to the specified output directory.
    Parameters:
        output_dir (str): The directory where the captured image will be saved.
    Returns:
        str: The path to the captured image (with timestamp as name) if successful, None otherwise.
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        image_path = os.path.join(output_dir,timestamp + '.jpg')
        image_name= os.path.basename(image_path)

        # Command to capture image using libcamera-still
        capture_command = f"libcamera-still -o {image_path}"

        #Execute the command
        subprocess.run(capture_command, shell=True)

        # Log successful image capture at the INFO level
        logger.info(f"Image captured successfully: {image_name}")

        # Return the path to the captured image file
        return image_path
    except Exception as e:
        # Log the error at the ERROR level
        logger.error(f"Error occurred while capturing image '{image_name}': {e}")
        return None
    
def preprocess_image(image_path):
    """
    Preprocesses the captured image for object detection. Extract a Region of interest and masked to perform detection only on the parking lot
    Parameters:
        image_path (str): The path to the captured image.
    Returns:
        numpy.ndarray: The preprocessed image as a NumPy array (OpenCV format) if successful, None otherwise
    """
    try:
        if image_path is None:
            raise ValueError("Image path '{image_path}' is None. Unable to preprocess image.")
        
        image = cv2.imread(image_path)

        #rectangle Roi 4608,2592                        
        roi_X,roi_Y = 1230, 1375
        roi_W,roi_H = 1920, 1080                                                #Roi W and H keep original ratio
        #extract roi from image
        roi=image[roi_Y:roi_Y+roi_H,roi_X:roi_X+roi_W]                      

        #Polygon cordinates for original_roi 783x440
        x1, y1 = 24, 446
        x2, y2 = 1199, 200
        x3, y3 = 1677, 290
        x4, y4 = 1873, 611
        x5, y5 = 1465, 795
        x6, y6 = 730, 738

        # Define the polygon-shaped mask
        mask = np.zeros((roi_H, roi_W), dtype=np.uint8)
        roi_points = np.array([[x1, y1], [x2, y2], [x3, y3],[x4, y4],[x5, y5], [x6, y6]] , dtype=np.int32)  # Define your triangle points
        cv2.fillPoly(mask, [roi_points], 255)
        
        #Apply the mask to the frame
        masked_frame = cv2.bitwise_and(roi, roi, mask=mask)

        return masked_frame
    except Exception as e:
        image_name= os.path.basename(image_path)
        # Log the error
        logger.error(f"Error occurred during image '{image_name}' preprocessing: {e}")
        return None