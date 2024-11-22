import pandas as pd
from collections import Counter

# Load the merged data
merged_data_cc = pd.read_csv(f'../data/merged_cc_data_car_data_cluster.csv')
merged_data_ccd = pd.read_csv(f'../data/merged_cleaned_card_data_car_data_cluster.csv')

locations = merged_data_ccd['location'].unique()

most_common_cc = {}

for row in merged_data_cc.iterrows():
    # print(row[1])
    if row[1][4] not in most_common_cc.keys():
        most_common_cc[row[1][4]] = {}
    if row[1][1] not in most_common_cc[row[1][4]].keys():
        most_common_cc[row[1][4]][row[1][1]] = 1
    else:
        most_common_cc[row[1][4]][row[1][1]] += 1

for row in merged_data_ccd.iterrows():
    # print(row[1])
    if row[1][4] not in most_common_cc.keys():
        most_common_cc[row[1][4]] = {}
    if row[1][1] not in most_common_cc[row[1][4]].keys():
        most_common_cc[row[1][4]][row[1][1]] = 1
    else:
        most_common_cc[row[1][4]][row[1][1]] += 1


for car, ccs in most_common_cc.items():
    sorted_ccs = dict(sorted(ccs.items(), key=lambda item: item[1], reverse=True))
    print(f"{car}: {sorted_ccs}")

# find if there is a card overlap of the most common card over all cars
cards = dict()

for car, ccs in most_common_cc.items():
    most_common_ccs = max(ccs, key=ccs.get)
    if most_common_ccs not in cards.keys():
        cards[most_common_ccs] = {"occurrences": 1, "cars": [car]}
    else:
        cards[most_common_ccs]["occurrences"] += 1
        cards[most_common_ccs]["cars"].append(car)

for card in cards:
    print(f"{card}: {cards[card]}")

cars = dict()

for card, data in cards.items():
    for car in data["cars"]:
        if car not in cars.keys():
            cars[car] = {"cards": [card]}
        else:
            cars[car]["cards"].append(card)

for car in cars:
    print(f"{car}: {cars[car]}")

