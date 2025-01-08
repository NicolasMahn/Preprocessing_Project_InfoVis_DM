import json
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from shapely.geometry import Point, Polygon, MultiPolygon, shape, LineString
from shapely.ops import unary_union
import pandas as pd
import numpy as np

# Load the polygons from the new JSON file
with open('./location_parking_cluster_matched_cleaned.json', 'r') as infile:
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

# Load employee cluster data
employee_cluster_path = './employee_cluster.geojson'
with open(employee_cluster_path) as f:
    employee_data = json.load(f)

# Convert employee data to GeoDataFrame
employee_features = []
for feature in employee_data['features']:
    properties = feature['properties']
    for employee in properties['employees']:
        point = Point(employee['longitude'], employee['latitude'])
        employee_features.append({
            'geometry': point,
            'id': properties['cluster_id']
        })

# Convert list of dictionaries to DataFrame
employee_df = pd.DataFrame(employee_features)

# Create GeoDataFrame with geometry column
employee_gdf = gpd.GeoDataFrame(employee_df, crs="EPSG:4326", geometry='geometry')

# Load the mean coordinates data
mean_coordinates_path = './mean_employee_cluster_coordinates.json'
with open(mean_coordinates_path) as f:
    mean_coordinates = json.load(f)

# Extract data for plotting
latitudes = [entry['latitude'] for entry in mean_coordinates]
longitudes = [entry['longitude'] for entry in mean_coordinates]
cluster_ids = [entry['cluster_id'] for entry in mean_coordinates]

# Generate unique colors for each location cluster
unique_names = cluster_gdf['name'].unique()
colors = [plt.cm.tab20(i / len(unique_names)) for i in range(len(unique_names))]

# Plot 1: Abila map only
plt.figure(figsize=(12, 8))
for geom, name in zip(gdf.geometry, gdf.Name):
    matching_name = next((desired_name for desired_name in desired_street_names if desired_name in name), None)
    color = '#D3D3D3'  # Default color
    if isinstance(geom, Polygon):
        x, y = geom.exterior.xy
        plt.fill(x, y, color=color, alpha=0.5)
    elif isinstance(geom, LineString):
        x, y = geom.xy
        plt.plot(x, y, color=color, linewidth=1)
plt.axis('off')
plt.savefig('./plots/abila_map.png', bbox_inches='tight')
plt.close()

# Plot 2: Abila map with location clusters
plt.figure(figsize=(12, 8))
for geom, name in zip(gdf.geometry, gdf.Name):
    matching_name = next((desired_name for desired_name in desired_street_names if desired_name in name), None)
    color = '#D3D3D3'  # Default color
    if isinstance(geom, Polygon):
        x, y = geom.exterior.xy
        plt.fill(x, y, color=color, alpha=0.5)
    elif isinstance(geom, LineString):
        x, y = geom.xy
        plt.plot(x, y, color=color, linewidth=1)
legend_patches = []
for i, name in enumerate(unique_names):
    cluster_points = cluster_gdf[cluster_gdf['name'] == name]
    points = []
    for geom in cluster_points['geometry']:
        if geom.geom_type == 'Point':
            points.append(geom)
        elif geom.geom_type == 'Polygon':
            points.extend([Point(x, y) for x, y in geom.exterior.coords])
        elif geom.geom_type == 'MultiPolygon':
            for poly in geom.geoms:
                points.extend([Point(x, y) for x, y in poly.exterior.coords])
    polygon = unary_union([point.buffer(0.0015) for point in points])
    color = colors[i]
    if isinstance(polygon, Polygon):
        x, y = polygon.exterior.xy
        plt.fill(x, y, color=color, alpha=0.75)
    elif isinstance(polygon, MultiPolygon):
        for poly in polygon.geoms:
            x, y = poly.exterior.xy
            plt.fill(x, y, color=color, alpha=0.75)
    legend_patches.append(mpatches.Patch(color=color, label=name))
plt.axis('off')
plt.savefig('./plots/abila_map_location_cluster.png', bbox_inches='tight')
plt.close()

# Plot 3: Abila map with location clusters and employee clusters
plt.figure(figsize=(12, 8))
for geom, name in zip(gdf.geometry, gdf.Name):
    matching_name = next((desired_name for desired_name in desired_street_names if desired_name in name), None)
    color = '#D3D3D3'  # Default color
    if isinstance(geom, Polygon):
        x, y = geom.exterior.xy
        plt.fill(x, y, color=color, alpha=0.5)
    elif isinstance(geom, LineString):
        x, y = geom.xy
        plt.plot(x, y, color=color, linewidth=1)
for i, name in enumerate(unique_names):
    cluster_points = cluster_gdf[cluster_gdf['name'] == name]
    points = []
    for geom in cluster_points['geometry']:
        if geom.geom_type == 'Point':
            points.append(geom)
        elif geom.geom_type == 'Polygon':
            points.extend([Point(x, y) for x, y in geom.exterior.coords])
        elif geom.geom_type == 'MultiPolygon':
            for poly in geom.geoms:
                points.extend([Point(x, y) for x, y in poly.exterior.coords])
    polygon = unary_union([point.buffer(0.0015) for point in points])
    color = colors[i]
    if isinstance(polygon, Polygon):
        x, y = polygon.exterior.xy
        plt.fill(x, y, color=color, alpha=0.75)
    elif isinstance(polygon, MultiPolygon):
        for poly in polygon.geoms:
            x, y = poly.exterior.xy
            plt.fill(x, y, color=color, alpha=0.75)
for idx, row in employee_gdf.iterrows():
    geom = row['geometry']
    if geom.geom_type == 'Point':
        plt.plot(geom.x, geom.y, 'o', markersize=15, color='#d95f02', zorder=5)  # Larger points with a suitable color
        plt.text(geom.x, geom.y, str(row['id']), fontsize=10, ha='center', va='center', color='white', zorder=6)  # ID inside the point
plt.scatter(longitudes, latitudes, c='blue', s=50, alpha=0.7, edgecolors='k', zorder=4)
plt.axis('off')
plt.savefig('./plots/abila_map_location_employee_cluster.png', bbox_inches='tight')
plt.close()

# Plot 4: Legend for location clusters
plt.figure(figsize=(6, 4))
plt.legend(handles=legend_patches, loc='center', bbox_to_anchor=(0.5, 0.5), frameon=False)
plt.axis('off')
plt.savefig('./plots/location_clusters_legend.png', bbox_inches='tight')
plt.close()