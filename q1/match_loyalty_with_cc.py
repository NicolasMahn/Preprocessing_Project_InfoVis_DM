from mongo import DB
import load_data
import datetime
import util

def sort_data_by_date(date_dict, data, type):
    for row in data[1]:
        date = row[0].date()
        if date in date_dict and type in date_dict[date]:
            date_dict[date][type].append(row)
        elif date in date_dict:
            date_dict[date][type] = [row]
        else:
            date_dict[date] = {type: [row]}
    return date_dict


def extract_complex_pairs(loyalty_cc_pairs):
    cc = []
    loyalty = []
    complex_pairs = set()
    loyalty_cc_pairs_copy = list(loyalty_cc_pairs.copy())
    for pair in loyalty_cc_pairs_copy:
        complex_pairs, loyalty_cc_pairs, cc = extract_complex_pair(pair[0], pair, complex_pairs, loyalty_cc_pairs,
                                                                   loyalty_cc_pairs_copy, cc)
        complex_pairs, loyalty_cc_pairs, loyalty = extract_complex_pair(pair[1], pair, complex_pairs, loyalty_cc_pairs,
                                                                        loyalty_cc_pairs_copy, loyalty)
    return complex_pairs, loyalty_cc_pairs


def extract_complex_pair(pair_part, pair, complex_pairs, loyalty_cc_pairs, loyalty_cc_pairs_copy, cards):
    if pair_part in cards:
        for i in complex_pairs:
            if pair_part in i:
                continue
        cp = set(pair)
        l = 0
        while l != len(cp):
            l = len(cp)
            for j in range(len(cp)):
                for k in loyalty_cc_pairs_copy:
                    if list(cp)[j] == k[0] or list(cp)[j] == k[1]:
                        cp.add(k[0])
                        cp.add(k[1])
                        if k in loyalty_cc_pairs:
                            loyalty_cc_pairs.remove(k)
        complex_pairs.add(tuple(cp))
    else:
        cards.append(pair_part)

    return complex_pairs, loyalty_cc_pairs, cards


def get_cc_loyalty_pairs(cc_data, loyalty_data):
    dates = sort_data_by_date({}, cc_data, "cc")
    dates = sort_data_by_date(dates, loyalty_data, "loyalty")

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

    complex_pairs, loyalty_cc_pairs = extract_complex_pairs(loyalty_cc_pairs)

    non_simple_cards = set()
    for cp in complex_pairs:
        for p in cp:
            non_simple_cards.add(p)

    simple_cards = set()
    for pair in loyalty_cc_pairs:
        for p in pair:
            simple_cards.add(p)

    return loyalty_cc_pairs, complex_pairs, no_pair_found_cc, no_pair_found_loyalty, simple_cards, non_simple_cards


def main():
    cc_data = load_data.open_csv_file("../data/cc_data.csv")
    loyalty_data = load_data.open_csv_file("../data/loyalty_data.csv")

    print(cc_data[0])
    print(cc_data[1][0])
    print(cc_data[1][1])
    print()
    print(loyalty_data[0])
    print(loyalty_data[1][0])
    print(loyalty_data[1][1])


    loyalty_cc_pairs, complex_pairs, no_pair_found_cc, no_pair_found_loyalty, simple_cards, non_simple_cards = (
        get_cc_loyalty_pairs(cc_data, loyalty_data))


    cleaned_card_data = []
    for pair in loyalty_cc_pairs:
        index = next(i for i, row in enumerate(cc_data[1]) if row[3] == pair[0])
        cleaned_card_data.append([cc_data[1][index][0], cc_data[1][index][1], cc_data[1][index][2], pair[0], pair[1]])
    cleaned_card_data = [["date", "location", "price", "last4ccnum", "loyaltynum"]] + cleaned_card_data
    util.save_csv(cleaned_card_data, "../data/cleaned_card_data.csv")

    sketchy_card_data = []
    for card in non_simple_cards:
        cc_index = [i for i, row in enumerate(cc_data[1]) if row[3] == card]
        if len(cc_index) > 1:
            cc_index = cc_index[0]
            sketchy_card_data.append([cc_data[1][cc_index][0], cc_data[1][cc_index][1], cc_data[1][cc_index][2],
                                      card, None])

    for card in non_simple_cards:
        loyalty_index = [i for i, row in enumerate(loyalty_data[1]) if row[3] == card]
        if len(loyalty_index) > 1:
            loyalty_index = loyalty_index[0]
            if loyalty_data[1][loyalty_index][0] in [i[0].date() for i in sketchy_card_data] \
                and loyalty_data[1][loyalty_index][1] in [i[1] for i in sketchy_card_data] \
                and loyalty_data[1][loyalty_index][2] in [i[2] for i in sketchy_card_data]:
                index = next(i for i, row in enumerate(sketchy_card_data)
                             if row[0] == loyalty_data[1][loyalty_index][0].date()
                             and row[1] == loyalty_data[1][loyalty_index][1]
                             and row[2] == loyalty_data[1][loyalty_index][2])
                sketchy_card_data[index][4] = card
            else:
                sketchy_card_data.append([loyalty_data[1][loyalty_index][0], loyalty_data[1][loyalty_index][1],
                                          loyalty_data[1][loyalty_index][2], None, card])
    cleaned_card_data = [["date", "location", "price", "last4ccnum", "loyaltynum"]] + cleaned_card_data
    util.save_csv(cleaned_card_data, "../data/sketchy_card_data.csv")
    print(sketchy_card_data)




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