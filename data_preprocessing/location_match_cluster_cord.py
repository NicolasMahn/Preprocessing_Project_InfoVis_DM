import json
import pandas as pd
import geopandas as gpd

# Load the locations_2 data
locations_2 = pd.read_csv('../data/locations_2.csv', delimiter=';')

# Load the cluster_polygon.geojson data
cluster_gdf = gpd.read_file('../data/cluster_polygons.geojson')

# Merge the locations_2 data with the cluster polygons based on the cluster ID
merged_data = locations_2.merge(cluster_gdf[['id', 'geometry']], left_on='Cluster Nummer', right_on='id')

# Select only the required columns: location name, geometry, and unique cluster ID
result = merged_data[['location_name', 'geometry', 'Cluster Nummer']]

# Save the result as a CSV file
result.to_csv('../data/locations_with_clusters.csv', index=False)