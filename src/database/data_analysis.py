# Right know there are just to simple methods that recieve the database_dict and calculate metrics just for the current day. 
# If more metrics are added inclde the methods here
# If database istructur is chagend, this methods need to be modified

from datetime import datetime, timedelta
import pandas as pd

def count_instances_per_timestamp(database_dict):
    timestamps = []
    bicycle_counts = []
    moto_counts = []
    total_counts = []
    occupied_spoits_ids = []
    # Get today's date
    today = datetime.now().date()
    
    for stamp, spots_list in database_dict.items():
        # Extract the date part from the timestamp key
        timestamp_date = datetime.strptime(stamp, '%Y-%m-%d_%H-%M-%S').date()
        # Check if the date part matches today's date
        if timestamp_date == today:
            timestamps.append(stamp)
            #total_counts.append(len(spots_list))
            bici = moto = 0
            for spot in spots_list:
                occupancy_status = spot[1] 
                if occupancy_status == 0:  # Check if the spot is occupied by a bicycle 
                    bici += 1
                elif occupancy_status == 1:  # Check if the spot is occupied by a motorcycle
                    moto += 1
            bicycle_counts.append(bici)
            moto_counts.append(moto)
            total_counts.append(bici+moto)

    return timestamps, bicycle_counts, moto_counts, total_counts, 

# i dont know if this method is working as intended it hasnt being proove
def get_average_spots_occupancy_duration(database_dict):

    sum_occupancy_duration = 0
    spots_count = 0
    for stamp, spots_list in database_dict.items():
        for spot in spots_list:
            average_duration = spot[4]
            if average_duration != 0:
                spots_count += 1
                sum_occupancy_duration += average_duration
    
    spots_occupancy_duration = sum_occupancy_duration / spots_count


    return spots_occupancy_duration/60 



