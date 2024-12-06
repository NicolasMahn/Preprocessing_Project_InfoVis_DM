import pandas as pd
import geopandas as gpd
from shapely import wkt

def card_data_to_location_cluster(data_name, file_path='../data/raw_data/'):
    data = pd.read_csv(f'{file_path}{data_name}.csv')

    # Convert timestamps to datetime format (MM/DD/YYYY HH:MM)
    if data_name != 'cleaned_card_data':
        data['timestamp'] = pd.to_datetime(data['timestamp'], format='%m/%d/%Y %H:%M', errors='coerce')
    else:
        data['timestamp'] = pd.to_datetime(data['date'], format="%Y-%m-%d %H:%M:%S", errors='coerce')

    # Set the seconds to '00'
    data['timestamp'] = data['timestamp'].apply(lambda x: x.replace(second=0) if pd.notnull(x) else x)

    # Save the updated data to a new CSV file
    data.to_csv(f'{file_path}{data_name}2.csv', index=False)
    print(f"Timestamps converted and saved to '{file_path}{data_name}2.csv'")

    # Reload the updated data
    data2 = pd.read_csv(f'{file_path}{data_name}2.csv')

    # Load the locations.csv file
    locations_df = pd.read_csv('../data/locations_cluster_geometry.csv')

    # Convert the 'geometry' column to shapely geometries
    locations_df['geometry'] = locations_df['geometry'].apply(wkt.loads)

    # Create a GeoDataFrame from the locations DataFrame
    locations_gdf = gpd.GeoDataFrame(locations_df, geometry='geometry', crs="EPSG:4326")

    # Merge the DataFrame with the GeoDataFrame based on the location names
    merged_data = data2.merge(locations_gdf, left_on='location', right_on='location_name', how='left')

    # Filter out rows with missing coordinates
    filtered_data = merged_data.dropna(subset=['geometry'])

    # Drop the location column
    filtered_data = filtered_data.drop(columns=['location_name'])

    # filtered_data = filtered_data.rename(columns={'name': 'name_location'})

    # Save the filtered data to a new CSV file
    filtered_data.to_csv(f'../data/{data_name}_location_cluster.csv', index=False)
    print(f"Filtered data saved to '../data/{data_name}_location_cluster.csv'")


card_data_to_location_cluster('cc_data')
card_data_to_location_cluster('loyalty_data')
card_data_to_location_cluster('cleaned_card_data', '../data/' )