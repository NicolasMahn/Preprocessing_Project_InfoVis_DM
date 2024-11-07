from load_data import open_csv_file
from collections import defaultdict
import json
import os
from datetime import datetime


def get_gps_data_sorted_by_id():
    original_gps_data_file = 'data/gps.csv'
    gps_data_sorted_by_id_file = 'data/gps_sorted_by_id.json'

    if os.path.exists(gps_data_sorted_by_id_file):
        return load_gps_data_sorted_by_id(gps_data_sorted_by_id_file)
    else:
        sorted_gps_dict = create_gps_data_sorted_by_id(original_gps_data_file)
        save_gps_data_sorted_by_id(sorted_gps_dict, gps_data_sorted_by_id_file)
        return sorted_gps_dict


def create_gps_data_sorted_by_id(original_gps_data_file):
    gps_labels, gps_data, _ = open_csv_file(original_gps_data_file)

    # Create a dictionary where each key is an id, and the value is a list of GPS entries
    gps_dict = defaultdict(list)

    # Loop through the gps_data and group by 'id'
    for entry in gps_data:
        gps_dict[entry[1]].append([entry[0], entry[2], entry[3]])  # Exclude the id (index 1)

    return gps_dict


def save_gps_data_sorted_by_id(sorted_gps_dict, gps_data_sorted_by_id_file):
    # Convert the defaultdict to a regular dict (JSON does not support defaultdict)
    gps_dict_normal = dict(sorted_gps_dict)

    # Save the data to a JSON file
    with open(gps_data_sorted_by_id_file, 'w') as json_file:
        json.dump(gps_dict_normal, json_file, default=str, indent=4)  # default=str to handle datetime


def load_gps_data_sorted_by_id(gps_data_sorted_by_id_file):
    # Load the data from the JSON file
    with open(gps_data_sorted_by_id_file, 'r') as json_file:
        loaded_data = json.load(json_file, object_hook=custom_datetime_parser)

    # Convert keys from strings to integers
    loaded_data = {int(key): value for key, value in loaded_data.items()}

    # Convert back to defaultdict if needed
    return defaultdict(list, loaded_data)


def custom_datetime_parser(dct):
    # Function to convert string back to datetime
    for key, value in dct.items():
        for entry in value:
            if isinstance(entry[0], str):
                # Try multiple datetime formats
                for fmt in ('%Y-%m-%d %H:%M:%S', '%m/%d/%Y %H:%M:%S'):
                    try:
                        entry[0] = datetime.strptime(entry[0], fmt)
                        break
                    except ValueError:
                        continue
    return dct
