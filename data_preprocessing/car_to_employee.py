import json
import pandas as pd

# Load the JSON file for stops
with open('../data/stops_per_car.json', 'r') as file:
    stops_data = json.load(file)

# Convert stops data to DataFrame
stops_list = []
for car_id, events in stops_data.items():
    for event in events:
        event['car_id'] = car_id
        stops_list.append(event)
stops_df = pd.DataFrame(stops_list)

# Ensure car_id is of type string
stops_df['car_id'] = stops_df['car_id'].astype(str)

# Display the first few rows of the stops DataFrame to check the data
print("Stops DataFrame:")
print(stops_df.head())

# Load the CSV file for car assignments
car_assignments_df = pd.read_csv('../data/raw_data/car-assignments.csv')

# Display the first few rows of the car assignments DataFrame to check the data
print("Car Assignments DataFrame:")
print(car_assignments_df.head())

# Ensure CarID is of type string
car_assignments_df['CarID'] = car_assignments_df['CarID'].astype(str)

# Merge the data on car_id
merged_df = pd.merge(stops_df, car_assignments_df, left_on='car_id', right_on='CarID', how='left')

# Display the first few rows of the merged DataFrame to check the data
print("Merged DataFrame:")
print(merged_df.head())

# Save the merged data to a CSV file
merged_df.to_csv('../data/merged_car_employee.csv', index=False)