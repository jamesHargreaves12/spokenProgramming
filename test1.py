import math

import generate_folds
from baseline import baseline_functions
from langModel.faster_lang_model import LanguageModel
from smt import smt_functions, decoder_with_log
from tools.minimum_edit_distance import minimum_edit_distance

def flatten(lss):
    return [item for sublist in lss for item in sublist]


sentence_pair_folds = generate_folds.get_folds(5, "SEQ")
validation_set = sentence_pair_folds[-1]
train_test_folds = sentence_pair_folds[:-1]
train_test_data = flatten(train_test_folds)

# print(len(validation_set))
# print(len(train_test_folds))
# print(len(train_test_data))

def total_edit_distance_baseline(test_pairs, threshold, stem_flag, lang_model,pseudocode_tokens):
    total_dist = 0
    for trans,pseudo in test_pairs:
        prediction = baseline_functions.get_output_baseline(trans,lang_model,pseudocode_tokens,stem_flag,threshold)
        total_dist += minimum_edit_distance(prediction,pseudo)
    return total_dist

def optimise_range(f, precision, start, end):
    min_x = start
    cur_x = start
    min_f = f(cur_x)
    while cur_x <= end-precision:
        cur_x += precision
        cur_f = f(cur_x)
        if cur_f < min_f:
            min_f = cur_f
            min_x = cur_x
    return min_x,min_f


# Using validation set on the baseline:
# Constants = stem_flag, threshold, n
def validate_baseline():
    pseudocode_tokens = baseline_functions.get_pseudocode_tokens(train_test_data)
    for n in range(1, 7):
        print("n =",n)
        for stem in [True,False]:
            lang_model = baseline_functions.get_language_model(train_test_data,n)
            op_f = lambda x : total_edit_distance_baseline(validation_set,x,stem,lang_model,pseudocode_tokens)
            print("S?",stem,"(x,fx)",optimise_range(op_f,0.1,0,1))
# n = 1
# S? True (x,fx) (0, 480)
# S? False (x,fx) (0, 485)
# n = 2
# S? True (x,fx) (0.30000000000000004, 480)
# S? False (x,fx) (0.30000000000000004, 485)
# n = 3
# S? True (x,fx) (0.2, 480)
# S? False (x,fx) (0.2, 485)
# n = 4
# S? True (x,fx) (0.2, 480)
# S? False (x,fx) (0.2, 485)
# n = 5
# S? True (x,fx) (0.1, 480)
# S? False (x,fx) (0.1, 485)
# n = 6
# S? True (x,fx) (0.1, 480)
# S? False (x,fx) (0.1, 485)


def total_edit_distance_smt(test_pairs, alpha, omega, lang_model, log_phrase_table):
    total_dist = 0
    decoder_with_log.set_alpha(alpha)
    decoder_with_log.set_omega(omega)
    for trans,pseudo in test_pairs:
        prediction = smt_functions.run_smt(lang_model,log_phrase_table,trans)
        print(prediction)
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
n = 2
epoch = 100
null_flag = True
lang_model = smt_functions.get_language_model(train_test_data,n)
log_phrase_table = smt_functions.get_log_phrase_table1(train_test_data,epoch,null_flag)
for alpha in [i/10 for i in range(1,10)]:
    for omega in  [i/2 for i in range(1,6)]:
        print("alpha,omega",alpha,omega)
        print(total_edit_distance_smt(validation_set, alpha, omega, lang_model, log_phrase_table))








# backup on github
# backup project data 2 on github
# baseline to smt_functions file
# check decoder works with ibmmodel1 version
# TODO Form validation set optimizer
# TODO Using ^ get result for the other 4 folds
