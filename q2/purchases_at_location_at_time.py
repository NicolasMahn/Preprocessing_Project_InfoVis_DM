from mongo import DB
import load_data
import datetime

def main():
    time_list = []

    cc_data = load_data.open_csv_file("../data/cc_data.csv")
    for row in cc_data[1]:
        timestamp = row[0].timestamp()
        cc_dict = {
            "starttime": timestamp,
            "endtime": timestamp,
            "type": "creditcard",
            "location": row[1],
            "price": row[2],
            "creditcard": row[3],
        }
        time_list.append(cc_dict)

    loyalty_data = load_data.open_csv_file("../data/loyalty_data.csv")
    for row in loyalty_data[1]:
        timestamp = row[0].timestamp()
        l_dict = {
            "starttime": timestamp,
            "endtime": timestamp,
            "type": "loyalty",
            "location": row[1],
            "price": row[2],
            "loyalty": row[3],
        }
        time_list.append(l_dict)

    cleaned_card_data = load_data.open_csv_file("../data/cleaned_card_data.csv")
    for row in cleaned_card_data[1]:
        timestamp = row[0].timestamp()
        ccd_dict = {
            "starttime": timestamp,
            "endtime": timestamp,
            "type": "pairs",
            "location": row[1],
            "price": row[2],
            "creditcard": row[3],
            "loyalty": row[4],
        }
        time_list.append(ccd_dict)

    sketchy_card_data = load_data.open_csv_file("../data/sketchy_card_data.csv")
    for row in sketchy_card_data[1]:
        timestamp = row[0].timestamp()
        cc = row[3]
        if cc == "" or cc == '':
            cc = None
        loyalty = row[4]
        if loyalty == "" or loyalty == '':
            loyalty = None
        scd_dict = {
            "starttime": timestamp,
            "endtime": timestamp,
            "type": "no_pairs",
            "location": row[1],
            "price": row[2],
            "creditcard": cc,
            "loyalty": loyalty
        }
        time_list.append(scd_dict)

    stops_at_location = load_data.open_csv_file("../data/stops_in_locations.csv")
    for row in stops_at_location[1]:
        c_dict = {
            "starttime": row[1].timestamp(),
            "endtime": row[2].timestamp(),
            "type": "cars_in_area",
            "location": row[4],
            "car_id": row[0],
            "start_coordinates": row[5],
            "end_coordinates": row[6]
        }
        time_list.append(c_dict)

    cc = 2
    l = 2
    ccd = 2
    np = 2
    cars = 2
    for row in time_list:
        if row["type"] == "creditcard" and cc > 0 and "Katerina" in row["location"]:
            print(row)
            cc -= 1
        elif row["type"] == "pairs" and ccd > 0 and "Katerina" in row["location"]:
            print(row)
            ccd -= 1
        elif row["type"] == "cars_in_area" and cars > 0 and "Katerina" in row["location"]:
            print(row)
            cars -= 1
        elif row["type"] == "no_pairs" and np > 0:
            print(row)
            np -= 1
        elif row["type"] == "loyalty" and l > 0:
            print(row)
            l -= 1
        if cc == 0 and ccd == 0 and cars == 0:
            break
    print()
    print()


    db = DB("purchases_over_time")
    db.delete_many({})

    db.insert_many(time_list)

if __name__ == "__main__":
    main()