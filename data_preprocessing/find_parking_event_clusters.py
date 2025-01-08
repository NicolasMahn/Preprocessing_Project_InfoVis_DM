# Step 2:
# clustering the stops per car on a radius to find parking events
# plot with clusters and abila streetmap as background
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from matplotlib.colors import ListedColormap
import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from shapely.geometry import shape, LineString, Polygon, MultiPolygon, Point
from shapely.geometry.polygon import Polygon as ShapelyPolygon
from shapely.ops import unary_union

# Load the JSON file for stops
with open('../data/stops_per_car.json', 'r') as file:
    data = json.load(file)

# Extract coordinates of stops with additional details
stops = []
for car_id, events in data.items():
    for event in events:
        stops.append({
            'car_id': car_id,
            'start_time': event['start_time'],
            'end_time': event['end_time'],
            'time_difference_sec': event['time_difference_sec'],
            'latitude': event['start_coordinates'][0],
            'longitude': event['start_coordinates'][1]
        })
        stops.append({
            'car_id': car_id,
            'start_time': event['start_time'],
            'end_time': event['end_time'],
            'time_difference_sec': event['time_difference_sec'],
            'latitude': event['end_coordinates'][0],
            'longitude': event['end_coordinates'][1]
        })

# Convert to DataFrame
stops_df = pd.DataFrame(stops)

# Apply DBSCAN clustering with a smaller radius (eps)
radius = 0.0025  # Smaller radius
coords = stops_df[['latitude', 'longitude']].values
db = DBSCAN(eps=radius, min_samples=15).fit(coords)
stops_df['cluster'] = db.labels_

# Filter out noise points (cluster label -1)
stops_df = stops_df[stops_df['cluster'] != -1]

# Assign unique IDs to each cluster
unique_cluster_ids = {cluster: idx for idx, cluster in enumerate(stops_df['cluster'].unique())}
stops_df['unique_cluster_id'] = stops_df['cluster'].map(unique_cluster_ids)

# Save points for each cluster to a JSON file with additional details
clusters = {}
for unique_id in stops_df['unique_cluster_id'].unique():
    cluster_points = stops_df[stops_df['unique_cluster_id'] == unique_id]
    clusters[int(unique_id)] = cluster_points[['car_id', 'start_time', 'end_time', 'time_difference_sec', 'latitude', 'longitude']].to_dict(orient='records')

with open('../data/stops_in_parking_event_clusters.json', 'w') as outfile:
    json.dump(clusters, outfile, indent=4)

# Calculate the bounding box for each cluster and save as polygons
cluster_polygons = []
for unique_id in stops_df['unique_cluster_id'].unique():
    cluster_points = stops_df[stops_df['unique_cluster_id'] == unique_id]
    min_lat = cluster_points['latitude'].min()
    max_lat = cluster_points['latitude'].max()
    min_lon = cluster_points['longitude'].min()
    max_lon = cluster_points['longitude'].max()
    polygon = Polygon([
        (min_lon, min_lat),
        (min_lon, max_lat),
        (max_lon, max_lat),
        (max_lon, min_lat),
        (min_lon, min_lat)
    ])
    cluster_polygons.append({
        'id': int(unique_id),
        'name': '',
        'geometry': polygon.__geo_interface__
    })

# Save the polygons to a JSON file
with open('../data/parking_event_cluster_geometry.json', 'w') as outfile:
    json.dump(cluster_polygons, outfile, indent=4)

# Load the polygons from the JSON file
with open('../data/parking_event_cluster_geometry.json', 'r') as infile:
    cluster_polygons = json.load(infile)

# Convert the JSON data to a GeoDataFrame
features = []
for feature in cluster_polygons:
    geom = feature['geometry']
    properties = feature
    features.append({
        'geometry': shape(geom),
        'id': properties['id'],
        'name': properties['name']
    })

cluster_gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")

# Load GeoJSON data for streets
geojson_path = '../data/raw_data/abila_2.geojson'
with open(geojson_path) as f:
    geojson_data = json.load(f)

# Define the array of street names to highlight
desired_street_names = ["Rist Way", "Carnero St", "Barwyn St", "Arkadiou St", "Androutsou St", "Velestinou Blv", "Ermou St", "Egeou Av", "Ipsilantou Ave",
                        "Pilau St", "Parla St", "Spetson St", "Taxiarchon Ave"]

# Extract geometries and properties
geometries = []
street_names = []
for feature in geojson_data['features']:
    geometry = feature['geometry']
    street_name = feature['properties']['Name']

    if "coordinates" in geometry:
        if geometry["type"] == "LineString" and len(geometry["coordinates"]) > 1:
            geom = shape(geometry)
            geometries.append(geom)
            street_names.append(street_name)
        elif geometry["type"] == "Polygon" and len(geometry["coordinates"][0]) > 1:
            geom = shape(geometry)
            geometries.append(geom)
            street_names.append(street_name)
        elif geometry["type"] == "MultiPolygon":
            valid_polygons = []
            for poly_coords in geometry["coordinates"]:
                if len(poly_coords[0]) > 1:
                    valid_polygons.append(poly_coords)
            if valid_polygons:
                geom = shape({"type": "MultiPolygon", "coordinates": valid_polygons})
                geometries.append(geom)
                street_names.append(street_name)

# Create a GeoDataFrame without reprojecting
gdf = gpd.GeoDataFrame({'geometry': geometries, 'Name': street_names}, crs="EPSG:4326")

# Plot the stops with clusters and street network
plt.figure(figsize=(12, 8))

# Use a predefined color palette
colors = list(mcolors.TABLEAU_COLORS.values())
color_map = {name: colors[i % len(colors)] for i, name in enumerate(desired_street_names)}

# Plot the geometries with different colors and increased line width
for geom, name in zip(gdf.geometry, gdf.Name):
    matching_name = next((desired_name for desired_name in desired_street_names if desired_name in name), None)
    if matching_name:
        color = color_map[matching_name]
    else:
        color = '#D3D3D3'  # Very light gray color
    if isinstance(geom, Polygon):
        x, y = geom.exterior.xy
        plt.fill(x, y, color=color, alpha=0.5)
    elif isinstance(geom, LineString):
        x, y = geom.xy
        plt.plot(x, y, color=color, linewidth=4 if matching_name else 1)

# Create legend
legend_patches = [mpatches.Patch(color=color, label=name) for name, color in color_map.items()]
plt.legend(handles=legend_patches, title="Street Names", loc="upper right")

# Plot the clusters as polygons and add unique cluster IDs
for unique_id in stops_df['unique_cluster_id'].unique():
    cluster_points = stops_df[stops_df['unique_cluster_id'] == unique_id]
    points = [Point(lon, lat) for lon, lat in zip(cluster_points['longitude'], cluster_points['latitude'])]
    polygon = unary_union([point.buffer(0.0025) for point in points])
    if isinstance(polygon, ShapelyPolygon):
        x, y = polygon.exterior.xy
        plt.fill(x, y, color='red', alpha=0.5)
        centroid = polygon.centroid
        plt.text(centroid.x, centroid.y, str(unique_id), fontsize=12, ha='center')
    elif isinstance(polygon, MultiPolygon):
        for poly in polygon:
            x, y = poly.exterior.xy
            plt.fill(x, y, color='red', alpha=0.5)
            centroid = poly.centroid
            plt.text(centroid.x, centroid.y, str(unique_id), fontsize=12, ha='center')

plt.title('Parking Event Clusters with Street Network')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Save the plot to the 'plots' directory
plt.savefig('./plots/parking_event_clusters_with_streets.png')
# Save the plot to the 'plots' directory without background
plt.savefig('./plots/parking_event_clusters_with_streets_transparent.png', transparent=True)
plt.show()