import math
import random

rec_en = [0.9, 0.9090909090909091, 0.6746987951807228, 0.8947368421052632, 1.0, 1.0, 0.8636363636363636, 0.9642857142857143]
prec_en = [0.9473684210526315, 0.8125, 0.75, 0.9375, 0.8888888888888888, 1.0, 0.9047619047619048, 0.9285714285714286]


rec_split = [0.85, 0.9090909090909091, 0.5662650602409639, 0.6842105263157895, 0.9, 0.8333333333333334, 0.9545454545454546, 0.6785714285714286]
prec_split = [1.0, 0.8846153846153846, 0.639344262295082, 0.625, 0.8, 1.0, 1.0, 0.7083333333333334]

med_enhanced = [4, 20, 74, 7, 2, 0, 0, 1, 3, 6, 5, 0, 11, 6, 2, 16, 0, 10, 3, 11, 4, 0, 4, 10, 5, 51, 1, 30, 8, 25, 9, 41, 21, 69, 1, 38, 8, 10, 7, 3, 0, 4, 14, 3, 1, 4, 20, 19, 6, 6, 27, 30, 4, 9, 9, 2, 8, 0, 7, 3, 8, 6, 4, 13, 4, 9, 3, 7, 0, 1, 0, 0, 14, 9, 1, 0, 48, 18, 6, 5, 8, 18, 3, 6]
med_baseline = [7, 19, 56, 4, 3, 3, 3, 2, 5, 5, 7, 1, 12, 8, 6, 11, 4, 21, 3, 12, 2, 7, 6, 23, 6, 39, 3, 27, 12, 14, 13, 46, 26, 27, 4, 27, 13, 9, 14, 5, 6, 8, 8, 7, 5, 2, 14, 22, 5, 7, 18, 21, 5, 4, 7, 6, 10, 5, 10, 10, 10, 10, 4, 16, 6, 7, 4, 2, 0, 1, 3, 1, 17, 11, 3, 7, 39, 9, 7, 6, 16, 17, 5, 11]


def next_exchange(cur_exchange):
    for i in range(len(cur_exchange)):
        if cur_exchange[i] == 0:
            cur_exchange[i] = 1
            return cur_exchange
        else:
            cur_exchange[i] = 0
    raise ValueError("No more values")

def get_diff_means(preds_a, preds_b, exchanges):
    tot_a = 0
    tot_b = 0
    for i,val in enumerate(exchanges):
        if val == 0:
            tot_a += preds_a[i]
            tot_b += preds_b[i]
        else:
            tot_b += preds_a[i]
            tot_a += preds_b[i]
    return abs(tot_a-tot_b)/len(preds_a)

def permutation_test(preds_a, preds_b):
    assert(len(preds_a) == len(preds_b))
    exchanges = [0 for _ in range(len(preds_a))]
    diff_means = get_diff_means(preds_a,preds_b,exchanges)
    more_extreme_count = 0
    try:
        while True:
            # print(exchanges)
            if get_diff_means(preds_a,preds_b,exchanges) >= diff_means:
                more_extreme_count += 1
            exchanges = next_exchange(exchanges)
    except:
        return more_extreme_count/ math.pow(2,len(preds_a))


def get_random_exchange(length):
    return [random.randint(0,1) for _ in range(length)]


def perm_test_random(preds_a, preds_b,num_perms):
    exchanges = [0 for _ in range(len(preds_a))]
    diff_means = get_diff_means(preds_a,preds_b,exchanges)
    more_extreme_count = 0
    for _ in range(num_perms):
        # print(exchanges)
        exchanges = get_random_exchange(len(preds_a))

        if get_diff_means(preds_a,preds_b,exchanges) >= diff_means:
            more_extreme_count += 1
    return more_extreme_count/num_perms

print(perm_test_random(med_baseline,med_enhanced,100000))
print(perm_test_random(med_baseline,med_enhanced,100000))
print(perm_test_random(med_baseline,med_enhanced,100000))
# print(permutation_test(rec_en,rec_split))
# print(permutation_test(prec_en,prec_split))
