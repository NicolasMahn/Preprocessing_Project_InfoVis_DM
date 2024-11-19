from mongo import DB
import load_data
import datetime

def main():
    time_dict = {}

    cc_data = load_data.open_csv_file("../data/cc_data.csv")
    for row in cc_data[1]:
        timestamp = row[0].timestamp()
        cc_dict = {
            "starttime": timestamp,
            "endtime": timestamp,
            "type": "creditcard",
            "locaton": row[1],
            "price": row[2],
            "card": row[3],
        }
        if timestamp not in time_dict:
            time_dict[timestamp] = [cc_dict]
        else:
            time_dict[timestamp].append(cc_dict)

    cleaned_card_data = load_data.open_csv_file("../data/cleaned_card_data.csv")



if __name__ == "__main__":
    main()