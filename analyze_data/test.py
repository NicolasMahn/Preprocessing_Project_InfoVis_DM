from gps_data_preprocessing import get_gps_data_sorted_by_id

def main():
    sorted_gps_data = get_gps_data_sorted_by_id()
    for key, value in sorted_gps_data.items():
        print(f"ID: {key}")
        #for entry in value:
        #    print(f"  {entry[0]}: {entry[1]}, {entry[2]}")
        #print()

if __name__ == '__main__':
    main()