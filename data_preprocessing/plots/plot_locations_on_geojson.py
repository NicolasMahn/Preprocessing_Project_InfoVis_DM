import json
import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from PIL import Image
import matplotlib.pyplot as plt
from shapely.geometry import shape, LineString, Polygon, MultiPolygon
from matplotlib.ticker import FixedLocator

# Load the first GeoJSON file
geojson_path_1 = '../../data/raw_data/abila_2.geojson'
with open(geojson_path_1) as f:
    geojson_data_1 = json.load(f)

# Define the array of street names to display
desired_street_names = ["Rist Way", "Carnero St", "Barwyn St", "Arkadiou St", "Androutsou St", "Velestinou Blv", "Ermou St", "Egeou Av", "Ipsilantou Ave",
                        "Pilau St", "Parla St", "Spetson St", "Taxiarchon Ave"]

# Load the second GeoJSON file
geojson_path_2 = '../../data/location_v1/locations.geojson'
with open(geojson_path_2) as f:
    geojson_data_2 = json.load(f)

# Extract geometries and properties from the first GeoJSON file
geometries_abila_street = []
street_names = []
for feature in geojson_data_1['features']:
    geometry = feature['geometry']
    street_name = feature['properties']['Name']

    if any(desired_name in street_name for desired_name in desired_street_names):
        if "coordinates" in geometry:
            if geometry["type"] == "LineString" and len(geometry["coordinates"]) > 1:
                geom = shape(geometry)
                geometries_abila_street.append(geom)
                street_names.append(street_name)
            elif geometry["type"] == "Polygon" and len(geometry["coordinates"][0]) > 1:
                geom = shape(geometry)
                geometries_abila_street.append(geom)
                street_names.append(street_name)
            elif geometry["type"] == "MultiPolygon":
                valid_polygons = []
                for poly_coords in geometry["coordinates"]:
                    if len(poly_coords[0]) > 1:
                        valid_polygons.append(poly_coords)
                if valid_polygons:
                    geom = shape({"type": "MultiPolygon", "coordinates": valid_polygons})
                    geometries_abila_street.append(geom)
                    street_names.append(street_name)

# Create a GeoDataFrame for the first GeoJSON data
gdf_geojson_abila_street = gpd.GeoDataFrame({'geometry': geometries_abila_street, 'Name': street_names}, crs="EPSG:4326")

# Extract geometries and properties from the second GeoJSON file
geometries_locations = []
location_names = []
for feature in geojson_data_2['features']:
    geometry = feature['geometry']
    location_name = feature['properties']['name']
    if "coordinates" in geometry:
        if geometry["type"] == "LineString" and len(geometry["coordinates"]) > 1:
            geom = shape(geometry)
            geometries_locations.append(geom)
            location_names.append(location_name)
        elif geometry["type"] == "Polygon" and len(geometry["coordinates"][0]) > 1:
            geom = shape(geometry)
            geometries_locations.append(geom)
            location_names.append(location_name)
        elif geometry["type"] == "MultiPolygon":
            valid_polygons = []
            for poly_coords in geometry["coordinates"]:
                if len(poly_coords[0]) > 1:
                    valid_polygons.append(poly_coords)
            if valid_polygons:
                geom = shape({"type": "MultiPolygon", "coordinates": valid_polygons})
                geometries_locations.append(geom)
                location_names.append(location_name)

# Create a GeoDataFrame for the second GeoJSON data
gdf_geojson_locations = gpd.GeoDataFrame({'geometry': geometries_locations, 'Name': location_names}, crs="EPSG:4326")

# Re-project both GeoDataFrames to the CRS of the first GeoJSON file
gdf_geojson_abila_street = gdf_geojson_abila_street.to_crs(gdf_geojson_abila_street.crs)
gdf_geojson_locations = gdf_geojson_locations.to_crs(gdf_geojson_abila_street.crs)

# Get the dimensions of the image
image_path = '../../data/raw_data/MC2-tourist.jpg'
image = Image.open(image_path)
width, height = image.size

# Set plot size to match the dimensions of MC2-tourist.jpg
fig, ax = plt.subplots(figsize=(width / 100, height / 100))

# Use a predefined color palette
colors = list(mcolors.TABLEAU_COLORS.values())
color_map = {name: colors[i % len(colors)] for i, name in enumerate(desired_street_names)}

# Plot the first GeoJSON data
for geom, name in zip(gdf_geojson_abila_street.geometry, gdf_geojson_abila_street.Name):
    matching_name = next((desired_name for desired_name in desired_street_names if desired_name in name), None)
    if matching_name:
        color = color_map[matching_name]
        if isinstance(geom, Polygon):
            x, y = geom.exterior.xy
            ax.fill(x, y, color=color, alpha=0.5)
        elif isinstance(geom, LineString):
            x, y = geom.xy
            ax.plot(x, y, color=color, linewidth=4)

# Create legend for first GeoJSON data
legend_patches = [mpatches.Patch(color=color, label=name) for name, color in color_map.items()]
ax.legend(handles=legend_patches, title="Street Names")

# Plot the second GeoJSON data
gdf_geojson_locations.plot(ax=ax, color='red', alpha=0.25, edgecolor='k')

# Re-project the GeoDataFrame to a projected CRS (e.g., EPSG:3857)
gdf_geojson_locations_projected = gdf_geojson_locations.to_crs(epsg=3857)

# Now calculate centroids in the projected CRS
centroids = gdf_geojson_locations_projected.geometry.centroid

# Add the location names as labels at centroid positions
for x, y, label in zip(centroids.x, centroids.y, gdf_geojson_locations['Name']):
    ax.text(x, y, label, fontsize=12, ha='center', va='center', color='black', weight='bold')


# Add grid and labels
ax.grid(True, which='both', linestyle='-', linewidth=0.8)
ax.minorticks_on()
ax.grid(which='minor', linestyle=':', linewidth=0.4)
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

# Remove excessive margins
plt.subplots_adjust(left=0.05, right=0.975, top=0.975, bottom=0.05)

# Save plot with the MC2 tourist map as background
plt.savefig('./plots/map_abila_street_location_areas.png')

# Show plot
plt.show()
