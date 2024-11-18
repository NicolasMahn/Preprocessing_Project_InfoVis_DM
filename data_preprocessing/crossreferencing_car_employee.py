import pandas as pd
import json

# Load the cc_location_data.csv file
cc_data = pd.read_csv('../data/cc_location_data.csv')

# Load the stops_in_locations.json file
with open('../data/stops_in_locations.json') as f:
    stops_data = json.load(f)

# Convert stops_data to a DataFrame
stops_df = pd.json_normalize(stops_data)

# Convert timestamps to datetime format with the correct format
cc_data['timestamp'] = pd.to_datetime(cc_data['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
stops_df['start_time'] = pd.to_datetime(stops_df['start_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
stops_df['end_time'] = pd.to_datetime(stops_df['end_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Drop rows with invalid timestamps
cc_data = cc_data.dropna(subset=['timestamp'])
stops_df = stops_df.dropna(subset=['start_time', 'end_time'])

# Create a list to store the filtered data
filtered_data = []

# Iterate through each stop and check if the timestamp falls within the range
for _, stop in stops_df.iterrows():
    matching_entries = cc_data[(cc_data['timestamp'] >= stop['start_time']) &
                               (cc_data['timestamp'] <= stop['end_time'])]
    for _, entry in matching_entries.iterrows():
        if entry['location'] == stop['location_name']:
            filtered_data.append({
                'timestamp': entry['timestamp'],
                'price': entry['price'],
                'last4ccnum': entry['last4ccnum'],
                'start_time': stop['start_time'],
                'end_time': stop['end_time'],
                'location_name': stop['location_name']
            })

# Convert the filtered data to a DataFrame
final_filtered_data = pd.DataFrame(filtered_data)

# Save the filtered data to a new CSV file
final_filtered_data.to_csv('../data/merged_card_car_data.csv', index=False)

print("Merged data saved to '../data/merged_card_car_data.csv'")