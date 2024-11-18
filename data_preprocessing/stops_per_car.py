import json
from datetime import datetime, timedelta

# Load the JSON file
with open('../data/gps_sorted_by_id_2.json', 'r') as file:
    data = json.load(file)

result = {}

# Iterate through each ID in the data
for id_, entries in data.items():
    # Sort entries by timestamp
    entries.sort(key=lambda x: datetime.strptime(x[0], '%Y-%d-%m %H:%M:%S'))
    differences = []

    # Compare consecutive timestamps
    for i in range(1, len(entries)):
        current_entry = entries[i]
        previous_entry = entries[i - 1]

        current_time = datetime.strptime(current_entry[0], '%Y-%d-%m %H:%M:%S')
        previous_time = datetime.strptime(previous_entry[0], '%Y-%d-%m %H:%M:%S')

        # Calculate time difference in seconds
        time_difference = (current_time - previous_time).total_seconds()

        if time_difference > 180:  # More than 3 minutes
            differences.append({
                "start_time": previous_entry[0],
                "end_time": current_entry[0],
                "time_difference_sec": time_difference,
                "start_coordinates": (previous_entry[1], previous_entry[2]),
                "end_coordinates": (current_entry[1], current_entry[2])
            })

    if differences:
        result[id_] = differences

# Save the results to a new JSON file
with open('../data/stops_per_car.json', 'w') as output_file:
    json.dump(result, output_file, indent=4)

print("Differences saved to '../data/stops_per_car.json'")


