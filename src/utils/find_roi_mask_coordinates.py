import cv2
import os
import numpy as np

# Global variables to store original and resized image dimensions
original_width = 0
original_height = 0
rooth_path = r'C:\T3100\Projects\Parkinglot_usage_analyse'
# Function to display coordinates when mouse is clicked
def print_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        original_x = int(x * (original_width / 1280))
        original_y = int(y * (original_height / 720))
        print(f"Resized coordinates (x={x}, y={y}) | Original coordinates (x={original_x}, y={original_y})")

def find_roi_coord(image):
    # Resize the image to 1280x720
    resized_image = cv2.resize(image, (1280, 720))
    # Display the image
    display_image(resized_image)

def display_image(frame):
    # Display the image
    cv2.imshow('frame', frame)
    # Set the callback function for mouse events
    cv2.setMouseCallback('frame', print_coordinates)
    # Wait for a key press and close the window when any key is pressed
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Usage
if __name__ == "__main__":
    file_name = '2024-03-01_11-50-15'
    image_path = os.path.join(rooth_path, 'data', file_name + '.jpg')
    # Read an image
    image = cv2.imread(image_path)
    # Get the original image dimensions
    original_height, original_width = image.shape[:2]
    #find_roi_coord(image)                                            #Show the original image and allow to click and print the point-clicked coordinates
    #rectangle Roi 4608,2592                        
    roi_X,roi_Y = 1230, 1375
    roi_W,roi_H = 1920, 1080                                                #Roi W and H keep original ratio
    # Extract ROI from the original image
    roi = image[roi_Y:(roi_Y + roi_H), roi_X:(roi_X + roi_W)]    
    #display_image(roi)
    #Polygon cordinates for original_roi 783x440
    x1, y1 = 24, 446
    x2, y2 = 1199, 200
    x3, y3 = 1677, 290
    x4, y4 = 1873, 611
    x5, y5 = 1465, 795
    x6, y6 = 730, 738
    # Define the polygon-shaped mask
    roi_points = np.array([[x1, y1], [x2, y2], [x3, y3],[x4, y4],[x5, y5], [x6, y6]] , dtype=np.int32)  # Define your triangle points
    mask = np.zeros((roi_H, roi_W), dtype=np.uint8)
    cv2.fillPoly(mask, [roi_points], 255)
    #Apply the mask to the frame
    masked_frame = cv2.bitwise_and(roi, roi, mask=mask)
    display_image(masked_frame)
    cv2.imwrite(os.path.join(rooth_path, 'data', 'Parking_lot2.jpg'),masked_frame)


"""
    #Polygon cordinates for original_roi 783x440
    x1, y1 = 4, 448
    x2, y2 = 1154, 199
    x3, y3 = 1675, 289
    x4, y4 = 1861, 611
    x5, y5 = 1468, 800
    x6, y6 = 724, 749

   #rectangle Roi 4608,2592                        
    roi_X,roi_Y = 1230, 1375
    roi_W,roi_H = 1920, 1080  
"""

"""
#old cordinates
 #rectangle Roi 4608,2592                        
        roi_X,roi_Y = 1660, 1510
        roi_W,roi_H = 1920, 1080    

#Polygon cordinates for original_roi 783x440
        x1, y1 = 52, 641
        x2, y2 = 1122, 191
        x3, y3 = 1657, 185
        x4, y4 = 1896, 484
        x5, y5 = 1468, 760
        x6, y6 = 787, 800

"""