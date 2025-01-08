import json
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon, Polygon, mapping
from mongo import DB

# Load the JSON file
with open('../data/stops_in_location_clusters_employee.json', 'r') as file:
    carstops_data = json.load(file)

# Convert data to a DataFrame
data = []
for stop in carstops_data:
    data.append({
        'car_id': stop.get('car_id'),
        'LastName': stop.get('LastName'),
        'FirstName': stop.get('FirstName'),
        'CurrentEmploymentType': stop.get('CurrentEmploymentType'),
        'CurrentEmploymentTitle': stop.get('CurrentEmploymentTitle'),
        'start_time': pd.to_datetime(stop.get('start_time')),
        'end_time': pd.to_datetime(stop.get('end_time')),
        'duration_of_stop_min': stop.get('duration_of_stop_min'),
        'latitude': stop.get('start_coordinates')[0],
        'longitude': stop.get('start_coordinates')[1],
        'location': stop.get('location')
    })

df = pd.DataFrame(data)

# Helper function to check time overlap
def has_overlap(group):
    for i, row1 in group.iterrows():
        for j, row2 in group.iterrows():
            if i >= j:
                continue
            overlap = (row1['start_time'] < row2['end_time'] and row2['start_time'] < row1['end_time'])
            overlap_duration = min(row1['end_time'], row2['end_time']) - max(row1['start_time'], row2['start_time'])
            if overlap and overlap_duration.total_seconds() >= 300:  # Minimum 5 minutes overlap
                return True
    return False

# Helper function to count repetitions of a cluster
def count_cluster_repetitions(cluster, all_clusters):
    cluster_set = frozenset([entry['car_id'] for entry in cluster])
    count = 0
    for other_cluster in all_clusters:
        other_cluster_set = frozenset([entry['car_id'] for entry in other_cluster])
        if cluster_set == other_cluster_set:
            count += 1
    return count

# Group by location and filter clusters with at least 2 overlapping entries
grouped = df.groupby('location')
result = []
seen_clusters = set()
all_clusters = []
cluster_id_counter = 1

for location, group in grouped:
    if location == "Gastech":
        continue

    group = group.sort_values(by='start_time')
    overlapping_entries = []

    for _, row in group.iterrows():
        overlapping = False
        for entry in overlapping_entries:
            overlap = (row['start_time'] < entry['end_time'] and entry['start_time'] < row['end_time'])
            overlap_duration = min(row['end_time'], entry['end_time']) - max(row['start_time'], entry['start_time'])
            if overlap and overlap_duration.total_seconds() >= 300:  # Minimum 5 minutes overlap
                overlapping = True
                break

        if overlapping or not overlapping_entries:
            overlapping_entries.append(row)

    if len(overlapping_entries) > 1 and has_overlap(pd.DataFrame(overlapping_entries)):
        cluster = []
        for entry in overlapping_entries:
            cluster.append({
                'car_id': entry['car_id'],
                'LastName': entry['LastName'],
                'FirstName': entry['FirstName'],
                'CurrentEmploymentType': entry['CurrentEmploymentType'],
                'CurrentEmploymentTitle': entry['CurrentEmploymentTitle'],
                'start_time': str(entry['start_time']),
                'end_time': str(entry['end_time']),
                'duration_of_stop_min': entry['duration_of_stop_min'],
                'latitude': entry['latitude'],
                'longitude': entry['longitude']
            })

        cluster_key = frozenset([entry['car_id'] for entry in overlapping_entries])
        repetitions = count_cluster_repetitions(cluster, all_clusters)

        if cluster_key not in seen_clusters:
            seen_clusters.add(cluster_key)
            all_clusters.append(cluster)
            result.append({
                'cluster_id': cluster_id_counter,
                'location': location,
                'cluster': cluster
            })
            cluster_id_counter += 1

# Save the results to JSON files
with open('../data/stops_same_location_time_employee.json', 'w') as outfile:
    json.dump(result, outfile, indent=4)

# Export data for frontend use
map_data = []
for cluster in result:
    for entry in cluster['cluster']:
        map_data.append({
            'cluster_id': cluster['cluster_id'],
            'location': cluster['location'],
            'latitude': entry['latitude'],
            'longitude': entry['longitude'],
            'car_id': entry['car_id'],
            'LastName': entry['LastName'],
            'FirstName': entry['FirstName'],
            'CurrentEmploymentType': entry['CurrentEmploymentType'],
            'CurrentEmploymentTitle': entry['CurrentEmploymentTitle'],
            'start_time': entry['start_time'],
            'end_time': entry['end_time']
        })

# Plotting the clusters
latitudes = [entry['latitude'] for entry in map_data]
longitudes = [entry['longitude'] for entry in map_data]
cluster_ids = [entry['cluster_id'] for entry in map_data]

plt.figure(figsize=(10, 6))
plt.scatter(longitudes, latitudes, c=cluster_ids, cmap='viridis', s=50, alpha=0.7, edgecolors='k')
plt.colorbar(label='Cluster ID')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Cluster Visualization')
plt.grid(True)
plt.show()


# Load the JSON file
with open('../data/stops_same_location_time_employee.json', 'r') as file:
    clusters_data = json.load(file)

# Process the data to create MultiPolygons for each cluster
result = []
for cluster in clusters_data:
    coordinates = [(entry['longitude'], entry['latitude']) for entry in cluster['cluster']]
    if len(coordinates) > 2:
        polygon = Polygon(coordinates)
        multipolygon = MultiPolygon([polygon])
    else:
        multipolygon = None  # Not enough points to form a polygon

    cluster_info = {
        'cluster_id': cluster['cluster_id'],
        'location': cluster['location'],
        'employees': cluster['cluster'],
        'geometry': mapping(multipolygon) if multipolygon else None
    }
    result.append(cluster_info)

# Save the result to a new JSON file
with open('../data/employee_clusters_with_geometry.json', 'w') as outfile:
    json.dump(result, outfile, indent=4)


mongo = DB("EmployeeCluster")

employee_clusters_json_path = '../data/employee_clusters_with_geometry.json'

try:
    with open(employee_clusters_json_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Lädt die JSON-Datei

        # Überprüfen, ob die Datei ein Objekt oder eine Liste enthält
        if isinstance(data, list):
            mongo.insert_many(data)  # Bei einer Liste von Dokumenten
        else:
            mongo.insert_one(data)  # Bei einem einzelnen Dokument

        print("Daten erfolgreich in die MongoDB eingefügt!")
except Exception as e:
    print(f"Fehler beim Importieren der Daten: {e}")

print(mongo.find_all())