from langModel.faster_lang_model import LanguageModel
from tests.bag_of_words_test import bag_of_words_test
from tests.minimum_edit_distance import minimum_edit_distance, minimum_edit_distance_per_token
from tools.generate_folds import RANDOM_SHUFFLE_ORDER
from tools.get_test_data import test_train_split, train_test_data, validation_set
from baseline import baseline_functions
from smt import smt_functions
from tests.get_times_for_systems import get_time_for_files


# want bag of words, minimum edit and times
from useful_functions import get_med_bow_norm


def get_translator(stem_flag, train, n=1, threshold=1):
    lang_model = smt_functions.get_language_model(train, n)
    pseud_tokens = baseline_functions.get_pseudocode_tokens(train)
    translator = lambda trans: baseline_functions.get_output_baseline(trans,lang_model,pseud_tokens,stem_flag,threshold)
    return translator


def get_threshold(stem_flag):
    n=5
    results = []
    for threshold in [(x)/100 for x in range(100)]:
        translator = get_translator(stem_flag,train_test_data,n,threshold)
        test = validation_set
        med,_,_ = get_med_bow_norm(translator,test)
        results.append((threshold,med))
    return results


if __name__ == "__main__":
    # print(get_threshold(False))
    # threshold of 1 is optimal - ie no reordering takes place



    # Get timings for fold 1:
    test,train = test_train_split[0]
    stem_flag = True
    translator = get_translator(stem_flag,train)
    stem_timings = get_time_for_files(translator, test)
    print(stem_timings)

    stem_flag = False
    translator = get_translator(stem_flag,train)
    no_stem_timings = get_time_for_files(translator, test)
    print(no_stem_timings)
    # no_stem_timings = [0.0038259029388427734, 0.006392240524291992, 0.02004098892211914, 0.002846956253051758, 0.0021550655364990234, 0.0019381046295166016, 0.0041582584381103516, 0.003520965576171875, 0.008037805557250977, 0.00461888313293457, 0.0030059814453125, 0.0032432079315185547, 0.0032880306243896484, 0.0059812068939208984, 0.0033731460571289062]


    # Get minimum edit distance and bag of words for folds
    # stem_flag = True
    # med_results = []
    # bow_results = []
    # norm_med_results = []
    # for test,train in train_test_split:
    #     translator = get_translator(stem_flag,train)
    #     med,bow,med_per_tok = get_med_bow_norm(translator,test)
    #     med_results.append(med)
    #     bow_results.append(bow)
    #     norm_med_results.append(med_per_tok)
    # med_results =[161, 107, 134, 187, 89, 137, 88, 80, 129]
    # bow_results = [133, 95, 112, 163, 79, 101, 72, 68, 115]
    # norm_med_results = [0.369317992642206, 0.37611497673908006, 0.3236425998635301, 0.4144024663159457, 0.3221639569007991, 0.4996500046412327, 0.31268496652643, 0.3396377432091717, 0.38226477579364365]

    # Traditional dataset results
    i = 0
    med_results = []
    bow_results = []
    meds_list = []
    for test,train in test_train_split:
        translator = get_translator(True,train)
        med = 0
        bow = 0
        count = 0
        for ts,ps in test:
            if RANDOM_SHUFFLE_ORDER[i] >= 49:
                count += 1
                predict = translator(ts)
                med += minimum_edit_distance(predict,ps)
                meds_list.append(minimum_edit_distance(predict, ps))
                bow += bag_of_words_test(predict,ps)
            i += 1
        med_results.append(med)
        bow_results.append(bow)
        print(count)
    print(i, med_results)
    print(bow_results)
    print(sum(bow_results))
    print(meds_list)
    # stem_flag = False
    # med_results = []
    # bow_results = []
    # norm_med_results = []
    # for train,test in train_test_split:
    #     translator = get_translator(stem_flag,train)
    #     med,bow,med_per_tok = get_med_bow_norm(translator,test)
    #     med_results.append(med)
    #     bow_results.append(bow)
    #     norm_med_results.append(med_per_tok)
    #
    # med_results =[160, 107, 140, 189, 96, 143, 96, 90, 138]
    # bow_results = [132, 95, 118, 173, 88, 105, 76, 76, 126]
    # norm_med_results = [0.3623254695347719, 0.38169279761101854, 0.34206191203284225, 0.4144875833204712, 0.34251377375061587, 0.5217248731851415, 0.34648838532984877, 0.38706163823645034, 0.4048266029557861]




    # print("target",sum([199, 118, 170, 280, 115, 184, 75, 58, 161]))
    # print("orig",sum([160, 107, 140, 189, 96, 143, 96, 90, 138]))
    #
    # print(med_results)
    # print(sum(med_results))
    # print(bow_results)
    # print(norm_med_results)



