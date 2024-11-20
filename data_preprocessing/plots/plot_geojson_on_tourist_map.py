import json
import pandas as pd
from shapely.geometry import shape, LineString, Polygon, MultiPolygon, Point
import matplotlib.pyplot as plt
import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from PIL import Image
from matplotlib.ticker import FixedLocator

# Load GeoJSON data
geojson_path = '../../data/raw_data/abila_2.geojson'
with open(geojson_path) as f:
    geojson_data = json.load(f)

# Define the array of street names to display
desired_street_names = ["Rist Way", "Carnero St", "Barwyn St", "Arkadiou St", "Androutsou St", "Velestinou Blv", "Ermou St", "Egeou Av", "Ipsilantou Ave",
                        "Pilau St", "Parla St", "Spetson St", "Taxiarchon Ave"]

# Extract geometries and properties
geometries = []
street_names = []
for feature in geojson_data['features']:
    geometry = feature['geometry']
    street_name = feature['properties']['Name']

    # Check if any part of the street name matches the desired street names
    if any(desired_name in street_name for desired_name in desired_street_names):
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
                # Check each Polygon in the MultiPolygon
                valid_polygons = []
                for poly_coords in geometry["coordinates"]:
                    if len(poly_coords[0]) > 1:  # Ensure exterior ring has >1 point
                        valid_polygons.append(poly_coords)
                if valid_polygons:
                    geom = shape({"type": "MultiPolygon", "coordinates": valid_polygons})
                    geometries.append(geom)
                    street_names.append(street_name)

# Create a GeoDataFrame without reprojecting
gdf = gpd.GeoDataFrame({'geometry': geometries, 'Name': street_names}, crs="EPSG:4326")

# Get the dimensions of the image
image_path = '../../data/raw_data/MC2-tourist.jpg'
image = Image.open(image_path)
width, height = image.size

# Set plot size to match the dimensions of MC2-tourist.jpg
fig, ax = plt.subplots(figsize=(width / 100, height / 100))  # Adjust the size as needed

# Use a predefined color palette
colors = list(mcolors.TABLEAU_COLORS.values())
color_map = {name: colors[i % len(colors)] for i, name in enumerate(desired_street_names)}

# Plot the geometries with different colors and increased line width
for geom, name in zip(gdf.geometry, gdf.Name):
    # Find the matching desired street name
    matching_name = next((desired_name for desired_name in desired_street_names if desired_name in name), None)
    if matching_name:
        color = color_map[matching_name]
        if isinstance(geom, Polygon):
            x, y = geom.exterior.xy
            ax.fill(x, y, color=color, alpha=0.5)
        elif isinstance(geom, LineString):
            x, y = geom.xy
            ax.plot(x, y, color=color, linewidth=4)  # Increase line width

# Create legend
legend_patches = [mpatches.Patch(color=color, label=name) for name, color in color_map.items()]
ax.legend(handles=legend_patches, title="Street Names")

# Add finer grid to the plot
ax.grid(True, which='both', linestyle='-', linewidth=0.8)
ax.minorticks_on()
ax.grid(which='minor', linestyle=':', linewidth=0.4)

# Set more numbers on the axis
ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=20))
ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=20))

# Use FixedLocator to set the ticks
x_ticks = ax.get_xticks()
y_ticks = ax.get_yticks()
ax.xaxis.set_major_locator(FixedLocator(x_ticks))
ax.yaxis.set_major_locator(FixedLocator(y_ticks))

# Format the tick labels to show the original coordinates
ax.set_xticklabels([f"{tick:.6f}° E" for tick in x_ticks])
ax.set_yticklabels([f"{tick:.6f}° N" for tick in y_ticks])

# Save plot as PNG with transparent background
plt.savefig('./plots/map_abila_grid_transparent.png', transparent=True)

# Add a white border around the plot
fig.patch.set_facecolor('white')
fig.subplots_adjust(left=0.05, right=0.975, top=0.975, bottom=0.05)

# Display the image as the background
ax.imshow(image, extent=[gdf.total_bounds[0], gdf.total_bounds[2], gdf.total_bounds[1], gdf.total_bounds[3]], aspect='auto')

# Save plot with the MC2 tourist map as background
plt.savefig('./plots/overlapped_map_abila_tourist.png')

# Show plot
plt.show()