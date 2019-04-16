import re
from collections import defaultdict

from get_data import train_test_split, split_data
from tools.find_resource_in_project import get_path
from tools.minimum_edit_distance import minimum_edit_distance_per_token


def get_translations_results(filename):
    predicts: dict = defaultdict(list)
    ed_re = re.compile(r"Edit distance = (\d+)\n")
    pred_re = re.compile(r"predict: (.*)\n")
    fold = 0
    with open(get_path(filename), "r") as file:
        for line in file.readlines():
            if ed_re.match(line):
                ed = int(ed_re.match(line).group(1))
                fold += 1
            elif pred_re.match(line):
                pred = pred_re.match(line).group(1)
                predicts[fold].append(pred)
            else:
                print("non matched line: ",line)
            # print(line)
    return predicts


trans = get_translations_results("/logs/results_split_v2.txt")
results= []
for i, cv_splits in enumerate(train_test_split):
    pred_i = 0
    test,_ = cv_splits
    total = 0
    for pair in test:
        data = split_data([pair])
        split_test_count = len(data)
        translation = []
        for j in range(split_test_count):
            translation += trans[i][pred_i].split(" ")
            pred_i += 1
        # print(len(translation), len(pair[1]),split_test_count)
        # print(" ".join(translation))
        total += minimum_edit_distance_per_token(translation,pair[1])
    results.append(total/len(test))
print(results)
print(sum(results)/len(results))