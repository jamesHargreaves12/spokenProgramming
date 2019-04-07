from get_data import train_test_split, split_data
from other.log_module import write_to_log
from smt import smt_functions
from test1 import total_edit_distance_smt


def get_ted_for_fold_v1():
    print("GET TED v2 test")
    results = []
    for test,train in train_test_split:
        split_test = split_data(test)
        split_train = split_data(train)
        n = 2
        epoch = 100
        null_flag = True
        alignments = smt_functions.get_alignment_1(split_train, epoch, null_flag)
        log_phrase_table = smt_functions.get_log_phrase_table1(split_train, alignments)
        lang_model = smt_functions.get_language_model(split_train, n)
        alpha = 0.4725864123957092
        omega = 2.6
        ted = total_edit_distance_smt(split_test, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}\n".format(ted))
        results.append(ted)
    return results


def get_ted_for_fold_v2():
    print("GET TED v2 test")
    results = []
    for test,train in train_test_split:
        split_test = split_data(test)
        split_train = split_data(train)
        n = 2
        epoch = 100
        null_flag = True
        alignments = smt_functions.get_alignment_2(split_train, epoch, null_flag)
        log_phrase_table = smt_functions.get_log_phrase_table2(split_train, alignments)
        lang_model = smt_functions.get_language_model(split_train, n)
        alpha = 0.5451790111763591
        omega = 1.5
        ted = total_edit_distance_smt(split_test, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}\n".format(ted))
        results.append(ted)
    return results

# print(get_alpha_v1())
# v1 - alpha = 0.4725864123957092
# v2 - alpha = 0.5451790111763591
# So v1 - omega = 2.6
# So v2 - omega = 1.5

if __name__ == "__main__":
    results = get_ted_for_fold_v1()
