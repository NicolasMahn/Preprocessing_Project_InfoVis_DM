import json
import pandas as pd

# Load the JSON file
with open('../data/stops_in_location_clusters_employee.json', 'r') as file:
    carstops_data = json.load(file)

# Convert data to a DataFrame
data = []
for stop in carstops_data:
    data.append({
        'car_id': stop.get('car_id'),
        'LastName': stop.get('LastName'),
        'FirstName': stop.get('FirstName'),
        'CurrentEmploymentType': stop.get('CurrentEmploymentType'),
        'CurrentEmploymentTitle': stop.get('CurrentEmploymentTitle'),
        'start_time': pd.to_datetime(stop.get('start_time')),
        'end_time': pd.to_datetime(stop.get('end_time')),
        'duration_of_stop_min': stop.get('duration_of_stop_min'),
        'latitude': stop.get('start_coordinates')[0],
        'longitude': stop.get('start_coordinates')[1],
        'location': stop.get('location')
    })

df = pd.DataFrame(data)

# Helper function to check time overlap
def has_overlap(group):
    for i, row1 in group.iterrows():
        for j, row2 in group.iterrows():
            if i >= j:
                continue
            overlap = (row1['start_time'] < row2['end_time'] and row2['start_time'] < row1['end_time'])
            overlap_duration = min(row1['end_time'], row2['end_time']) - max(row1['start_time'], row2['start_time'])
            if overlap and overlap_duration.total_seconds() >= 600:  # Minimum 5 minutes overlap
                return True
    return False

# Helper function to check if a cluster repeats
def cluster_repeats(cluster, all_clusters):
    cluster_set = frozenset([entry['car_id'] for entry in cluster])
    for other_cluster in all_clusters:
        other_cluster_set = frozenset([entry['car_id'] for entry in other_cluster])
        if cluster_set == other_cluster_set:
            return True
    return False

# Group by location and filter clusters with at least 2 overlapping entries
grouped = df.groupby('location')
result = []
seen_clusters = set()
all_clusters = []
cluster_id_counter = 1

for location, group in grouped:
    group = group.sort_values(by='start_time')
    overlapping_entries = []

    for _, row in group.iterrows():
        overlapping = False
        for entry in overlapping_entries:
            overlap = (row['start_time'] < entry['end_time'] and entry['start_time'] < row['end_time'])
            overlap_duration = min(row['end_time'], entry['end_time']) - max(row['start_time'], entry['start_time'])
            if overlap and overlap_duration.total_seconds() >= 300:  # Minimum 5 minutes overlap
                overlapping = True
                break

        if overlapping or not overlapping_entries:
            overlapping_entries.append(row)

    if len(overlapping_entries) > 1 and has_overlap(pd.DataFrame(overlapping_entries)):
        cluster = []
        for entry in overlapping_entries:
            cluster.append({
                'car_id': entry['car_id'],
                'LastName': entry['LastName'],
                'FirstName': entry['FirstName'],
                'CurrentEmploymentType': entry['CurrentEmploymentType'],
                'CurrentEmploymentTitle': entry['CurrentEmploymentTitle'],
                'start_time': str(entry['start_time']),
                'end_time': str(entry['end_time']),
                'duration_of_stop_min': entry['duration_of_stop_min'],
                'latitude': entry['latitude'],
                'longitude': entry['longitude']
            })

        cluster_key = frozenset([entry['car_id'] for entry in overlapping_entries])
        if cluster_key not in seen_clusters and not cluster_repeats(cluster, all_clusters):
            seen_clusters.add(cluster_key)
            all_clusters.append(cluster)
            result.append({
                'cluster_id': cluster_id_counter,
                'location': location,
                'cluster': cluster
            })
            cluster_id_counter += 1

# Save the result to a JSON file
with open('../data/stops_same_location_time_employee.json', 'w') as outfile:
    json.dump(result, outfile, indent=4)
