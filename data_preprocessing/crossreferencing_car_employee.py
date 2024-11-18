import pandas as pd
import json
from rapidfuzz.fuzz import ratio  # Für Ähnlichkeitsprüfung

# 1. CSV-Datei laden
cc_data = pd.read_csv('../data/cc_location_data.csv')

# 2. JSON-Datei laden
with open('../data/stops_in_locations.json') as f:
    stops_data = json.load(f)

# JSON-Daten normalisieren
stops_df = pd.json_normalize(stops_data)

# 3. Konvertierung der Timestamps in datetime
cc_data['timestamp'] = pd.to_datetime(cc_data['timestamp'], errors='coerce')
stops_df['start_time'] = pd.to_datetime(stops_df['start_time'], errors='coerce')
stops_df['end_time'] = pd.to_datetime(stops_df['end_time'], errors='coerce')

# Ungültige Zeilen entfernen
cc_data.dropna(subset=['timestamp'], inplace=True)
stops_df.dropna(subset=['start_time', 'end_time'], inplace=True)

# 4. Paare prüfen und sammeln
filtered_data = []
SIMILARITY_THRESHOLD = 80  # Mindestähnlichkeitswert (0-100)

for _, cc_row in cc_data.iterrows():
    for _, stop_row in stops_df.iterrows():
        # Prüfen, ob der Timestamp im Bereich liegt
        if stop_row['start_time'] <= cc_row['timestamp'] <= stop_row['end_time']:
            # Prüfen, ob location und location_name ähnlich sind
            similarity = ratio(cc_row['location'], stop_row['location_name'])
            if similarity >= SIMILARITY_THRESHOLD:
                filtered_data.append({
                    'timestamp': cc_row['timestamp'],
                    'price': cc_row['price'],
                    'last4ccnum': cc_row['last4ccnum'],
                    'start_time': stop_row['start_time'],
                    'end_time': stop_row['end_time'],
                    'location_name': stop_row['location_name'],
                    'similarity': similarity  # Ähnlichkeitswert speichern (optional)
                })

# 5. Ergebnisse in DataFrame umwandeln und speichern
final_filtered_data = pd.DataFrame(filtered_data)
final_filtered_data.to_csv('../data/merged_card_car_data.csv', index=False)

print("Merged data saved to '../data/merged_card_car_data.csv'")
