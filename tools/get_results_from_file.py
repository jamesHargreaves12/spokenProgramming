import re
from collections import defaultdict

from tools.find_resource_in_project import get_path


def get_translations_omega(filename):
    predicts:dict = {}
    omega = -1
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
    return predicts


def get_rule_based_translations_from_file(filename):
    predicts = []
    with open(get_path(filename), "r") as file:
        for line in file.readlines():
            predicts.append(line.strip("\n").split(" "))
    return predicts


def get_edit_distances_from_file(filename):
    ed_re = re.compile(r"Edit distance = (\d+)\n")
    o_re = re.compile(r"omega ([0-9.]+)\n")
    both_re = re.compile(r"Edit distance = (\d+)omega ([0-9.]+)\n")
    results = []
    omega = -1
    with open(get_path(filename), "r") as file:
        for line in file.readlines():
            if ed_re.match(line):
                ed = int(ed_re.match(line).group(1))
                if omega != -1:
                    results.append((omega,ed))
            elif o_re.match(line):
                omega = float(o_re.match(line).group(1))
            elif both_re.match(line):
                match = both_re.match(line)
                ed = int(match.group(1))
                if omega != -1:
                    results.append((omega,ed))
                omega = float(match.group(2))
            # else:
            #     print(line)
    return results
