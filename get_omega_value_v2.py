from get_data import train_test_data, validation_set
from other.log_module import write_to_log
from smt import smt_functions
from test1 import total_edit_distance_smt

# RUN this file on the outside computer - should take 2.5 days to run

def validate_ibmmodel2():
    n = 2
    epoch = 100
    null_flag = True
    alignments = smt_functions.get_alignment_2(train_test_data,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table2(train_test_data,alignments)
    lang_model = smt_functions.get_language_model(train_test_data,n)
    alpha = 0.77358249072
    for omega in [i/2 for i in range(1,6)]:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        ted = total_edit_distance_smt(validation_set, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}".format(ted))


validate_ibmmodel2()
