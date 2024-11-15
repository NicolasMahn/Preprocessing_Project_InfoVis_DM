import json
import pandas as pd

# Load CSV data and extract unique locations
csv_path = '../data/cc_data.csv'
df = pd.read_csv(csv_path, header=None, names=['Date', 'Location', 'Amount', 'ID'], encoding='ISO-8859-1')
unique_locations = df['Location'].unique()

# Load GeoJSON data
geojson_path = '../data/abila_2.geojson'
with open(geojson_path) as f:
    geojson_data = json.load(f)

# Search for locations in GeoJSON data
matching_features = []
for feature in geojson_data['features']:
    properties = feature['properties']
    if any(loc in properties['Name'] for loc in unique_locations):
        matching_features.append(properties['Name'])

# Print the results
if matching_features:
    print("Matching locations in GeoJSON:")
    for name in matching_features:
        print(name)
else:
    print("No matching locations found in GeoJSON.")