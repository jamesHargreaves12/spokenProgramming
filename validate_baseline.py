from baseline import baseline_functions
from get_data import train_test_data, validation_set
from tools.minimum_edit_distance import minimum_edit_distance


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

