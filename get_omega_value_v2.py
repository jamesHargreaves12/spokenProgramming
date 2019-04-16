from get_data import train_test_data, validation_set
from other.log_module import write_to_log
from smt import smt_functions
from test1 import total_edit_distance_smt
import matplotlib.pyplot as plt
# RUN this file on the outside computer - should take 2.5 days to run

def validate_ibmmodel2():
    n = 2
    epoch = 100
    null_flag = True
    alignments = smt_functions.get_alignment_2(train_test_data,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table2(train_test_data,alignments)
    lang_model = smt_functions.get_language_model(train_test_data,n)
    alpha = 0.7042902967121091
    results = []
    for omega in [i/2 for i in range(1,6)]:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        ted = total_edit_distance_smt(validation_set, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}".format(ted))
        results.append((omega,ted))
    return results

if __name__ == "__main__":
    # results = validate_ibmmodel2()
    # print(results)
    # old_results = [(0.4,718),(0.5,718),(0.6,718),(0.7,719),(0.8,718),(0.9,719),(1.0,723),(1.2,719),(1.3,719),(1.4,719),(1.5,719),(2.0,719),(2.5,720)]
    results = [(0.5,706),(1.0,706),(1.5,706),(2.0,701),(2.5,698),(2.7,698),(2.8,698),(2.9,698),(3.0,698),(3.1,698),(3.2,698),(3.3,699),(3.4,699),(3.5,697),(3.6,697),(3.7,697),(3.8,702),(3.9,702),(4.0,702)]
    # omega = 3.5
    xs = [x for x, _ in results]
    ys = [y for _, y in results]
    plt.plot(xs, ys)
    plt.show()
