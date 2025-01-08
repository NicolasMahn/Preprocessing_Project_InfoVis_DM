from mongo import DB
import json

mongo = DB("LocationCluster")

location_clusters_json_path = '../data/location_parking_cluster_matched_cleaned.json'

try:
    with open(location_clusters_json_path, "r", encoding="utf-8") as file:
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