from random import random

from mongo import DB
import load_data
import datetime
import util
import matplotlib.pyplot as plt

def get_purchases_per_location_original(data):
    location_counts = {}
    for row in data[1]:
        location = row[1]  # Assuming 'location' is the second column
        if location in location_counts:
            location_counts[location] += 1
        else:
            location_counts[location] = 1
    return location_counts

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


def natural_number_coincidence_test(pair, cc_data, loyalty_data, cc, loyalty):
    # print(f"Complex pairs interactions {i}: {pair}")

    for p in pair:
        ds = []
        if p in cc:
            for ccd in cc_data[1]:
                if ccd[3] == p:
                    ds.append(ccd)
                    # print(f"cc: {ccd}")
        if p in loyalty:
            for ld in loyalty_data[1]:
                if ld[3] == p:
                    ds.append(ld)
                    # print(f"loyalty: {ld}")
        total_cp_count = set()
        pair_count = {}
        for p_sub in pair:
            if p_sub != p:
                pp_count = 0
                for d in ds:
                    for c_ccd in cc_data[1]:
                        if (d[0].date() == c_ccd[0].date() and d[1] == c_ccd[1] and d[2] == c_ccd[2] and
                                c_ccd[3] == p_sub):
                            cp_count = 2
                            c_pair = [p, p_sub]
                            for p_sub_sub in pair:
                                if p_sub_sub != p_sub and p_sub_sub != p:
                                    for c_ccd in cc_data[1]:
                                        if (d[0].date() == c_ccd[0].date() and d[1] == c_ccd[1] and d[2] ==
                                                c_ccd[2] and
                                                c_ccd[3] == p_sub_sub):
                                            cp_count += 1
                                            c_pair.append(p_sub_sub)
                                    for c_ld in loyalty_data[1]:
                                        if (d[0].date() == c_ld[0].date() and d[1] == c_ld[1] and
                                                d[2] == c_ld[2] and c_ld[3] == p_sub_sub):
                                            cp_count += 1
                                            c_pair.append(p_sub_sub)
                            if cp_count > 2:
                                # print(f"Complex pair count {p}: {cp_count}")
                                total_cp_count.add(tuple(c_pair))
                            pp_count += 1
                            continue
                    for c_ld in loyalty_data[1]:
                        if (d[0].date() == c_ld[0].date() and d[1] == c_ld[1] and d[2] == c_ld[2] and
                                c_ld[3] == p_sub):
                            cp_count = 2
                            c_pair = [p, p_sub]
                            for p_sub_sub in pair:
                                if p_sub_sub != p_sub and p_sub_sub != p:
                                    for c_ccd in cc_data[1]:
                                        if (d[0].date() == c_ccd[0].date() and d[1] == c_ccd[1] and d[2] ==
                                                c_ccd[2] and
                                                c_ccd[3] == p_sub_sub):
                                            cp_count += 1
                                            c_pair.append(p_sub_sub)
                                    for c_ld in loyalty_data[1]:
                                        if (d[0].date() == c_ld[0].date() and d[1] == c_ld[1] and
                                                d[2] == c_ld[2] and c_ld[3] == p_sub_sub):
                                            cp_count += 1
                                            c_pair.append(p_sub_sub)
                            if cp_count > 2:
                                # print(f"Complex pair found with {c_pair}")
                                total_cp_count.add(tuple(c_pair))
                            pp_count += 1
                pair_count[p_sub] = pp_count

        # print(f"Pair count {p}: {pair_count}")
    # print(total_cp_count)
    num = sum([1 / (len(tcc) - 1) for tcc in total_cp_count])
    return (isinstance(num, int) or (isinstance(num, float) and num.is_integer())) and num > 0


def extract_complex_pairs(loyalty_cc_pairs, cc_data, loyalty_data):
    cc = []
    loyalty = []
    complex_pairs = set()
    for pair in loyalty_cc_pairs:
        complex_pairs, removal_list, cc = extract_complex_pair(pair[0], pair, complex_pairs,
                                                               loyalty_cc_pairs, cc)
        complex_pairs, removal_list, loyalty = extract_complex_pair(pair[1], pair, complex_pairs,
                                                                    loyalty_cc_pairs, loyalty)

    complex_pairs_copy = complex_pairs.copy()
    for pair in complex_pairs_copy:
        if natural_number_coincidence_test(pair, cc_data, loyalty_data, cc, loyalty):
            if pair in complex_pairs:
                complex_pairs.remove(pair)
            for r_pair in removal_list.copy():
                for p in pair:
                    if p in r_pair and r_pair in removal_list:
                        removal_list.remove(r_pair)
    for r_pair in removal_list:
        loyalty_cc_pairs.remove(r_pair)

    return complex_pairs, loyalty_cc_pairs


def extract_complex_pair(pair_part, pair, complex_pairs, loyalty_cc_pairs, cards):
    removal_list = []
    if pair_part in cards:
        for i in complex_pairs:
            if pair_part in i:
                continue
        cp = set(pair)
        l = 0
        while l != len(cp):
            l = len(cp)
            for j in range(len(cp)):
                for k in loyalty_cc_pairs:
                    if list(cp)[j] == k[0] or list(cp)[j] == k[1]:
                        cp.add(k[0])
                        cp.add(k[1])
                        removal_list.append(k)
        complex_pairs.add(tuple(cp))
    else:
        cards.append(pair_part)

    return complex_pairs, removal_list, cards


def get_cc_loyalty_pairs(cc_data, loyalty_data):
    dates = sort_data_by_date({}, cc_data, "cc")
    dates = sort_data_by_date(dates, loyalty_data, "loyalty")

    loyalty_cc_pairs = set()
    found_pairs = set()
    no_pair_found_cc = set()
    no_pair_found_loyalty = set()
    for v in dates.values():
        for ccd in v["cc"]:
            for ld in v["loyalty"]:
                if ccd[1] == ld[1]:
                    if ccd[2] == ld[2]:
                        loyalty_cc_pairs.add((ccd[3], ld[3]))
                        found_pairs.add(ccd[3])
                        found_pairs.add(ld[3])

        for ccd in v["cc"]:
            if ccd[3] not in found_pairs:
                no_pair_found_cc.add(ccd[3])

        for ld in v["loyalty"]:
            if ld[3] not in found_pairs:
                no_pair_found_loyalty.add(ld[3])

    complex_pairs, loyalty_cc_pairs = extract_complex_pairs(loyalty_cc_pairs, cc_data, loyalty_data)

    sketchy_cards = set()
    for cp in complex_pairs:
        for p in cp:
            sketchy_cards.add(p)
    for npfc in no_pair_found_cc:
         sketchy_cards.add(npfc)
    for npfl in no_pair_found_loyalty:
         sketchy_cards.add(npfl)

    simple_cards = set()
    for pair in loyalty_cc_pairs:
        for p in pair:
            simple_cards.add(p)

    return loyalty_cc_pairs, complex_pairs, no_pair_found_cc, no_pair_found_loyalty, simple_cards, sketchy_cards


def get_purchases_per_location(data):
    location_counts = {}
    for row in data:
        if row[0] == "date":
            continue
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

    numb_purchases_per_location_cc = get_purchases_per_location_original(cc_data)
    numb_purchases_per_location_loyalty = get_purchases_per_location_original(loyalty_data)

    loyalty_cc_pairs, complex_pairs, no_pair_found_cc, no_pair_found_loyalty, simple_cards, sketchy_cards = (
        get_cc_loyalty_pairs(cc_data, loyalty_data))

    cleaned_card_data = []
    for pair in loyalty_cc_pairs:
        indices = [i for i, row in enumerate(cc_data[1]) if row[3] == pair[0]]
        for index in indices:
            cleaned_card_data.append([cc_data[1][index][0], cc_data[1][index][1], cc_data[1][index][2], pair[0], pair[1]])
    cleaned_card_data = [["date", "location", "price", "last4ccnum", "loyaltynum"]] + cleaned_card_data
    util.save_csv(cleaned_card_data, "../data/cleaned_card_data.csv")

    sketchy_card_data = []
    for card in sketchy_cards:
        cc_indices = [i for i, row in enumerate(cc_data[1]) if row[3] == card]
        for cc_index in cc_indices:
            sketchy_card_data.append([cc_data[1][cc_index][0], cc_data[1][cc_index][1], cc_data[1][cc_index][2],
                                      card, None])

    for card in sketchy_cards:
        loyalty_indices = [i for i, row in enumerate(loyalty_data[1]) if row[3] == card]
        for loyalty_index in loyalty_indices:
            scd_index = [i for i, row in enumerate(sketchy_card_data)
                         if row[0].date() == loyalty_data[1][loyalty_index][0].date()
                         and row[1] == loyalty_data[1][loyalty_index][1]
                         and row[2] == loyalty_data[1][loyalty_index][2]]
            if len(scd_index) > 1:
                sketchy_card_data[scd_index[0]][4] = card
            elif len(scd_index) > 0:
                sketchy_card_data[scd_index[0]][4] = card
            else:
                sketchy_card_data.append([loyalty_data[1][loyalty_index][0], loyalty_data[1][loyalty_index][1],
                                          loyalty_data[1][loyalty_index][2], None, card])
    sketchy_card_data = [["date", "location", "price", "last4ccnum", "loyaltynum"]] + sketchy_card_data
    util.save_csv(sketchy_card_data, "../data/sketchy_card_data.csv")

    """
    print(cleaned_card_data[0])
    print(cleaned_card_data[1])
    print(cleaned_card_data[2])
    print(cleaned_card_data[3])
    print()
    print(sketchy_card_data[0])
    if len(sketchy_card_data) > 1:
        print(sketchy_card_data[1])
    if len(sketchy_card_data) > 2:
        print(sketchy_card_data[2])
    if len(sketchy_card_data) > 3:
        print(sketchy_card_data[3])
    """

    cleaned_card_location_data = get_purchases_per_location(cleaned_card_data)
    sketchy_card_location_data = get_purchases_per_location(sketchy_card_data)

    sum_locations_clean = sum(cleaned_card_location_data.values())
    sum_locations_sketchy = sum(sketchy_card_location_data.values())
    sum_locations_cc = sum(numb_purchases_per_location_cc.values())
    sum_locations_loyalty = sum(numb_purchases_per_location_loyalty.values())

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

        if sum_locations_sketchy == 0:
            percent_sketchy = 0
        else:
            percent_sketchy = sketchy_card_location_data.get(location, 0)/sum_locations_sketchy


        purchases_per_location_cc = numb_purchases_per_location_cc.get(location, 0)
        avg_cc_amount = []
        for row in cc_data[1]:
            if row[0] == "date":
                continue
            if row[1] == location:
                avg_cc_amount.append(row[2])
        if len(avg_cc_amount) == 0:
            avg_cc_amount = 0
        else:
            avg_cc_amount = sum(avg_cc_amount)/len(avg_cc_amount)


        purchases_per_location_loyalty = numb_purchases_per_location_loyalty.get(location, 0)
        avg_loyalty_amount = []
        for row in loyalty_data[1]:
            if row[0] == "date":
                continue
            if row[1] == location:
                avg_loyalty_amount.append(row[2])
        if len(avg_loyalty_amount) == 0:
            avg_loyalty_amount = 0
        else:
            avg_loyalty_amount = sum(avg_loyalty_amount)/len(avg_loyalty_amount)


        # TODO: Add Car Card Pairs and Cars in Area
        # Cars in area mok
        car_card_pair = num
        for i in range(car_card_pair):
            if random() < 0.1:
                car_card_pair -= 1

        avg_car_card_amount = []
        for row in cleaned_card_data:
            if row[0] == "date":
                continue
            if row[1] == location and random() < 0.1:
                avg_car_card_amount.append(row[2])
        if len(avg_car_card_amount) == 0:
            avg_car_card_amount = 0
        else:
            avg_car_card_amount = sum(avg_car_card_amount)/len(avg_car_card_amount)
            



        card_location_data[location] =  {
            "absolut_cc": purchases_per_location_cc,
            "absolut_loyalty": purchases_per_location_loyalty,
            "absolut_cars_in_area": purchases_per_location_cc,
            "absolut_card_pair": num,
            "absolut_car_card_pair": car_card_pair,
            "absolut_no_car_card_pair": num - car_card_pair + sketchy_card_location_data.get(location, 0),
            "absolut_no_pair": sketchy_card_location_data.get(location, 0),
            "percent_cc": (purchases_per_location_cc/sum_locations_cc)*100,
            "percent_loyalty": (purchases_per_location_loyalty/sum_locations_loyalty)*100,
            "percent_cars_in_area": (purchases_per_location_cc/sum_locations_cc)*100,
            "percent_card_pair": (num/sum_locations_clean)*100,
            "percent_car_card_pair": (car_card_pair / sum_locations_clean) * 100,
            "percent_no_car_card_pair": ((num - car_card_pair + sketchy_card_location_data.get(location, 0)) / sum_locations_clean) * 100,
            "percent_no_pair": percent_sketchy*100,
            "avg_amount_cc": avg_cc_amount,
            "avg_amount_loyalty": avg_loyalty_amount,
            "avg_amount_cars_in_area": avg_cc_amount,
            "avg_amount_card_pair": avg_cleaned_amount,
            "avg_amount_car_card_pair": avg_car_card_amount,
            "avg_amount_no_car_card_pair": (avg_cleaned_amount - avg_car_card_amount + avg_sketchy_amount)/3,
            "avg_amount_no_pair": avg_sketchy_amount
        }

    # plot_percent_sketchy_vs_cleaned_location(card_location_data, "percent")
    # plot_percent_sketchy_vs_cleaned_location(card_location_data, "absolut")
    # plot_percent_sketchy_vs_cleaned_location(card_location_data, "avg_amount")

    for i, (location, data) in enumerate(card_location_data.items()):
        print(location)
        print(data)
        print()
        if i == 3:
            break

    mongo = DB("comparing_purchases_of_pairs")
    mongo.delete_many({})

    mongo.insert_many([{"location": location, **data} for location, data in card_location_data.items()])
    print(mongo.find_all())








if __name__ == "__main__":
    main()