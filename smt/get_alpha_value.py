import math

from get_data import train_test_data
from smt import smt_functions
from smt.test_models import print_alignment
from scipy.optimize import minimize
import numpy as np


def remove_swallowed_phrases(phrases:list):
    phrases.sort(key=lambda x:(x[0],-x[1]))
    swallow = True
    while swallow:
        swallow = False
        remove_list = []
        for i in range(len(phrases)-1):
            if phrases[i][1] > phrases[i+1][1]:
                remove_list.append(i+1)
        for i,j in enumerate(remove_list):
            phrases.pop(j-i)
            swallow = True
    return phrases

def get_smallest_phrase_set(alignment):
    max_x = max([x for x,_ in alignment])
    start_x = 0
    phrases = []
    while start_x <= max_x:
        new_points = True
        end_x = start_x
        cur_set = []
        min_y=-1
        max_y=-1
        while new_points and start_x <= max_x:
            cur_set = [(x,y) for x,y in alignment if start_x <= x <= end_x]
            if not cur_set:
                end_x += 1
                if end_x <= max_x:
                    continue
                else:
                    break
            len_cur_set = len(cur_set)
            ys = [y for _,y in cur_set]
            min_y,max_y = min(ys),max(ys)
            cur_set = [(x,y) for x,y in alignment if min_y <= y <= max_y]
            new_points = not(len(cur_set) == len_cur_set)
            xs = [x for x,_ in cur_set]
            start_x,end_x = min(xs+[start_x]),max(xs)
        if end_x <= max_x:
            phrases.append((start_x,end_x,min_y,max_y))
        start_x = end_x+1
    return remove_swallowed_phrases(phrases)


def get_distances(phrases):
    distances = []
    sorted_ps = sorted(phrases,key=lambda x:x[2])
    prev = (-1,-1,-1,-1)
    for cur in sorted_ps:
        dist = abs(cur[0] - prev[1] - 1)
        distances.append(dist)
        prev = cur
    return distances


alpha = 0.1
def probability_distance(d,n,i):
    num = math.pow(alpha,d)
    den = 0
    for j in range(n):
        power = abs(i-j)
        den += math.pow(alpha,power)
    return num/den


def get_distances_of_alignments(alignments):
    dss = []
    for i,align in enumerate(alignments):
        ps = get_smallest_phrase_set(align)
        ds = get_distances(ps)
        dss.append(ds)
    return dss


def get_alpha(alignments):
    dss = get_distances_of_alignments(alignments)
    len_d = (sum([len(ds) for ds in dss]))
    sum_d = (sum([sum(ds) for ds in dss]))
    return sum_d/(len_d+sum_d)

cache = {}
def bounded_total_prob(alpha,n,minimumBound:True):
    if (alpha,n,minimumBound) in cache:
        return cache[alpha,n,minimumBound]
    sum_term = 0
    for d in range(1,n):
        sum_term += pow(alpha,d)
    result = 1+sum_term + (sum_term if not minimumBound else 0)
    cache[alpha, n, minimumBound] = result
    return result



def get_log_probability_of_data_given_alpha(alignments,sentence_pairs,alpha):
    dss = get_distances_of_alignments(alignments)
    log_prob_data = 0
    for i,ds in enumerate(dss):
        n = len(sentence_pairs[i][0])
        total_prob = bounded_total_prob(alpha,n,minimumBound=False)
        log_prob_data += math.log(alpha)*sum(ds) - len(ds)*math.log(total_prob)
    return log_prob_data


if __name__ == "__main__":
    epoch = 100
    null_flag = True
    alignments1 = smt_functions.get_alignment_1(train_test_data,epoch,null_flag)
    print(get_alpha(alignments1))
    # gets alpha as 0.7788829380260138 (for english -> pseudocode)
    alignments2 = smt_functions.get_alignment_2(train_test_data,epoch,null_flag)
    print(get_alpha(alignments2))
    # gets alpha as 0.7042902967121091 (for english -> pseudocode)
    # gets alpha as 0.67335562987 (for pseudocode -> english)
    # TODO this uses the approximation that d is distributed to infinity - compute it without this approximation.

    # constraints = ({'type':'ineq', 'fun':lambda x: x[0]})
    # for alpha_100 in range(1,100):
    #     alpha = alpha_100 / 100
    #     prob_data = get_log_probability_of_data_given_alpha(alignments2,train_test_data,alpha)
    #     print(alpha,prob_data)

    # TODO this hasnt worked come back to it if time