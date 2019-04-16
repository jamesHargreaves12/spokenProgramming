import re
from collections import defaultdict

from get_data import validation_set, train_test_folds, train_test_split
from tools.find_resource_in_project import get_path
from tools.minimum_edit_distance import minimum_edit_distance_per_token


def get_translations_omega(filename):
    predicts:dict = {}
    omega = -1
    # Edit distance = 1015
    # omega 1.1
    ed_re = re.compile(r"Edit distance = (\d+)\n")
    o_re = re.compile(r"omega ([0-9.]+)\n")
    pred_re = re.compile(r"predict: (.*)\n")
    omega_preds = []
    with open(get_path(filename), "r") as file:
        for line in file.readlines():
            if ed_re.match(line):
                ed = int(ed_re.match(line).group(1))
            elif o_re.match(line):
                if omega != -1:
                    predicts[omega] = omega_preds
                omega_preds = []
                omega = float(o_re.match(line).group(1))
            elif pred_re.match(line):
                pred = pred_re.match(line).group(1)
                omega_preds.append(pred)
            # print(line)
    predicts[omega] = omega_preds
    return predicts

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


trans = get_translations_results("/logs/results_v2.txt")
# [fold][i]
eds = defaultdict(list)
averages = []
for i,splits in enumerate(train_test_split):
    test,_ = splits
    total = 0
    for j,pair in enumerate(test):
        _,pseud = pair
        # print(i,j)
        predict = trans[i][j].split(" ")
        aed = minimum_edit_distance_per_token(predict,pseud)
        total += aed
    averages.append(total / len(test))
    print(total/len(test))
print(averages)
print(sum(averages)/len(averages))
