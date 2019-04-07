from get_data import train_test_split
from other.log_module import write_to_log
from smt import smt_functions
from test1 import total_edit_distance_smt

def get_ted_for_fold_v1():
    print("GET TED v1 test")
    results = []
    for test,train in train_test_split:
        n = 2
        epoch = 100
        null_flag = True
        alignments = smt_functions.get_alignment_1(train, epoch, null_flag)
        log_phrase_table = smt_functions.get_log_phrase_table1(train, alignments)
        lang_model = smt_functions.get_language_model(train, n)
        alpha = 0.8027082941508369
        omega = 1.0
        ted = total_edit_distance_smt(test, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}\n".format(ted))
        results.append(ted)
    return results


if __name__ == "__main__":
    # results = get_ted_for_fold_v1()
    results = [239,402,510,507,867,290,290,466,939]
    print(sum(results))
    # 4510