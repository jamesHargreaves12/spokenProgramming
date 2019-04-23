from other.log_module import write_to_log
from tests.bag_of_words_test import bag_of_words_test
from tests.minimum_edit_distance import minimum_edit_distance, minimum_edit_distance_per_token


def get_med_bow_norm(translator,test_set):
    meds = 0
    bows = 0
    meds_per_tok = 0
    for ts, truth in test_set:
        predict = translator(ts)
        pred_str = " ".join(predict)
        write_to_log("predict: "+pred_str+"\n")
        # print(pred_str)
        med = minimum_edit_distance(predict, truth)
        # write_to_log(str(med)+"\n")
        meds += med
        bows += bag_of_words_test(predict, truth)
        meds_per_tok += minimum_edit_distance_per_token(predict, truth)
    return meds,bows,meds_per_tok/len(test_set)
