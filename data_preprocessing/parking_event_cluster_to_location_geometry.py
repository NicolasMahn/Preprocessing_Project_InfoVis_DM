# Step 3: merge the manually selected cluster-location pairs to the geometry
import json
import pandas as pd
import geopandas as gpd

# Load the locations_2 data
locations_2 = pd.read_csv('../data/locations_with_cluster_nr.csv', delimiter=';')

# Load the cluster_polygon.geojson data
cluster_gdf = gpd.read_file('../data/parking_event_cluster_geometry.geojson')

# Merge the locations_2 data with the cluster polygons based on the cluster ID
merged_data = locations_2.merge(cluster_gdf[['id', 'geometry']], left_on='Cluster Nummer', right_on='id')

# Select only the required columns: location name, geometry, and unique cluster ID
result = merged_data[['location_name', 'geometry', 'Cluster Nummer']]

# Save the result as a CSV file
result.to_csv('../data/locations_cluster_geometry.csv', index=False)