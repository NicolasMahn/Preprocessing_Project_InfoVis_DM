import json
import pandas as pd

# Load employee cluster data
employee_cluster_path = './employee_cluster.geojson'
with open(employee_cluster_path) as f:
    employee_data = json.load(f)

# Extract coordinates and cluster id
employee_features = []
for feature in employee_data['features']:
    properties = feature['properties']
    cluster_id = properties['cluster_id']
    for employee in properties['employees']:
        employee_features.append({
            'latitude': employee['latitude'],
            'longitude': employee['longitude'],
            'cluster_id': cluster_id
        })

# Convert list of dictionaries to DataFrame
employee_df = pd.DataFrame(employee_features)

# Calculate mean latitude and longitude for each cluster
mean_coordinates = employee_df.groupby('cluster_id')[['latitude', 'longitude']].mean().reset_index()

# Convert the result to a list of dictionaries
mean_coordinates_list = mean_coordinates.to_dict(orient='records')

# Save the mean coordinates to a new JSON file
output_path = './mean_employee_cluster_coordinates.json'
with open(output_path, 'w') as f:
    json.dump(mean_coordinates_list, f, indent=4)