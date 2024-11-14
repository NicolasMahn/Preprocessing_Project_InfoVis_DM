import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# Load GeoJSON data
geojson_path = './data/abila_2.geojson'
gdf = gpd.read_file(geojson_path)

# Plot the GeoDataFrame
fig, ax = plt.subplots(figsize=(10, 10))
gdf.plot(ax=ax, color='blue', edgecolor='black')

# Add street names
for x, y, label in zip(gdf.geometry.centroid.x, gdf.geometry.centroid.y, gdf['street_name']):
    ax.text(x, y, label, fontsize=8, ha='right')

# Add basemap
ctx.add_basemap(ax, crs=gdf.crs.to_string())

# Show plot
plt.show()