from mongo import DB
import load_data

def get_purchases_per_location(data):
    location_counts = {}
    for row in data[1]:
        location = row[1]  # Assuming 'location' is the second column
        if location in location_counts:
            location_counts[location] += 1
        else:
            location_counts[location] = 1
    return location_counts


def main():
    cc_data = load_data.open_csv_file("data/cc_data.csv")
    loyalty_data = load_data.open_csv_file("data/loyalty_data.csv")

    mongo = DB("num_purchases_per_location")
    mongo.delete_many({})
    numb_purchases_per_location_cc = get_purchases_per_location(cc_data)
    numb_purchases_per_location_loyalty = get_purchases_per_location(loyalty_data)

    numb_purchases_per_location = []
    for location in (numb_purchases_per_location_loyalty.keys() | numb_purchases_per_location_cc.keys()):
        numb_purchases_per_location.append(
            {"location": location,
             "numb_purchases_cc": numb_purchases_per_location_cc.get(location, 0),
             "numb_purchases_loyalty": numb_purchases_per_location_loyalty.get(location, 0)})

    print(mongo.insert_many(numb_purchases_per_location))
    print(mongo.find_all())


if __name__ == "__main__":
    main()