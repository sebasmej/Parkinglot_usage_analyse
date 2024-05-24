# Parking Lot Occupancy Analysis System

## Project Description

This repository contains the source code for a parking lot occupancy analysis system developed as a university project. 
The system utilizes object detection to analyze the occupancy of a bicycle and motorcycle parking lot in front of the university campus. It runs on a Raspberry Pi equipped with a camera, capturing images of the parking lot. The captured images undergo preprocessing, object detection using YOLOv5n6 model trained on a custom dataset, tracking of detected objects, and storage of occupancy data in a local database. 

Additionally, a graphical user interface (GUI) is provided for visualizing the derived results of the main analysis. The GUI, implemented in the `GUI` folder, includes a `gui.py` file that queries the database, performs a simple data analysis of occupancy, and displays the results on a local UI. The project aims to provide a practical solution for monitoring parking lot usage and analyzing occupancy patterns.

## Features

- Object detection using YOLOv5n6 model trained on a custom dataset for detecting bicycles and motorcycles.
- Tracking system implemented to assign detections to corresponding parking spots and track occupancy.
- Continuous analysis of parking lot occupancy with data saved in a local database (SQlite).
- Graphical user interface (GUI) for visualizing analysis results (Tkinter).

## Installation Instructions

### Raspberry Pi Setup

1. **Prepare Raspberry Pi:**
   - Ensure your Raspberry Pi is set up and connected to the internet.
   - Connect and enable the camera module in the Raspberry Pi configuration settings.

2. **Install Operating System:**
   - Install Raspberry Pi OS (formerly Raspbian) on your Raspberry Pi if not already installed.

3. **Enable Camera Module:**
   - Enable the camera module in the Raspberry Pi configuration settings.

### Dependencies Installation

1. **Clone Repository:**
   - Clone this repository to your Raspberry Pi:
     ```
     git clone <repository-url>
     ```

2. **Install Python Dependencies:**
   - Navigate to the project directory:
     ```
     cd <project-directory>
     ```
   - Install required Python dependencies:
     ```
     pip install -r requirements.txt
     ```

### Configuration

1. **Pre-trained Models:**
   - Pre-trained models for object detection are located in the `models` directory.
   - The default model (YOLOv5n6) is automatically selected for detection.

2. **Database Setup:**
   - The system uses a local database stored on the Raspberry Pi.
   - If the database doesn't exist, it will be automatically created.

## Running the Program

To run the program, execute the `main.py` script with optional command-line arguments:

- **-map \<path>**: Path to a .txt file containing the mapped layout of the parking lot. A mapped parking lot file already exists and is used by default. If the camera position is changed it is necessary to modify this map file.
  
- **-model \<path>**: Path to the YOLO model file for object detection. Default: yolov5n6.

- **-conf \<value>**: Confidence threshold for the detection task, ranging from 0 to 1. Default: 0.05.

- **-iou \<value>**: IoU threshold for Non-Maximum Suppression (NMS). Default: 0.3.

- **-n \<value>**: Length of the detection record, influencing the frame capture frequency (`f`). Default: 2.

The program runs continuously, repeating the process of taking photos, preprocessing, object detection, tracking, and saving the results in the database. You can set these arguments directly in the code or provide them when running the script.

## Using the GUI Interface

To visualize the data collected and analyzed by the main program, use the `gui.py` script. This script queries the database every 15 minutes, performs a data analysis of occupancy, and displays the information in a local UI.

To run the GUI script, execute `gui.py` with the following optional command-line argument:

- **-database \<path>**: Path to the database file (`.db`). Default: the local database created by the main program.
