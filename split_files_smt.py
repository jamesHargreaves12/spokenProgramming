from termcolor import colored

from get_data import train_test_data, validation_set, split_data
from other.log_module import write_to_log
from smt import smt_functions, get_alpha_value
from test1 import total_edit_distance_smt

def get_alpha_v1():
    epoch = 100
    null_flag = True
    split_train_test = split_data(train_test_data)
    align = smt_functions.get_alignment_1(split_train_test,epoch,null_flag)
    return get_alpha_value.get_alpha(align)

def get_alpha_v2():
    epoch = 100
    null_flag = True
    split_train_test = split_data(train_test_data)
    align = smt_functions.get_alignment_2(split_train_test,epoch,null_flag)
    return get_alpha_value.get_alpha(align)


def validate_ibmmodel1():
    print("Validate ibmmode1")
    n = 2
    epoch = 100
    null_flag = True
    split_tt_data = split_data(train_test_data)
    alignments = smt_functions.get_alignment_1(split_tt_data,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table1(split_tt_data,alignments)
    lang_model = smt_functions.get_language_model(split_tt_data,n)
    alpha = 0.4725864123957092
    results = []
    split_validation = split_data(validation_set)
    for omega in [i/2 for i in range(1,6)]:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        ted = total_edit_distance_smt(split_validation, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}".format(ted))
        results.append((omega,ted))
    return results


def validate_ibmmodel2():
    print("Validate ibmmode2")
    n = 2
    epoch = 100
    null_flag = True
    split_tt_data = split_data(train_test_data)
    alignments = smt_functions.get_alignment_2(split_tt_data,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table2(split_tt_data,alignments)
    lang_model = smt_functions.get_language_model(split_tt_data,n)
    alpha = 0.5451790111763591
    results = []
    split_validation = split_data(validation_set)
    for omega in [i/2 for i in range(1,6)]:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        ted = total_edit_distance_smt(split_validation, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}".format(ted))
        results.append((omega,ted))
    return results


# print(get_alpha_v1())
# 0.4725864123957092
# print(get_alpha_v2())
# 0.5451790111763591
print(validate_ibmmodel1())
#
# print(validate_ibmmodel2())
#
