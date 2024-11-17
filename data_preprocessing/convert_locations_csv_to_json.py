import csv
import json

# Pfade anpassen
input_csv = "../data/locations.csv"  # Name deiner CSV-Datei
output_geojson = "../data/locations.geojson"

# GeoJSON-Grundstruktur
geojson = {
    "type": "FeatureCollection",
    "features": []
}

# CSV einlesen und in GeoJSON umwandeln
with open(input_csv, "r", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=";")
    for row in reader:
        # Name und Koordinaten auslesen
        name = row["location"]
        coordinates = json.loads(row["coordinates"])  # Wandelt die Koordinaten von JSON-ähnlichem String in Liste um

        # Feature erstellen
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

# GeoJSON-Datei speichern
with open(output_geojson, "w", encoding="utf-8") as geojsonfile:
    json.dump(geojson, geojsonfile, ensure_ascii=False, indent=4)

print(f"GeoJSON-Datei erfolgreich erstellt: {output_geojson}")
