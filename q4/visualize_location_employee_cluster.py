import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import shape, Polygon, MultiPolygon
import json

# Dateien laden
abila_geojson_path = '../data/raw_data/abila_2.geojson'
employee_clusters_json_path = '../data/employee_clusters_with_geometry.json'
location_cluster_json_path = '../data/location_parking_cluster_matched_cleaned.json'

# Abila GeoJSON laden
with open(abila_geojson_path) as f:
    geojson_data = json.load(f)

# Straßen definieren, die hervorgehoben werden sollen
desired_street_names = [
    "Rist Way", "Carnero St", "Barwyn St", "Arkadiou St", "Androutsou St",
    "Velestinou Blv", "Ermou St", "Egeou Av", "Ipsilantou Ave",
    "Pilau St", "Parla St", "Spetson St", "Taxiarchon Ave"
]

# Geometrien und Straßennamen extrahieren
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
            geom = shape(geometry)
            geometries.append(geom)
            street_names.append(street_name)

# GeoDataFrame erstellen
gdf = gpd.GeoDataFrame({'geometry': geometries, 'Name': street_names}, crs="EPSG:4326")

# Location-Cluster aus JSON laden
with open(location_cluster_json_path) as f:
    location_clusters = json.load(f)

# Employee-Cluster aus JSON laden
with open(employee_clusters_json_path) as f:
    employee_clusters = json.load(f)

# Plot erstellen
plt.figure(figsize=(12, 8))

# Straßen-Netzwerk plotten
for geom in gdf.geometry:
    if geom.geom_type == 'Polygon':
        x, y = geom.exterior.xy
        plt.fill(x, y, color='#D3D3D3', alpha=0.5)
    elif geom.geom_type == 'LineString':
        x, y = geom.xy
        plt.plot(x, y, color='#D3D3D3', linewidth=1)

# Location-Cluster als grüne Polygone plotten
for cluster in location_clusters:
    cluster_geometry = cluster.get('geometry')
    if cluster_geometry and 'coordinates' in cluster_geometry:
        try:
            poly = shape(cluster_geometry)
            if isinstance(poly, MultiPolygon):
                for sub_poly in poly.geoms:
                    x, y = sub_poly.exterior.xy
                    plt.fill(x, y, color='green', alpha=0.5)
            elif isinstance(poly, Polygon):
                x, y = poly.exterior.xy
                plt.fill(x, y, color='green', alpha=0.5)
        except Exception as e:
            print(f"Fehler bei Location-Cluster: {e}")

# Employee-Cluster als rote Polygone plotten
for cluster in employee_clusters:
    cluster_geometry = cluster.get('geometry')
    if cluster_geometry and 'coordinates' in cluster_geometry:
        try:
            poly = shape(cluster_geometry)
            if isinstance(poly, MultiPolygon):
                for sub_poly in poly.geoms:
                    x, y = sub_poly.exterior.xy
                    plt.fill(x, y, color='red', alpha=0.5)
            elif isinstance(poly, Polygon):
                x, y = poly.exterior.xy
                plt.fill(x, y, color='red', alpha=0.5)
        except Exception as e:
            print(f"Fehler bei Employee-Cluster: {e}")

plt.title('Park- und Employee-Cluster mit Straßennetzwerk')
plt.xlabel('Längengrad')
plt.ylabel('Breitengrad')
plt.show()
