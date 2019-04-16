from baseline import baseline_functions
from get_data import train_test_split
from smt import smt_functions
from tools.minimum_edit_distance import minimum_edit_distance_per_token


def total_edit_distance_baseline(test_pairs, threshold, stem_flag, lang_model,pseudocode_tokens):
    total_dist = 0
    for trans,pseudo in test_pairs:
        prediction = baseline_functions.get_output_baseline(trans,lang_model,pseudocode_tokens,stem_flag,threshold)
        total_dist += minimum_edit_distance_per_token(prediction,pseudo)
    return total_dist/len(test_pairs)


def get_ted_for_folds_baseline():
    print("GET TED baseline")
    results = []
    for test,train in train_test_split:
        lang_model = smt_functions.get_language_model(train, 1)
        pseudocode_tokens = baseline_functions.get_pseudocode_tokens(train)
        ted = total_edit_distance_baseline(test,0,True,lang_model,pseudocode_tokens)
        print(ted)
        results.append(ted)
    return results


if __name__ == "__main__":
    results = get_ted_for_folds_baseline()
    print(results)
    print(sum(results)/len(results))