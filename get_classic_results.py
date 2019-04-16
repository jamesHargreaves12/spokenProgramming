import math

import get_data
from generate_folds import RANDOM_SHUFFLE_ORDER
from tools.find_resource_in_project import get_path
from tools.minimum_edit_distance import minimum_edit_distance_per_token


def get_translations_from_file(filename):
    predicts = []
    with open(get_path(filename), "r") as file:
        for line in file.readlines():
            predicts.append(line.strip("\n").split(" "))
    return predicts

if __name__ == "__main__":
    translations = []
    translations.extend(get_translations_from_file("/results/traditional_train.txt"))
    translations.extend(get_translations_from_file("/results/traditional_test1.txt"))
    translations.extend(get_translations_from_file("/results/traditional_test2.txt"))
    data = get_data.train_test_data + get_data.validation_set

    # print(len(translations))
    # print(len(data))
    translations_shuffled = []
    for i in RANDOM_SHUFFLE_ORDER:
        translations_shuffled.append(translations[i])
    translations = translations_shuffled

    results = []
    for i,pair in enumerate(data):
        truth = pair[1]
        results.append(minimum_edit_distance_per_token(translations[i],truth))
    # print(results)
    n = len(results)
    start_pos = 0
    fold_aed = []
    for i in range(10):
        size_fold = math.ceil((n-start_pos)/(10-i))
        aed = sum(results[start_pos:start_pos+size_fold])/size_fold
        fold_aed.append(aed)
        start_pos += size_fold
    print(fold_aed)
    print(sum(fold_aed[:len(fold_aed) - 1])/(len(fold_aed)-1))


