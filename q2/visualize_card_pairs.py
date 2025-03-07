import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import load_data
from mongo import DB


def calculate_matrices():
    cc_data = load_data.open_csv_file("../data/raw_data/cc_data.csv")
    loyalty_data = load_data.open_csv_file("../data/raw_data/loyalty_data.csv")

    l_nums = list(set(ld[3] for ld in loyalty_data[1]))
    cc_nums = list(set(cd[3] for cd in cc_data[1]))

    cleaned_card_data = load_data.open_csv_file("../data/cleaned_card_data.csv")
    cleaned_cards = set()
    cleaned_l_nums = set()
    for row in cleaned_card_data[1]:
        cc_num = row[3]
        l_num = row[4]

        index = l_nums.index(l_num)
        cc_index = cc_nums.index(cc_num)
        tmp_cc_num = cc_nums[index]
        cc_nums[index] = cc_num
        cc_nums[cc_index] = tmp_cc_num

        cleaned_cards.add((cc_num, l_num))
        cleaned_l_nums.add(l_num)

    l_nums = list(l_nums)
    for i, l_num in enumerate(l_nums.copy()):
        if l_num not in cleaned_l_nums:
            last_l_num = l_nums[-1]
            l_nums[i] = last_l_num
            l_nums[-1] = l_num
        else:
            cc_num = [cc for cc, ln in cleaned_cards if ln == l_num]
            if len(cc_num) > 1:
                print(f"Multiple cards for loyalty card {l_num}: {cc_num}")
            cc_num = cc_num[0]
            index = cc_nums.index(cc_num)
            tmp_cc_num = cc_nums[i]
            cc_nums[i] = cc_num
            cc_nums[index] = tmp_cc_num

    absolute_matrix = np.zeros((len(l_nums), len(cc_nums)))
    relative_cc_matrix = np.zeros((len(l_nums), len(cc_nums)))
    relative_l_matrix = np.zeros((len(l_nums), len(cc_nums)))

    purchases_with_cc = {}
    for i in range(len(cc_nums)):
        purchases_with_cc[i] = [[cd[0].date(), cd[1], cd[2]] for cd in cc_data[1] if cc_nums[i] == cd[3]]

    purchases_with_l = {}
    for i in range(len(l_nums)):
        purchases_with_l[i] = [[ld[0].date(), ld[1], ld[2]] for ld in loyalty_data[1] if l_nums[i] == ld[3]]

    for i in range(len(l_nums)):
        for j in range(len(cc_nums)):
            for purchase_l in purchases_with_l[i]:
                for purchase_cc in purchases_with_cc[j]:
                    # print(purchase_l, purchase_cc)
                    if purchase_l[0] == purchase_cc[0] and purchase_l[1] == purchase_cc[1] and purchase_l[2] == purchase_cc[2]:
                        absolute_matrix[i, j] += 1
        total_i = sum(absolute_matrix[i])
        for j in range(len(cc_nums)):
            relative_l_matrix[i, j] = absolute_matrix[i, j] / total_i *100

    for i in range(len(cc_nums)):
        total_i = sum(absolute_matrix[:, i])
        for j in range(len(l_nums)):
            relative_cc_matrix[j, i] = absolute_matrix[j, i] / total_i *100

    return absolute_matrix, relative_cc_matrix, relative_l_matrix, l_nums, cc_nums


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
    ax.set_title("Loyalty-, Credit Cards Matrix")
    ax.set_xlabel("Credit Cards")
    ax.set_ylabel("Loyalty Cards")

    # Add a colorbar
    fig.colorbar(im, ax=ax)

    # Display the plot
    plt.tight_layout()
    plt.show()

def save_matrices_in_mongodb(absolute_matrix, relative_cc_matrix, relative_loyalty_matrix, loyalty_nums, cc_nums):
    mongo = DB("card_matrices")

    # Convert numpy arrays to lists
    absolute_matrix_list = absolute_matrix.tolist()
    relative_cc_matrix_list = relative_cc_matrix.tolist()
    relative_loyalty_matrix_list = relative_loyalty_matrix.tolist()

    mongo.delete_many({})
    mongo.insert_one_if_not_exists({"matrix": "absolute_matrix", "data": absolute_matrix_list}, "matrix")
    mongo.insert_one_if_not_exists({"matrix": "relative_cc_matrix", "data": relative_cc_matrix_list}, "matrix")
    mongo.insert_one_if_not_exists({"matrix": "relative_loyalty_matrix", "data": relative_loyalty_matrix_list}, "matrix")
    mongo.insert_one_if_not_exists({"y_axis": "loyalty_nums", "data": loyalty_nums}, "y_axis")
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
    absolute_matrix, relative_cc_matrix, relative_l_matrix, l_nums, cc_nums = calculate_matrices()

    save_matrices_in_mongodb(absolute_matrix, relative_cc_matrix, relative_l_matrix, l_nums, cc_nums)
    visualize_cc_pairs(relative_cc_matrix, l_nums, cc_nums)

if __name__ == "__main__":
    main()