import gc
from baseline import baseline_functions
from other.log_module import write_to_log
from smt import smt_functions, decoder_with_log
from tools.minimum_edit_distance import minimum_edit_distance
from get_data import validation_set,train_test_data

def total_edit_distance_smt(test_pairs, alpha, omega, lang_model, log_phrase_table):
    total_dist = 0
    decoder_with_log.set_alpha(alpha)
    decoder_with_log.set_omega(omega)
    for trans,pseudo in test_pairs:
        gc.collect()
        prediction = smt_functions.run_smt(lang_model,log_phrase_table,trans)
        print(prediction)
        write_to_log("predict: {}\n".format(prediction))
        predicted_toks = prediction.split(" ")
        total_dist += minimum_edit_distance(predicted_toks,pseudo)
    return total_dist
# Using validation on SMT with ibmmodel1:
# Constants
# Language model = n
# training of IBMModel1 = epoch,null_flag
# decoder = Alpha, Omega
#
# n = {1,2,3,4,5,6}
# alpha = (0,1)
# omega > 1

def validate_ibmmode1():
    n = 2
    epoch = 100
    null_flag = True
    alignments = smt_functions.get_alignment_1(train_test_data,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table1(train_test_data,alignments)
    lang_model = smt_functions.get_language_model(train_test_data,n)
    alpha = 0.8027082941508369
    for omega in [i/2 for i in range(1,6)]:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        ted = total_edit_distance_smt(validation_set, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}".format(ted))
validate_ibmmode1()
# alpha = 0.5, omega = 0.5 => ED = 1064


def validate_ibmmodel2():
    n = 2
    epoch = 100
    null_flag = True
    alignments = smt_functions.get_alignment_2(train_test_data,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table2(train_test_data,alignments)
    lang_model = smt_functions.get_language_model(train_test_data,n)
    # for alpha in [i/10 for i in range(1,10)]:
    #     for omega in [i/2 for i in range(1,6)]:
    #         message = "alpha {} omega {}\n".format(alpha, omega)
    #         write_to_log(message)
    #         print("alpha,omega",alpha,omega)
    #         ted = total_edit_distance_smt(validation_set, alpha, omega, lang_model, log_phrase_table)
    #         print(ted)
    #         write_to_log("Edit distance = {}".format(ted))
# validate_ibmmodel2()






# backup on github
# backup project data 2 on github
# baseline to smt_functions file
# check decoder works with ibmmodel1 version
# TODO Form validation set optimizer
# TODO Using ^ get result for the other 4 folds
