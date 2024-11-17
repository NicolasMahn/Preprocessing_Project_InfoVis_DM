import csv


def save_csv(data, file_name):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data[0])
        writer.writerows(data[1:])