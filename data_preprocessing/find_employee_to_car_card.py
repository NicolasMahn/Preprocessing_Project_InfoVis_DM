# find employee to a car-card pair
import pandas as pd

# Load the most_used_cards_per_car.csv file
most_used_cards = pd.read_csv('../data/most_used_cards_per_car.csv')

# Filter out card numbers that are not unique to the car ID
unique_cards = most_used_cards.groupby('most_used_card').filter(lambda x: len(x) == 1)

# Print the filtered-out data to the console
filtered_out_data = most_used_cards[~most_used_cards['most_used_card'].isin(unique_cards['most_used_card'])]
print("Filtered out data:")
print(filtered_out_data)

# Load the car_assignment.csv file
car_assignment = pd.read_csv('../data/raw_data/car-assignments.csv')

# Merge the filtered data with the car assignment data on the car ID
merged_data = unique_cards.merge(car_assignment, left_on='car_id',right_on='CarID', how='left')

merged_data = merged_data.drop(columns=['CarID'])

# Save the merged data to a new CSV file
merged_data.to_csv('../data/car_card_to_employee.csv', index=False)

print("Filtered and merged data saved to '../data/car_card_to_employee.csv'")