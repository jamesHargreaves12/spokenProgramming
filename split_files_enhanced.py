from termcolor import colored

from get_data import train_test_data, validation_set, split_data, split_keywords, remove_start_tokens
from other.log_module import write_to_log
from smt import smt_functions, get_alpha_value
from test1 import total_edit_distance_smt_enhanced

n=2
epoch = 100
null_flag = True

def get_alpha_v1():
    split_train_test = split_data(train_test_data)
    remove_start_tokens(split_train_test)
    align = smt_functions.get_alignment_1(split_train_test,epoch,null_flag)
    return get_alpha_value.get_alpha(align)


def get_alpha_v2():
    split_train_test = split_data(train_test_data)
    remove_start_tokens(split_train_test)
    align = smt_functions.get_alignment_2(split_train_test,epoch,null_flag)
    return get_alpha_value.get_alpha(align)


def validate_ibmmodel1():
    print("Validate ibmmodel 1")
    split_tt_data = split_data(train_test_data)
    alignments = smt_functions.get_alignment_1(split_tt_data,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table1(split_tt_data,alignments)
    lang_model = smt_functions.get_language_model(split_tt_data,n)
    alpha = 0.5522747815607111
    results = []
    split_validation = split_data(validation_set)
    splits = [i/2 for i in range(1,6)]
    for omega in splits:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        ted = total_edit_distance_smt_enhanced(split_validation, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}\n".format(ted))
        results.append((omega,ted))
    return results


def validate_ibmmodel2():
    print("Validate ibmmodel2")
    split_tt_data = split_data(train_test_data)
    split_validation = split_data(validation_set)
    lang_model = smt_functions.get_language_model(split_tt_data,n)
    remove_start_tokens(split_tt_data)
    alignments = smt_functions.get_alignment_2(split_tt_data,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table2(split_tt_data,alignments)
    alpha = 0.5995053272450532
    results = []
    omegas = [i/2 for i in range(1,6)]
    for omega in omegas:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        ted = total_edit_distance_smt_enhanced(split_validation, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}\n".format(ted))
        results.append((omega,ted))
    return results


# print(get_alpha_v1())
# 0.5522747815607111
print(get_alpha_v2())
# 0.5995053272450532
# print(validate_ibmmodel1())
# results = []
# So omega = 2.6
print(validate_ibmmodel2())
# results = [(0.5,579),(0.8,567),(0.9,567),(1.0,566),(1.1,565),(1.2,565),(1.3,563),(1.4,562),(1.5,556),(1.6,559),(1.7,559)(2.0,560),(2.5,566)
# So omega = 1.5

