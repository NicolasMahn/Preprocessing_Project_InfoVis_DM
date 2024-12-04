import json
import pandas as pd

# Load the JSON file for stops
with open('../data/carstops_in_cluster.json', 'r') as file:
    carstops_data = json.load(file)

# Load the CSV file for car assignments
car_assignments_df = pd.read_csv('../data/raw_data/car-assignments.csv')

# Convert CarID to string for matching
car_assignments_df['CarID'] = car_assignments_df['CarID'].astype(str).str.strip()

# Handle non-finite values in CarID
car_assignments_df['CarID'] = pd.to_numeric(car_assignments_df['CarID'], errors='coerce')
car_assignments_df = car_assignments_df.dropna(subset=['CarID'])
car_assignments_df['CarID'] = car_assignments_df['CarID'].astype(int).astype(str)

# Create a dictionary for quick lookup
car_assignments_dict = car_assignments_df.set_index('CarID').to_dict('index')

# Match car_id in carstops_data to CarID in car_assignments_dict
matched_data = {}
for cluster_id, stops in carstops_data.items():
    matched_stops = []
    for stop in stops:
        car_id = str(stop['car_id'])
        if car_id in car_assignments_dict:
            stop.update(car_assignments_dict[car_id])
        matched_stops.append(stop)
    matched_data[cluster_id] = matched_stops

# Save the matched data to a JSON file
with open('../data/carstops_cluster_with_employees.json', 'w') as file:
    json.dump(matched_data, file, indent=4)