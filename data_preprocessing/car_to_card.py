from itertools import count

import pandas as pd
from rapidfuzz.fuzz import ratio
from collections import Counter
import json


# Load the cc_location_data.csv file
cc_data = pd.read_csv('../data/cc_data_location_cluster.csv')

# Load the stops_in_location_data.csv file
stops_data = pd.read_csv('../data/stops_in_location_cluster.csv')

# Convert timestamps to datetime format with the correct format
cc_data['timestamp'] = pd.to_datetime(cc_data['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
stops_data['start_time'] = pd.to_datetime(stops_data['start_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
stops_data['end_time'] = pd.to_datetime(stops_data['end_time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Drop rows with invalid timestamps
cc_data.dropna(subset=['timestamp'])
stops_data = stops_data.dropna(subset=['start_time', 'end_time'])

# Create a list to store the filtered data
filtered_data = []

# Iterate through each stop and check if the timestamp falls within the range
for _, stop in stops_data.iterrows():
    matching_entries = cc_data[(cc_data['timestamp'] >= stop['start_time']) &
                               (cc_data['timestamp'] <= stop['end_time'])]
    for _, entry in matching_entries.iterrows():
        filtered_data.append({
            'last4ccnum': entry['last4ccnum'],
            'timestamp_purchase': entry['timestamp'],
            'location': entry['location'],  # Ensure this column name matches the CSV file
            'car_id': stop['car_id'],
            'start_time_visit': stop['start_time'],
            'end_time_visit': stop['end_time'],
            'location_name': stop['location'],
            'geometry': entry['geometry'],
        })

# Convert the filtered data to a DataFrame
merged_data = pd.DataFrame(filtered_data)

# Print the columns of the merged_data DataFrame
#print(merged_data)

# Filter the merged data to keep only rows where the location names are similar

# Define a similarity threshold
SIMILARITY_THRESHOLD = 80

final_filtered_data = merged_data[
    merged_data.apply(lambda row: ratio(row['location'], row['location_name']) >= SIMILARITY_THRESHOLD, axis=1)
]

final_filtered_data = final_filtered_data.drop(columns=['location_name'])

# Save the filtered data to a new CSV file
final_filtered_data.to_csv('../data/merged_card_car_data_cluster.csv', index=False)

print("Merged data saved to '../data/merged_card_car_data_cluster.csv'")

# Load the merged data
merged_data = pd.read_csv('../data/merged_card_car_data_cluster.csv')

# Group by car_id and find the most common last4ccnum for each group along with its count
most_common_cards = merged_data.groupby('car_id')['last4ccnum'].apply(lambda x: Counter(x).most_common(1)[0])

# Convert the filtered results to a DataFrame
most_common_cards_df = pd.DataFrame([
    {'car_id': car_id, 'most_used_card': last4ccnum, 'count': count}
    for car_id, (last4ccnum, count) in most_common_cards.items()
])

# Save the DataFrame to a CSV file
most_common_cards_df.to_csv('../data/most_used_cards_per_car.csv', index=False)

print("Filtered most used card data saved to '../data/most_used_cards_per_car.csv'")