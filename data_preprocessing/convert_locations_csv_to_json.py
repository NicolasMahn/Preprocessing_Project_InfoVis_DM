import csv
import json

# Paths
input_csv = '../data/locations.csv'  # Name of your CSV file
output_geojson = '../data/locations.geojson'

# GeoJSON base structure
geojson = {
    "type": "FeatureCollection",
    "features": []
}

# Read CSV and convert to GeoJSON
with open(input_csv, 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';')
    for row in reader:
        # Read name and coordinates
        name = row['location']
        coordinates = json.loads(row['coordinates'])  # Convert coordinates from JSON-like string to list

        # Create feature
        feature = {
            "type": "Feature",
            "properties": {
                "name": name
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coordinates]
            }
        }
        geojson["features"].append(feature)

# Save GeoJSON file (overwrite if exists)
with open(output_geojson, 'w', encoding='utf-8') as geojsonfile:
    json.dump(geojson, geojsonfile, ensure_ascii=False, indent=4)

print(f"GeoJSON file successfully created: {output_geojson}")