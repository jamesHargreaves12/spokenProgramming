from get_data import train_test_data, validation_set
from other.log_module import write_to_log
from smt import smt_functions
from test1 import total_edit_distance_smt
import matplotlib.pyplot as plt


def validate_ibmmode1():
    n = 2
    epoch = 100
    null_flag = True
    alignments = smt_functions.get_alignment_1(train_test_data,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table1(train_test_data,alignments)
    lang_model = smt_functions.get_language_model(train_test_data,n)
    alpha = 0.7788829380260138
    results = []
    omega_values = [0.9,1.1,0.8,1.2,0.7,1.3,0.6,1.4]
    for omega in omega_values:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        ted = total_edit_distance_smt(validation_set, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}\n".format(ted))
        results.append((omega,ted))
    return results


# results = validate_ibmmode1()
# omega, edit_distance
if __name__  == "__main__":
    results = [(0.5, 1035),(0.7,1033),(0.8,1032),(0.9,1032),(1.0, 1032),(1.1,1035),(1.2,1035),(1.3,1034),(1.5, 1034),(2.0, 1037),(2.5, 1037)]
    xs = [x for x,_ in results]
    ys = [y for _,y in results]
    plt.plot(xs,ys)
    plt.show()

