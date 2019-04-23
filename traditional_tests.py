import math
import time

from data_prep_tools.constants import base_dir_1, base_dir_2
from tools.get_results_from_file import get_rule_based_translations_from_file
from tests.bag_of_words_test import bag_of_words_test
from tests.minimum_edit_distance import minimum_edit_distance, minimum_edit_distance_per_token
from tools import get_test_data
from tools.generate_folds import RANDOM_SHUFFLE_ORDER
from tools.get_test_data import flatten
from traditional_MT import load_dep_parse
from traditional_MT.graph_to_expression import get_output_string


def correct_order_to_shuffle_order(translations):
    translations_shuffled = []
    for i in RANDOM_SHUFFLE_ORDER:
        translations_shuffled.append(translations[i])
    return translations_shuffled


def form_folds(preds, truth, num_folds,without_train_flag = False):
    fold_size = math.ceil(len(preds)/num_folds)
    num_folds -= 1
    folds = []
    cur_fold = []
    num_in_fold = 0
    for i in range(len(preds)):
        if not without_train_flag or RANDOM_SHUFFLE_ORDER[i] >= 49:
            cur_fold.append((preds[i],truth[i]))
        num_in_fold += 1
        if num_in_fold == fold_size:
            folds.append(cur_fold)
            cur_fold = []
            num_in_fold = 0
            if num_folds > 0:
                fold_size = math.ceil((len(preds)-i-1)/num_folds)
            num_folds -= 1
    return folds

def get_timings():
    toks1,deps1 = load_dep_parse.get_token_deps(base_dir=base_dir_1)
    toks2,deps2 = load_dep_parse.get_token_deps(base_dir=base_dir_2)
    toks = toks1 + toks2
    deps = deps1 + deps2
    print(len(toks))
    print(len(deps))
    size_fold_0 = 15
    results = []
    for i in range(size_fold_0):
        index = RANDOM_SHUFFLE_ORDER[i]
        tokens = toks[index]
        dependencies = deps[index]
        start = time.time()
        out = get_output_string(tokens, dependencies)
        end = time.time()
        results.append(end-start)
    return results

if __name__ == "__main__":
    data = get_test_data.train_test_data + get_test_data.validation_set
    truth = [x[1] for x in data]
    tr_train = get_rule_based_translations_from_file("/results/traditional_train.txt")
    tr_test1 = get_rule_based_translations_from_file("/results/traditional_test1.txt")
    tr_test2 = get_rule_based_translations_from_file("/results/traditional_test2.txt")
    preds = tr_train + tr_test1 + tr_test2
    preds = correct_order_to_shuffle_order(preds)

    folds = form_folds(preds,truth,10,True)
    folds = folds[:-1]
    print(len(flatten(folds)))
    eds = []
    bows = []
    norm_eds = []
    for fold in folds:
        tot_ed = 0
        tot_bow = 0
        tot_norm = 0
        print(len(fold))
        for pred,truth in fold:
            ed = minimum_edit_distance(pred,truth)
            bow = bag_of_words_test(pred,truth)
            norm_ed = minimum_edit_distance_per_token(pred,truth)
            tot_ed += ed
            tot_bow += bow
            tot_norm += norm_ed
        eds.append(tot_ed)
        bows.append(tot_bow)
        norm_eds.append(tot_norm/len(fold))
    print(eds)
    print(sum(eds))
    print(bows)
    print(sum(bows))
    print(norm_eds)

    print(get_timings())

