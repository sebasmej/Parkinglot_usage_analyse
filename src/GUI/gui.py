# the UI check for changes on the database every cretain time and updates the visualization.

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import sys
import os
import pandas as pd
import numpy as np

database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))
sys.path.append(database_path)
from database import *
from data_analysis import *

# Global variables for Matplotlib plot and canvas
fig, ax = plt.subplots()
canvas = None
database_dict = {}

# Create a function to update the Matplotlib plot
def update_plot(timestamps, bicycle_counts, moto_counts, total_counts):
        # Clear the previous plot
        ax.clear()

        # Convert timestamps to datetime objects
        datetime_objects = pd.to_datetime(timestamps, format='%Y-%m-%d_%H-%M-%S')
        # Extract hours and minutes from datetime objects
        hours_minutes = [dt.strftime('%H:%M') for dt in datetime_objects]
        #print("hours_minutes: ", hours_minutes)
        # Keep only the timestamps at 15-minute intervals for x-axis labels
        hours_minutes_for_labels = [hm for i, hm in enumerate(hours_minutes) if i % 4 == 0]
        x_ticks_positions = np.arange(0, len(hours_minutes), 4)

        #Set x-axis ticks and labels
        ax.set_xticks(x_ticks_positions)  # Set ticks for timestamps at 15-minute intervals
        ax.set_xticklabels(hours_minutes_for_labels, rotation=90)  # Set labels for timestamps at 15-minute intervals
    
        # Plot the data
        ax.plot(hours_minutes, bicycle_counts, marker='o', color='b', label='Bicycles')
        ax.plot(hours_minutes, moto_counts, marker='o', color='r', label='Motorcycles')
        ax.plot(hours_minutes, total_counts, marker='o', color='g', label='Total Instances')
        #ax.tick_params(axis='x', rotation=90)  # Adjust the rotation angle as needed
        
        # Set plot labels and title
        ax.set_xlabel('Time (Hours)')
        ax.set_ylabel('Occupancy')
        ax.set_title('Parking Lot Occupancy Over Time')
        
        # Add legend
        ax.legend()
        
        # Update the canvas
        canvas.draw()

# Function to periodically update the UI
def update_ui_periodically():
    while True:
        # Connect to the database
        new_database_dict = get_instances_info()
        database_dict = new_database_dict
        timestamps, bicycle_counts, moto_counts, total_counts = count_instances_per_timestamp(database_dict)
        """for i in range(len(timestamps)):
             print(timestamps[i], bicycle_counts[i], moto_counts[i], total_counts[i])"""

        current_timestamp = 0
        curent_bici_count = 0
        current_moto_count = 0
        current_total_instances = 0
        occupied_spots_ids = []
        if timestamps or bicycle_counts or moto_counts: 
            current_timestamp = timestamps[-1]
            curent_bici_count = bicycle_counts[-1]
            current_moto_count = moto_counts[-1]
            current_total_instances = curent_bici_count + current_moto_count
            current_spots_list = new_database_dict[current_timestamp]

            for spot in current_spots_list:
                occupied_spots_ids.append(spot[0])

        # Update the UI
        update_plot(timestamps, bicycle_counts, moto_counts, total_counts)
        label_occupancy.config(text=f"Total of bicycles: {curent_bici_count}, Total of motorcycles: {current_moto_count}, Total instances: {current_total_instances}")
        label_occupied_spots.config(text="Occupied Parking Spots: " + ", ".join(occupied_spots_ids))
        
        # Sleep for 15 minutes before checking again (plus 30 seconds to ensure that the pipeline already made an entry on the atabase)
        time.sleep(930)


# Entry point of the script
if __name__ == "__main__":
    # Create the main window
    window = tk.Tk()
    window.title("Parking Lot Occupancy Monitoring")

    # Set the window size to a larger fixed size
    window.geometry("800x640")

    # Add a Matplotlib plot for live occupancy monitoring
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().pack(pady=20)  # Add space at the top

    # Add labels to display information
    label_occupancy = tk.Label(window, text=f"Total of bicycles: 0, Total of motorcycles: 0, Total instances: 0", font=("Arial", 14))
    label_occupancy.pack(pady=10)  # Add space below the plot

    label_occupied_spots = tk.Label(window, text="Occupied Parking Spots: ", font=("Arial", 14))
    label_occupied_spots.pack(pady=10)  # Add space below the occupancy label

    """ # Add a label for average spot occupancy duration
    label_avg_occupancy_duration = tk.Label(window, text="Average Spot Occupancy Duration: ", font=("Arial", 14))
    label_avg_occupancy_duration.pack(pady=10)  # Add space below the occupied spots label"""

    # Create a thread to run the update_ui_periodically function
    update_thread = threading.Thread(target=update_ui_periodically)
    update_thread.daemon = True
    update_thread.start()
    
    # Run the GUI
    window.mainloop()

   
