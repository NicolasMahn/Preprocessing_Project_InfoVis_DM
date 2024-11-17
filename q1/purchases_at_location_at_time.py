from mongo import DB
import load_data
import datetime

def main():
    cc_data = load_data.open_csv_file("../data/cc_data.csv")
    loyalty_data = load_data.open_csv_file("../data/loyalty_data.csv")
    """
    print(cc_data[0])
    print(cc_data[1][0])
    print(cc_data[1][1])
    print()
    print(loyalty_data[0])
    print(loyalty_data[1][0])
    print(loyalty_data[1][1])
    """
    dates = {}
    for row in cc_data[1]:
        date = row[0].date()
        if date in dates and "cc" in dates[date]:
            dates[date]["cc"].append(row)
        elif date in dates:
            dates[date]["cc"] = [row]
        else:
            dates[date] = {"cc": [row]}

    for row in loyalty_data[1]:
        date = row[0].date()
        if date in dates and "loyalty" in dates[date]:
            dates[date]["loyalty"].append(row)
        elif date in dates:
            dates[date]["loyalty"] = [row]
        else:
            dates[date] = {"loyalty": [row]}


    loyalty_cc_pairs = set()
    found_pairs = set()
    no_pair_found_cc = set()
    no_pair_found_loyalty = set()
    for v in dates.values():
        for cc_data in v["cc"]:
            for loyalty_data in v["loyalty"]:
                if cc_data[1] == loyalty_data[1]:
                    if cc_data[2] == loyalty_data[2]:
                        loyalty_cc_pairs.add((cc_data[3], loyalty_data[3]))
                        found_pairs.add(cc_data[3])
                        found_pairs.add(loyalty_data[3])

        for cc_data in v["cc"]:
            if cc_data[3] not in found_pairs:
                no_pair_found_cc.add(cc_data[3])

        for loyalty_data in v["loyalty"]:
            if loyalty_data[3] not in found_pairs:
                no_pair_found_loyalty.add(loyalty_data[3])

    #check if pairs unique
    cc = []
    loyalty = []
    double_appearence_cc = set()
    double_appearence_loyalty = set()
    for pair in loyalty_cc_pairs:
        if pair[0] in cc:
            # print(f"CC in more then one pair: {[p for p in loyalty_cc_pairs if p[0] == pair[0]]}")
            double_appearence_cc.add(pair[0])
        else:
            cc.append(pair[0])
        if pair[1] in loyalty:
            # print(f"Loyalty in more then one pair: {[p for p in loyalty_cc_pairs if p[1] == pair[1]]}")
            double_appearence_loyalty.add(pair[1])
        else:
            loyalty.append(pair[1])

    print("Double appearence in cc:")
    print(double_appearence_cc)
    print("Double appearence in loyalty:")
    print(double_appearence_loyalty)

    print()
    print("Pairs found:")
    print(loyalty_cc_pairs)
    print(len(loyalty_cc_pairs))
    print()
    print("No pair found in cc:")
    print(no_pair_found_cc)
    print()
    print("No pair found in loyalty:")
    print(no_pair_found_loyalty)

    return

    mongo = DB("purchases_at_location_at_time")
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