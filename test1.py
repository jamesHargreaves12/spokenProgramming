import gc
from baseline import baseline_functions
from other.log_module import write_to_log
from smt import smt_functions, decoder_with_log
from tools.minimum_edit_distance import minimum_edit_distance
from get_data import validation_set, train_test_data, split_keywords


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



def total_edit_distance_smt_enhanced(test_pairs, alpha, omega, lang_model, log_phrase_table):
    total_dist = 0
    decoder_with_log.set_alpha(alpha)
    decoder_with_log.set_omega(omega)
    for trans,pseudo in test_pairs:
        gc.collect()
        trans_start = trans[0]
        pseudo_start = pseudo[0]
        if trans_start in split_keywords:
            prediction = smt_functions.run_smt(lang_model,log_phrase_table,trans,initial_trans=trans_start)
            prediction = prediction
        else:
            prediction = smt_functions.run_smt(lang_model,log_phrase_table,trans)
        print(prediction)
        write_to_log("predict: {}\n".format(prediction))
        predicted_toks = prediction.split(" ")
        total_dist += minimum_edit_distance(predicted_toks,pseudo)
    return total_dist


if __name__ == "__main__":
    pass
# alpha = 0.5, omega = 0.5 => ED = 1064

# validate_ibmmodel2()


# backup on github
# backup project data 2 on github
# baseline to smt_functions file
# check decoder works with ibmmodel1 version
# TODO Form validation set optimizer
# TODO Using ^ get result for the other 4 folds
