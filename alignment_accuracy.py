import get_data
from smt import smt_functions, ibmmodel1, ibm_models, ibmmodel2
import matplotlib.pyplot as plt

from smt.test_models import print_alignment

alignments = [
    [(0,1),(1,0),(2,1),(3,2),(4,3),(5,4),(6,8),(7,5),(8,6),(9,7),(10,8),(11,9),(12,10),(13,11),(14,15),(15,12),(16,13),(17,14),(18,15),(19,16)],
    [(0,0),(1,1),(2,2),(3,2),(4,2),(5,3),(6,4),(7,5),(8,5),(9,5),(10,8),(11,9),(12,10),(13,12),(14,14),(14,15),(15,13),(16,16),(17,19),(19,20),(20,21),(21,21),(22,21),(23,21),(24,24),(26,25),(27,27),(28,28),(30,30),(31,31),(36,32),(37,33)],
    [(4,0),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(13,2),(16,3),(18,6),(21,9),(24,7),(26,5),(27,5),(28,5),(29,4),(32,12),(38,13),(35,15),(46,10),(40,11),(41,11),(42,11),(49,16),(53,17),(55,17),(56,17),(57,18),(51,19),(53,20),(55,20),(56,20),(57,21),(63,25),(67,22),(68,26),(69,27),(70,29),(71,30),(73,31),(74,32),(77,34),(78,34),(80,33),(76,35),(81,36),(82,36),(83,36),(85,39),(86,38),(87,38),(92,42),(90,43),(93,41),(94,41),(100,46),(101,45),(102,45),(104,44),(106,48),(106,49),(107,47),(108,51),(109,55),(111,54),(112,53),(113,53),(116,55),(117,55),(119,58),(120,57),(121,57),(123,56),(125,60),(125,61),(126,59),(131,63),(132,64)],
    [(0,1),(5,0),(3,2),(4,2),(6,3),(9,4),(10,5),(11,6),(12,7),(13,8),(14,9,),(15,9),(16,9),(17,10),(18,11),(19,12),(21,13),(25,14),(26,15)],
    [(0,3),(1,2),(2,3),(3,4),(5,1),(11,0),(13,5),(14,6),(15,7),(16,7),(17,8)],
    [(0,0),(1,1),(2,2),(3,2),(6,3),(8,4)],
    [(0,0),(1,1),(2,2),(4,3),(5,4),(8,5),(11,6),(12,7),(13,8),(15,9),(16,10),(17,11),(18,12),(19,12),(20,12),(21,13),(22,14),(23,15),(24,16),(26,17),(31,18),(19,33)],
    [(0,0),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,11),(13,11),(14,12),(15,13),(16,14),(17,15),(18,16),(19,17),(20,18),(21,19),(22,20),(23,21),(24,22),(25,23),(28,24),(29,25)],
]

test, train = get_data.train_test_split[0]
n = 2
epoch = 100
null_flag = True
fm_flag = True

def get_pred_align_test_1(train,test):
    t_e_given_f,t_f_given_e = ibmmodel1.get_alignment_models_1(train, epoch, null_flag,fm_flag)
    return [ibmmodel1.get_phrase_alignment(t_e_given_f,t_f_given_e,fs,es,null_flag) for fs,es in test]


def get_pred_align_test_2(train,test):
    t_e_given_f, d_e_given_f, t_f_given_e, d_f_given_e = ibmmodel2.get_alignment_models_2(train,epoch,epoch,null_flag,fm_flag)
    return [ibmmodel2.get_phrase_alignment_2(t_e_given_f, d_e_given_f, t_f_given_e, d_f_given_e, fs, es, null_flag) for fs,es in test]

def score_alignment_recall(pred_aligns):
    results = []
    for i in range(len(alignments)):
        pred_align = pred_aligns[i]
        true_align = alignments[i]
        score = 0
        for pair in true_align:
            if pair in pred_align:
                score += 1
        results.append(score / len(true_align))
        # print(len(true_align),score/len(true_align))
    return results

def score_alignment_precision(pred_aligns):
    results = []
    for i in range(len(alignments)):
        pred_align = pred_aligns[i]
        true_align = alignments[i]
        score = 0
        for pair in pred_align:
            if pair in true_align:
                score += 1
        results.append(score / len(pred_align))
        # print(len(true_align),score/len(true_align))
    return results


def ibm_model1():
    pred_aligns = get_pred_align_test_1(train,test)
    return score_alignment_precision(pred_aligns)


def ibm_model2():
    pred_aligns = get_pred_align_test_2(train,test)
    return score_alignment_precision(pred_aligns)

def combine_split_aligns(pred_aligns,split_test,test):
    result = []
    cur_test_index = 0
    prev_e_start = 0
    prev_f_start = 0
    current_alignment = []
    for i,split in enumerate(split_test):
        assert(prev_e_start + len(split[0]) <= len(test[cur_test_index][0]))
        assert(prev_f_start + len(split[1]) <= len(test[cur_test_index][1]))
        current_alignment.extend([(e+prev_e_start,f+prev_f_start) for e,f in pred_aligns[i]])
        prev_e_start += len(split[0])
        prev_f_start += len(split[1])
        if prev_e_start == len(test[cur_test_index][0]):
            cur_test_index += 1
            result.append(current_alignment)
            current_alignment = []
            prev_e_start = 0
            prev_f_start = 0
    return result


def split_model1():
    split_train = get_data.split_data(train)
    split_test = get_data.split_data(test)
    pred_aligns = get_pred_align_test_1(split_train,split_test)
    combined_aligns = combine_split_aligns(pred_aligns,split_test,test)
    return score_alignment_precision(combined_aligns)

def split_model2():
    split_train = get_data.split_data(train)
    split_test = get_data.split_data(test)
    pred_aligns = get_pred_align_test_2(split_train,split_test)
    combined_aligns = combine_split_aligns(pred_aligns,split_test,test)
    # for i in range(len(pred_aligns)):
    #     print_alignment(pred_aligns[i],split_test[i])
    return score_alignment_precision(combined_aligns)

# Recall:
ibm_v1 = [0.35, 0.5625, 0.21794871794871795, 0.6842105263157895, 0.6363636363636364, 0.8333333333333334, 0.5454545454545454, 0.42857142857142855]
average = sum(ibm_v1)/len(ibm_v1)
# 0.5322977734984314
ibm_v2 = [0.9, 0.6875, 0.3717948717948718, 0.8421052631578947, 0.8181818181818182, 0.6666666666666666, 0.9090909090909091, 0.7857142857142857]
average = sum(ibm_v2)/len(ibm_v2)
# 0.7476317268258058
split_v1 = [0.35, 0.71875, 0.3974358974358974, 0.8947368421052632, 0.9090909090909091, 0.8333333333333334, 0.6363636363636364, 0.5714285714285714]
average = sum(split_v1)/len(split_v1)
# 0.6638923987197014
split_v2 = [0.35, 0.8125, 0.44871794871794873, 0.6842105263157895, 0.9090909090909091, 0.6666666666666666, 0.9545454545454546, 0.9642857142857143]
average = sum(split_v2)/len(split_v2)
# 0.7237521524528104


# Precision:
# print(ibm_model1())
ibm_v1 = [1.0, 0.782608695652174, 0.6071428571428571, 0.8666666666666667, 0.5384615384615384, 0.5, 0.8571428571428571, 1.0]
average = sum(ibm_v1)/len(ibm_v1)
# 0.7690028268832616
# print(ibm_model2())
ibm_v2 = [1.0, 0.8148148148148148, 0.5087719298245614, 0.8, 0.6923076923076923, 0.8, 0.8333333333333334, 0.8461538461538461]
average = sum(ibm_v2)/len(ibm_v2)
# 0.7869227020542809
# print(split_model1())
split_v1 = [1.0, 0.7857142857142857, 0.7380952380952381, 0.8095238095238095, 0.7142857142857143, 1.0, 0.9333333333333333, 0.7619047619047619]
average = sum(split_v1)/len(split_v1)
# 0.8428571428571429
# print(split_model2())
split_v2 = [0.4375, 0.9259259259259259, 0.5072463768115942, 0.7333333333333333, 0.8333333333333334, 1.0, 0.9545454545454546, 1.0]
average = sum(split_v2)/len(split_v2)
# 0.7989855529937053

# plt.plot(ibm_v1,label='ibm_v1')
# plt.plot(ibm_v2,label='ibm_v2')
# plt.plot(split_v1,label='split_v1')
# plt.plot(split_v2,label='split_v2')
# plt.legend()
# plt.show()
