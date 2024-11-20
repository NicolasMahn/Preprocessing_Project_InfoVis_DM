import json
from datetime import datetime


def unify_date_format(input_file, output_file, target_format='%Y-01-%d %H:%M:%S'):
    """
    Vereinheitlicht das Datumsformat in einer JSON-Datei.

    Args:
        input_file (str): Pfad zur Eingabedatei (JSON).
        output_file (str): Pfad zur Ausgabedatei (JSON).
        target_format (str): Ziel-Datumsformat (Standard: '%Y-%m-%d %H:%M:%S').
    """
    # Liste der möglichen Datumsformate
    possible_formats = [
        '%Y-%d-01 %H:%M:%S',
        '01/%d/%Y %H:%M:%S',
        '%d-01-%Y %H:%M:%S',
        '%d/01/%Y %H:%M:%S',
        '%Y-%d-01 %H:%M:%S'
    ]

    def parse_and_format_date(date_string):
        """Versucht, ein Datum zu parsen und ins Ziel-Format umzuwandeln."""
        for fmt in possible_formats:
            try:
                return datetime.strptime(date_string, fmt).strftime(target_format)
            except ValueError:
                continue
        raise ValueError(f"Unbekanntes Datumsformat: {date_string}")

    # Datei laden
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Daten verarbeiten
    for id_, entries in data.items():
        for entry in entries:
            entry[0] = parse_and_format_date(entry[0])  # Erster Eintrag ist das Datum

    # Datei speichern
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Datumsformat in {output_file} vereinheitlicht.")


# Beispielaufruf
unify_date_format('../../data/raw_data/gps_sorted_by_id.json', '../data/gps_sorted_by_id_2.json')
