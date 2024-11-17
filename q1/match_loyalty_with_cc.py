from mongo import DB
import load_data
import datetime
import util
import matplotlib.pyplot as plt

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


def get_purchases_per_location(data):
    location_counts = {}
    for row in data:
        location = row[1]  # Assuming 'location' is the second column
        if location in location_counts:
            location_counts[location] += 1
        else:
            location_counts[location] = 1
    return location_counts

def plot_percent_sketchy_vs_cleaned_location(card_location_data, type_):
    locations = list(card_location_data.keys())
    percent_cleaned = [card_location_data[loc][f"{type_}_cleaned"] for loc in locations]
    percent_sketchy = [card_location_data[loc][f"{type_}_sketchy"] for loc in locations]

    x = range(len(locations))

    fig, ax = plt.subplots(figsize=(10, 6))

    bar_width = 0.35
    bar1 = ax.bar(x, percent_cleaned, bar_width, label=f"{type_} Cleaned")
    bar2 = ax.bar([i + bar_width for i in x], percent_sketchy, bar_width, label=f"{type_} Sketchy")

    ax.set_xlabel('Location')
    ax.set_ylabel(type_)
    ax.set_title('Comparison of Sketchy vs Legitimate Purchases at Locations')
    ax.set_xticks([i + bar_width / 2 for i in x])
    ax.set_xticklabels(locations, rotation=45, ha='right')
    ax.legend()

    plt.tight_layout()
    plt.show()


def main():
    cc_data = load_data.open_csv_file("../data/cc_data.csv")
    loyalty_data = load_data.open_csv_file("../data/loyalty_data.csv")


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
    sketchy_card_data = [["date", "location", "price", "last4ccnum", "loyaltynum"]] + sketchy_card_data
    util.save_csv(sketchy_card_data, "../data/sketchy_card_data.csv")

    print(cleaned_card_data[0])
    print(cleaned_card_data[1])
    print(cleaned_card_data[2])
    print(cleaned_card_data[3])
    print()
    print(sketchy_card_data[0])
    print(sketchy_card_data[1])
    print(sketchy_card_data[2])
    print(sketchy_card_data[3])

    cleaned_card_location_data = get_purchases_per_location(cleaned_card_data)
    sketchy_card_location_data = get_purchases_per_location(sketchy_card_data)

    sum_locations_clen = sum(cleaned_card_location_data.values())
    sum_locations_sketchy = sum(sketchy_card_location_data.values())

    card_location_data = {}
    for location, num in cleaned_card_location_data.items():
        avg_sketchy_amount = []
        for row in sketchy_card_data:
            if row[0] == "date":
                continue
            if row[1] == location:
                avg_sketchy_amount.append(row[2])
        if len(avg_sketchy_amount) == 0:
            avg_sketchy_amount = 0
        else:
            avg_sketchy_amount = sum(avg_sketchy_amount)/len(avg_sketchy_amount)

        avg_cleaned_amount = []
        for row in cleaned_card_data:
            if row[0] == "date":
                continue
            if row[1] == location:
                avg_cleaned_amount.append(row[2])
        if len(avg_cleaned_amount) == 0:
            avg_cleaned_amount = 0
        else:
            avg_cleaned_amount = sum(avg_cleaned_amount)/len(avg_cleaned_amount)

        card_location_data[location] =  {
            "absolut_cleaned": num,
            "absolut_sketchy": sketchy_card_location_data.get(location, 0),
            "percent_cleaned": num/sum_locations_clen,
            "percent_sketchy": sketchy_card_location_data.get(location, 0)/sum_locations_sketchy,
            "avg_amount_cleaned": avg_cleaned_amount,
            "avg_amount_sketchy": avg_sketchy_amount
        }

    plot_percent_sketchy_vs_cleaned_location(card_location_data, "percent")
    plot_percent_sketchy_vs_cleaned_location(card_location_data, "absolut")
    card_location_data.pop("Nationwide Refinery")
    card_location_data.pop("Abila Airport")
    card_location_data.pop("Abila Scrapyard")
    card_location_data.pop("Kronos Pipe and Irrigation")
    plot_percent_sketchy_vs_cleaned_location(card_location_data, "avg_amount")
    # mongo = DB("percent_location_comparison_sketchy_vs_cleaned")
    # mongo.delete_many({})





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