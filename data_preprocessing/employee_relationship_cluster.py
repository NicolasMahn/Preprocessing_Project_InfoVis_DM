import json
import pandas as pd

# Load the JSON file
with open('../data/carstops_cluster_with_employees.json', 'r') as file:
    carstops_data = json.load(file)

# Convert data to a DataFrame
data = []
for cluster_id, stops in carstops_data.items():
    for stop in stops:
        data.append({
            'cluster_id': cluster_id,
            'car_id': stop.get('car_id', 'Unknown'),
            'LastName': stop.get('LastName', 'Unknown'),
            'start_time': pd.to_datetime(stop.get('start_time', '1970-01-01')),
            'end_time': pd.to_datetime(stop.get('end_time', '1970-01-01')),
            'latitude': stop.get('latitude', 0.0),
            'longitude': stop.get('longitude', 0.0)
        })

df = pd.DataFrame(data)

# Find entries with the same time for each cluster
df['time'] = df['start_time'].dt.floor('T')
grouped = df.groupby(['cluster_id', 'time'])

# Filter clusters with different car_id within the same cluster
result = []
seen_clusters = set()
for (cluster_id, time), group in grouped:
    unique_car_ids = group['car_id'].unique()
    if len(unique_car_ids) > 1:
        cluster = []
        seen_car_ids = set()
        for _, row in group.iterrows():
            if row['car_id'] not in seen_car_ids:
                seen_car_ids.add(row['car_id'])
                cluster.append({
                    'car_id': row['car_id'],
                    'LastName': row['LastName'],
                    'latitude': row['latitude'],
                    'longitude': row['longitude']
                })
        cluster_key = frozenset([row['car_id'] for row in cluster])
        if cluster_key not in seen_clusters:
            seen_clusters.add(cluster_key)
            result.append({
                'cluster_id': cluster_id,
                'time': str(time),
                'cluster': cluster
            })

# Save the result to a JSON file
with open('../data/clusters_with_different_car_ids.json', 'w') as outfile:
    json.dump(result, outfile, indent=4)