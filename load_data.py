import csv
import os
from datetime import datetime


def parse_value(value):
    """
    Try to parse the value into float, int, or datetime, otherwise return it as a string.
    """
    # Try to parse as float first (since int can be a special case of float)
    try:
        float_value = float(value)
        # Check if the float is actually an integer value
        if float_value.is_integer():
            return int(float_value)
        else:
            return float_value
    except ValueError:
        pass

    # Try to parse as datetime (multiple formats)
    for date_format in ["%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%m/%d/%Y"]:
        try:
            return datetime.strptime(value, date_format)
        except ValueError:
            continue

    # If all parsing fails, return the original string
    return value


def open_csv_file(data_source):
    points = list()
    original_indices = list()
    labels = list()

    # Open and read the CSV file
    if os.path.exists(data_source):
        with open(data_source, mode='r', newline='') as file:
            reader = csv.reader(file)

            # Extract the first row as labels
            labels = next(reader)

            # Read each subsequent row in the CSV file
            for index, row in enumerate(reader):
                parsed_row = list()
                for value in row:
                    parsed_value = parse_value(value)
                    parsed_row.append(parsed_value)

                points.append(parsed_row)  # Append parsed values
                original_indices.append(index)  # Track the original index for each point

        return labels, points, original_indices
    else:
        print(f"Error: File '{data_source}' does not exist.")
        os._exit(1)
