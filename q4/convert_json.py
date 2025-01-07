import json

# Datei laden
file_path = '../data/location_parking_cluster_matched.json'
with open(file_path, 'r') as f:
    data = json.load(f)

# Bereinigung der Daten
for cluster in data:
    geometry = cluster.get('geometry')
    if geometry:
        if 'coordinates' in geometry:
            if not isinstance(geometry['coordinates'], list):
                print(f"Ungültige Geometrie: {geometry}")
                cluster['geometry'] = None  # Entferne die fehlerhafte Geometrie
            elif geometry['type'] == 'Polygon' and not isinstance(geometry['coordinates'][0], list):
                print(f"Korrigiere Polygon: {geometry}")
                cluster['geometry']['coordinates'] = [[geometry['coordinates']]]
            elif geometry['type'] == 'MultiPolygon' and not isinstance(geometry['coordinates'][0][0], list):
                print(f"Korrigiere MultiPolygon: {geometry}")
                cluster['geometry']['coordinates'] = [[geometry['coordinates']]]

# Datei speichern
cleaned_file_path = '../data/location_parking_cluster_matched_cleaned.json'
with open(cleaned_file_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"Bereinigte Datei gespeichert unter: {cleaned_file_path}")
