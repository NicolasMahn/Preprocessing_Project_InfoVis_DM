import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import load_data
import json
from mongo import DB

def open_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

def calculate_matrices():
    cc_data = load_data.open_csv_file("../data/raw_data/cc_data.csv")
    cc_nums = list(set(cd[3] for cd in cc_data[1]))

    most_common_cc_per_car = open_json("../data/most_common_cc_per_car.json")
    most_common_cc_per_car = dict(sorted(most_common_cc_per_car.items(), key=lambda item: int(item[0])))
    cars = list(most_common_cc_per_car.keys())

    absolute_matrix = np.zeros((len(cars), len(cc_nums)))
    relative_cc_matrix = np.zeros((len(cars), len(cc_nums)))
    relative_car_matrix = np.zeros((len(cars), len(cc_nums)))

    for i, car in enumerate(cars):
        for j, cc in enumerate(cc_nums):
            if str(cc) in most_common_cc_per_car[car].keys():
                absolute_matrix[i, j] = most_common_cc_per_car[car][str(cc)]
            else:
                absolute_matrix[i, j] = 0
        total_i = sum(absolute_matrix[i])
        if total_i == 0:
            continue
        for j in range(len(cc_nums)):
            relative_car_matrix[i, j] = absolute_matrix[i, j] / total_i * 100

    for i in range(len(cc_nums)):
        total_i = sum(absolute_matrix[:, i])
        if total_i == 0:
            continue
        for j in range(len(cars)):
            relative_cc_matrix[j, i] = absolute_matrix[j, i] / total_i * 100

    return absolute_matrix, relative_cc_matrix, relative_car_matrix, cars, cc_nums

def visualize_cc_pairs(matrix, x_axis, y_axis):
    # Create a custom colormap
    cividis = plt.cm.cividis
    newcolors = cividis(np.linspace(1, 0, 256))
    white = np.array([1, 1, 1, 1])
    newcolors[0, :] = white
    custom_cmap = mcolors.ListedColormap(newcolors)

    # Plot the confusion matrix
    fig, ax = plt.subplots(figsize=(16, 12))
    im = ax.imshow(matrix, cmap=custom_cmap)

    # Add labels
    ax.set_xticks(np.arange(len(y_axis)))
    ax.set_yticks(np.arange(len(x_axis)))
    ax.set_xticklabels(y_axis)
    ax.set_yticklabels(x_axis)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add grid
    ax.grid(which='both', color='gray', linestyle='-', linewidth=0.5)

    # Add titles and labels
    ax.set_title("Car - Credit Cards Matrix")
    ax.set_xlabel("Credit Cards")
    ax.set_ylabel("Car IDs")

    # Add a colorbar
    fig.colorbar(im, ax=ax)

    # Display the plot
    plt.tight_layout()
    plt.show()

def save_matrices_in_mongodb(absolute_matrix, relative_cc_matrix, relative_car_matrix, cars, cc_nums):
    mongo = DB("car_matrices")

    # Convert numpy arrays to lists
    absolute_matrix_list = absolute_matrix.tolist()
    relative_cc_matrix_list = relative_cc_matrix.tolist()
    relative_car_matrix_list = relative_car_matrix.tolist()

    mongo.delete_many({})
    mongo.insert_one_if_not_exists({"matrix": "absolute_matrix", "data": absolute_matrix_list}, "matrix")
    mongo.insert_one_if_not_exists({"matrix": "relative_cc_matrix", "data": relative_cc_matrix_list}, "matrix")
    mongo.insert_one_if_not_exists({"matrix": "relative_car_matrix", "data": relative_car_matrix_list}, "matrix")
    mongo.insert_one_if_not_exists({"y_axis": "cars", "data": cars}, "y_axis")
    mongo.insert_one_if_not_exists({"x_axis": "cc_nums", "data": cc_nums}, "x_axis")

    saved_data = mongo.find_all()

    for data in saved_data:
        print(data)
        if "matrix" in data.keys():
            if "relative_cc_matrix" in data["matrix"]:
                for list in data["data"]:
                    for item in list:
                        if item != 0 and item != 1:
                            print(item)

    mongo.close()

def main():
    absolute_matrix, relative_cc_matrix, relative_car_matrix, cars, cc_nums = calculate_matrices()

    save_matrices_in_mongodb(absolute_matrix, relative_cc_matrix, relative_car_matrix, cars, cc_nums)
    visualize_cc_pairs(relative_car_matrix, cars, cc_nums)

if __name__ == "__main__":
    main()