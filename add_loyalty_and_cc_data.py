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

    mongo = DB("num_purchases_per_location")#
    numb_purchases_per_location_cc = get_purchases_per_location(cc_data)
    print(mongo.insert_one_replace_if_exists({"cc_data": numb_purchases_per_location_cc}, "cc_data"))
    print(mongo.find({"cc_data": {"$exists": True}}))
    numb_purchases_per_location_loyalty = get_purchases_per_location(loyalty_data)
    print(mongo.insert_one_replace_if_exists({"loyalty_data": numb_purchases_per_location_loyalty}, "loyalty_data"))
    print(mongo.find({"loyalty_data": {"$exists": True}}))


if __name__ == "__main__":
    main()