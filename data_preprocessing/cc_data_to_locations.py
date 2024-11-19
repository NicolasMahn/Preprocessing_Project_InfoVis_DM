import pandas as pd
import geopandas as gpd
from shapely import wkt

# Load the cc_data.csv file
cc_data = pd.read_csv('../data/cc_data.csv')

# Convert timestamps to datetime format (MM/DD/YYYY HH:MM)
cc_data['timestamp'] = pd.to_datetime(cc_data['timestamp'], format='%m/%d/%Y %H:%M', errors='coerce')

# Set the seconds to '00'
cc_data['timestamp'] = cc_data['timestamp'].apply(lambda x: x.replace(second=0) if pd.notnull(x) else x)

# Save the updated data to a new CSV file
cc_data.to_csv('../data/cc_data2.csv', index=False)
print("Timestamps converted and saved to '../data/cc_data2.csv'")

# Reload the updated data
cc_data2 = pd.read_csv('../data/cc_data2.csv')

# Load the locations.csv file
locations_df = pd.read_csv('../data/locations_with_clusters.csv')

# Convert the 'geometry' column to shapely geometries
locations_df['geometry'] = locations_df['geometry'].apply(wkt.loads)

# Create a GeoDataFrame from the locations DataFrame
locations_gdf = gpd.GeoDataFrame(locations_df, geometry='geometry', crs="EPSG:4326")

# Merge the DataFrame with the GeoDataFrame based on the location names
merged_data = cc_data2.merge(locations_gdf, left_on='location', right_on='location_name', how='left')

# Filter out rows with missing coordinates
filtered_data = merged_data.dropna(subset=['geometry'])

# Drop the location column
filtered_data = filtered_data.drop(columns=['location_name'])

#filtered_data = filtered_data.rename(columns={'name': 'name_location'})

# Save the filtered data to a new CSV file
filtered_data.to_csv('../data/cc_location_data2.csv', index=False)
print("Filtered data saved to '../data/cc_location2_data.csv'")