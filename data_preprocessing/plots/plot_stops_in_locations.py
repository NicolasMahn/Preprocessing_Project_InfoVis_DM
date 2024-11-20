import json
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# Load the stops_in_locations.json file
with open('../../data/location_v1/stops_in_locations.json', 'r') as file:
    stops_data = json.load(file)

# Create a list to store the stop points
stop_points = []

# Iterate through the stops data and create Point geometries
for stop in stops_data:
    stop_point = Point(stop['start_coordinates'][1], stop['start_coordinates'][0])
    stop_points.append({
        "car_id": stop['car_id'],
        "start_time": stop['start_time'],
        "end_time": stop['end_time'],
        "location_name": stop['location_name'],
        "geometry": stop_point
    })

# Convert the list to a GeoDataFrame
stops_gdf = gpd.GeoDataFrame(stop_points)

# Plot the stop points
fig, ax = plt.subplots(figsize=(10, 10))
stops_gdf.plot(ax=ax, marker='o', color='red', markersize=5, label='Stops')

# Optionally, plot the locations from locations.geojson
locations_gdf = gpd.read_file('../../data/location_v1/locations.geojson')
locations_gdf.plot(ax=ax, facecolor='none', edgecolor='blue', linewidth=1, label='Locations')

# Add a legend and title
plt.legend()
plt.title('Car Stops in Defined Locations')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Show the plot
plt.show()