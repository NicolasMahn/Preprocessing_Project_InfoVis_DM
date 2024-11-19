import json
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely import wkt

# Load the stops_per_car.json file
with open('../data/stops_per_car.json', 'r') as file:
    stops_data = json.load(file)

# Load the locations.csv file
locations_df = pd.read_csv('../data/locations_with_clusters.csv')

# Convert the 'geometry' column to shapely geometries
locations_df['geometry'] = locations_df['geometry'].apply(wkt.loads)

# Create a GeoDataFrame from the locations DataFrame
locations_gdf = gpd.GeoDataFrame(locations_df, geometry='geometry', crs="EPSG:4326")

# Create a list to store the results
results = []

# Iterate through each car's stops
for car_id, stops in stops_data.items():
    for stop in stops:
        stop_point = Point(stop['start_coordinates'][1], stop['start_coordinates'][0])

        # Check if the stop point is within any of the polygons
        for _, location in locations_gdf.iterrows():
            if location['geometry'].contains(stop_point):
                results.append({
                    "car_id": car_id,
                    "start_time": stop['start_time'],
                    "end_time": stop['end_time'],
                    "duration_of_stop_min": stop['time_difference_sec']/60,
                    "location": location['location_name'],
                    "start_coordinates": stop['start_coordinates'],
                    "end_coordinates": stop['end_coordinates']
                })

# Save the results to a new JSON file
with open('../data/stops_in_locations2.json', 'w') as output_file:
    json.dump(results, output_file, indent=4)

print("Results saved to '../data/stops_in_locations2.json'")

# Convert the results to a DataFrame
results_df = pd.DataFrame(results)

# Save the results to a new CSV file
results_df.to_csv('../data/stops_in_locations2.csv', index=False)

print("Results saved to '../data/stops_in_locations2.csv'")