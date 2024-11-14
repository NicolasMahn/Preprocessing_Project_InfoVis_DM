import json
from shapely.geometry import shape, LineString, Polygon, MultiPolygon
import matplotlib.pyplot as plt
import contextily as ctx
import geopandas as gpd

# Load GeoJSON data
geojson_path = '../data/abila_2.geojson'
with open(geojson_path) as f:
    geojson_data = json.load(f)

# Define the array of street names to display
desired_street_names = ["Pilau Street", "Parla Street", "Spetson Street", "Taxiarchon Avenue", "Carnero Street", "Rist Way",
    "Barwyn Street", "Arkadiou Street", "Velestinou Boulevard", "Alfou Street",
    "Androutsou Street", "Ermou Street", "Egeou Avenue", "Ipsilonut Avenue"]

# Extract geometries and properties
geometries = []
street_names = []
for feature in geojson_data['features']:
    geometry = feature['geometry']
    street_name = feature['properties']['Name']

    # Check if coordinates exist and contain sufficient points
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

# Create a GeoDataFrame and reproject to EPSG:3857
gdf = gpd.GeoDataFrame({'geometry': geometries, 'Name': street_names}, crs="EPSG:4326")
gdf = gdf.to_crs(epsg=3857)

# Plot the geometries
fig, ax = plt.subplots(figsize=(10, 10))
for geom, name in zip(gdf.geometry, gdf.Name):
    if isinstance(geom, Polygon):
        x, y = geom.exterior.xy
        ax.fill(x, y, color='blue', alpha=0.5)
    elif isinstance(geom, LineString):
        x, y = geom.xy
        ax.plot(x, y, color='blue')

    if name in desired_street_names:
        centroid = geom.centroid
        ax.text(centroid.x, centroid.y, name, fontsize=8, ha='right')

# Add basemap
ctx.add_basemap(ax, crs=gdf.crs)

# Show plot
plt.show()