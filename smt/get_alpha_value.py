import math

from smt import smt_functions
from smt.test_models import print_alignment
from test1 import train_test_data


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
                start_x += 1
                continue
            len_cur_set = len(cur_set)
            ys = [y for _,y in cur_set]
            min_y,max_y = min(ys),max(ys)
            cur_set = [(x,y) for x,y in alignment if min_y <= y <= max_y]
            new_points = not(len(cur_set) == len_cur_set)
            end_x = max([x for x,_ in cur_set])
        phrases.append((start_x,end_x,min_y,max_y))
        start_x = end_x+1
    return phrases


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


def get_probability(alignments,sentence_pairs):
    dss = []
    for i,align in enumerate(alignments):
        if i % 1 == 0:
            print(i)
        print_alignment(align,sentence_pairs[i])
        ps = get_smallest_phrase_set(align)
        ds = get_distances(ps)
        print(ds)
        dss.append(ds)
    return dss

epoch = 100
null_flag = True
alignments = smt_functions.get_alignment_1(train_test_data,epoch,null_flag)
print(get_probability(alignments[0:4],train_test_data[0:4]))