import math

import get_data
from tools.find_resource_in_project import get_path
from tools.minimum_edit_distance import minimum_edit_distance


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
    results = []
    for i,pair in enumerate(data):
        truth = pair[1]
        results.append(minimum_edit_distance(translations[i],truth))
    print(results)
    n = len(results)
    start_pos = 0
    fold_ted = []
    for i in range(10):
        size_fold = math.ceil((n-start_pos)/(10-i))
        ted = sum(results[start_pos:start_pos+size_fold])
        fold_ted.append(ted)
        start_pos += size_fold
    print(fold_ted)
    print(sum(fold_ted[:10]))


