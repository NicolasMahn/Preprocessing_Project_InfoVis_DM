import pandas as pd
from rapidfuzz.fuzz import ratio
from collections import Counter


# Load the cc_location_data.csv file
cc_data = pd.read_csv('../data/cc_location_data.csv')

# Load the stops_in_location_data.csv file
stops_data = pd.read_csv('../data/stops_in_locations.csv')

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
            'name_location': entry['name_location'],  # Ensure this column name matches the CSV file
            'car_id': stop['car_id'],
            'start_time_visit': stop['start_time'],
            'end_time_visit': stop['end_time'],
            'location_name': stop['location_name'],
            'geometry': entry['geometry'],
        })

# Convert the filtered data to a DataFrame
merged_data = pd.DataFrame(filtered_data)

# Print the columns of the merged_data DataFrame
print(merged_data)

# Filter the merged data to keep only rows where the location names are similar

# Define a similarity threshold
SIMILARITY_THRESHOLD = 80

final_filtered_data = merged_data[
    merged_data.apply(lambda row: ratio(row['name_location'], row['location_name']) >= SIMILARITY_THRESHOLD, axis=1)
]

final_filtered_data = final_filtered_data.drop(columns=['location_name'])

# Save the filtered data to a new CSV file
final_filtered_data.to_csv('../data/merged_card_car_data.csv', index=False)

print("Merged data saved to '../data/merged_card_car_data.csv'")

# Load the merged data
merged_card_car_data = pd.read_csv('../data/merged_card_car_data.csv')

# Group by car_id and find the most common last4ccnum for each group
most_common_cards = merged_card_car_data.groupby('car_id')['last4ccnum'].apply(lambda x: Counter(x).most_common(1)[0][0])

# Print the results
for car_id, last4ccnum in most_common_cards.items():
    print(f"Car ID: {car_id}, Most Frequently Used Card: {last4ccnum}")