# what happens if there was an error in the pipeline (right now the error is reported on the log file, and the pipeline will be stop and restarted in the next iteration)
# In case of an error, the database dont get an entry in that iteration, that means that the database dont have holes.
# In case of an error on the pipeline the UI will show the last state of the parking lot (because the database didnt become more entries), until a new entry is added.
# To do:
# Restring the database to a specific Size (manage data storage over long periods)


import sqlite3
import os

# Define the file path for the SQLite database
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
db_file_path = os.path.join(ROOT_DIR, "occupancy_data.db")

def create_database():
    #print("db_file_path: ", db_file_path)
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    # Create the 'occupied_spots' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS occupied_spots (
            id INTEGER PRIMARY KEY,
            spot_id TEXT,
            timestamp DATETIME,
            occupancy_status INTEGER,
            occupied_timestamp DATETIME,
            average_occupation_duration REAL,
            score REAL
        )
    ''')
    conn.commit()
    conn.close()

#Method to insert an Entry
def insert_occupied_spot(spot_id, timestamp, occupancy_status, occupied_timestamp, average_occupation_duration, score):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO occupied_spots (spot_id, timestamp, occupancy_status, occupied_timestamp, average_occupation_duration, score) VALUES (?, ?, ?, ?, ?, ?)', (spot_id, timestamp, occupancy_status, occupied_timestamp, average_occupation_duration, score))
    conn.commit()
    conn.close()

#Method to get database info
def get_instances_info():
    """
    - Method retrives the hole info store in the database
    - The information is summirize by timestamp in a dict. The key is the timestamp and the value is a list with the occupied parking spots info that that were encounter on that report timestamp
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        # Retrieve all instances
        cursor.execute("SELECT * FROM occupied_spots ORDER BY timestamp")
        instances_info = cursor.fetchall()
        database_dict = {}
        for row in instances_info:
            timestamp = row[2]
            value = (row[1],row[3], row[4],row[5], row[6])      # Spot_id, occupied_by, occupied_timestamp, average duration, score
            if timestamp in database_dict:
                database_dict[timestamp].append(value)
            else:
                database_dict[timestamp] = [value]

        return database_dict

    finally:
        # Close the database connection
        conn.close()

"""def get_instances_counts():
    try:
        # Connect to the database
        conn = sqlite3.connect(db_file_path)
        cursor = conn.cursor()

        # Count bicycles
        cursor.execute("SELECT COUNT(*) FROM occupied_spots WHERE occupancy_status = 0 GROUP BY timestamp")
        bicycles_count = len(cursor.fetchall())

        # Count motorcycles
        cursor.execute("SELECT COUNT(*) FROM occupied_spots WHERE occupancy_status = 1 GROUP BY timestamp")
        motorcycles_count = len(cursor.fetchall())

        # Calculate total instances count
        total_instances_count = bicycles_count + motorcycles_count

        return total_instances_count, bicycles_count, motorcycles_count

    finally:
        # Close the database connection
        conn.close()"""


