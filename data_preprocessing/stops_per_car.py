# Step 1: find stops that last min 3 Minutes sorted by the car ID
import json
from datetime import datetime, timedelta
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely import wkt

# Load the JSON file
with open('../data/raw_data/gps_sorted_by_id_2.json', 'r') as file:
    gps_data = json.load(file)

result = {}

# Function to calculate the difference between coordinates
def coordinates_difference(coord1, coord2):
    return abs(coord1[0] - coord2[0]) < 0.0001 and abs(coord1[1] - coord2[1]) < 0.0001

# Iterate through each ID in the gps_data
for id_, entries in gps_data.items():
    # Sort entries by timestamp
    entries.sort(key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'))
    differences = []

    # Compare consecutive timestamps
    for i in range(1, len(entries)):
        current_entry = entries[i]
        previous_entry = entries[i - 1]

        current_time = datetime.strptime(current_entry[0], '%Y-%m-%d %H:%M:%S')
        previous_time = datetime.strptime(previous_entry[0], '%Y-%m-%d %H:%M:%S')

        # Calculate time difference in seconds
        time_difference = (current_time - previous_time).total_seconds()

        if time_difference > 180:  # More than 3 minutes
            start_coordinates = (previous_entry[1], previous_entry[2])
            end_coordinates = (current_entry[1], current_entry[2])

            if coordinates_difference(start_coordinates, end_coordinates):
                differences.append({
                    "start_time": previous_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "end_time": current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "time_difference_sec": time_difference,
                    "start_coordinates": start_coordinates,
                    "end_coordinates": end_coordinates
                })

    if differences:
        result[id_] = differences

# Save the results to a new JSON file
with open('../data/stops_per_car.json', 'w') as output_file:
    json.dump(result, output_file, indent=4)

print("Differences saved to '../data/stops_per_car.json'")