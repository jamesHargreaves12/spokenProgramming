from itertools import product,permutations
from collections import defaultdict
import time

def get_initial(english_pseudo):
    p_lexicon = set()
    for english,pseudo in english_pseudo:
        p_lexicon.update(pseudo)
    uniform = 1/len(p_lexicon)
    t_initial = defaultdict(lambda:uniform)
    return t_initial

def find_alignments(es,ps,n):
    counts = [0 for _ in ps]
    counts[0] = len(es)
    alignment_mapping = [0 for i,_ in enumerate(es)]
    while True:
        assert(sum(counts) == len(es))
        yield [(es[i],ps[j]) for i,j in enumerate(alignment_mapping)]
        increment_alignment_with_count(0,alignment_mapping,counts)
        if sum(alignment_mapping) == 0:
            return


# find alignment with maximum count ie stops one pseudocode token mapping to entire file
len_counts = 0
len_alignment_mapping = 0
def increment_alignment_with_count(i,alignment_mapping, counts):
    """increments alignment_mapping starting at index i and keeps count up to date"""
    global len_counts
    global len_alignment_mapping
    changed = [i]
    alignment_mapping[i] += 1
    while alignment_mapping[i] == len_counts:
        alignment_mapping[i] = 0
        counts[-1] -= 1
        counts[0] += 1
        i += 1
        if i == len_alignment_mapping:
            return changed
        alignment_mapping[i] += 1
        changed.append(i)
    counts[alignment_mapping[i]-1] -= 1
    counts[alignment_mapping[i]] += 1
    return changed


def find_alignments2(es,ps,n):
    global len_counts
    global len_alignment_mapping
    counts = [0 for _ in ps]
    alignment_mapping = [0 for i,_ in enumerate(es)]
    len_counts = len(counts)
    len_alignment_mapping = len(alignment_mapping)
    counts[0] = len_counts
    orig_align = alignment_mapping.copy()
    changes = []
    current_alignment = [(es[i],ps[j]) for i,j in enumerate(alignment_mapping)]
    while True:
        # assert(sum(counts) == len(es) and max(counts[1:]) <= n)
        for index in changes:
            current_alignment[index] = (es[index],ps[alignment_mapping[index]])
        yield current_alignment
        changes = increment_alignment_with_count(0,alignment_mapping,counts)
        if alignment_mapping == orig_align:
            return
        while True:
            too_many = 0
            by_how_many = 0
            for c_i,c_val in enumerate(counts):
                if c_val > n and c_i != 0:
                    too_many = c_i
                    by_how_many = c_val-n
                    break
            if too_many:
                for j,x in enumerate(alignment_mapping):
                    if x == too_many:
                        if by_how_many == 1:
                            increment_alignment_with_count(j, alignment_mapping, counts)
                            if alignment_mapping == orig_align:
                                # Back at the start
                                return
                            break
                        else:
                            alignment_mapping[j] = 0
                            counts[x] -= 1
                            counts[0] += 1
                            by_how_many -= 1
                    else:
                        alignment_mapping[j] = 0
                        counts[x] -= 1
                        counts[0] += 1
            else:
                break

# es = "some rangom long story 2 4".split(" ")
# ps = "asdkfj jaldsjfsdj fajs ds".split(" ")
# print(len([x for x in find_alignments2(es,ps,3)]))
# print(len([x for x in find_alignments(es,ps)]))
# print(len([x for x in find_alignments2([x for x in range(21)],[0,1,2])]))
#
# for i,x in enumerate(find_alignments2("casa verde".split(" "),"green house".split(" "))):
#     print(x)
#     if i > 100:
# #         break
#
# es = ['VARIABLE', 'equals', 'VARIABLE', 'times', 'NUMBER', 'VARIABLE', 'equals', 'VARIABLE', 'plus', 'VARIABLE', 'times', 'NUMBER', 'and', 'then', 'return', 'VARIABLE', 'plus', 'VARIABLE', 'plus', 'VARIABLE']
# ps = ['VARIABLE', '=', 'VARIABLE', '*', 'NUMBER', 'VARIABLE', '=', '(', 'VARIABLE', '+', 'VARIABLE', ')', '*', 'NUMBER', 'return', 'VARIABLE', '+', 'VARIABLE', '+', 'VARIABLE']
#
# pairs = [(['VARIABLE', 'equals', 'VARIABLE', 'times', 'NUMBER'],['VARIABLE', '=', 'VARIABLE', '*', 'NUMBER']),
#          (['VARIABLE', 'equals', 'VARIABLE', 'plus', 'VARIABLE', 'times', 'NUMBER'],['VARIABLE', '=', 'VARIABLE', '+', 'VARIABLE', '*', 'NUMBER']),
#          (['return', 'VARIABLE', 'plus', 'VARIABLE', 'plus', 'VARIABLE'],['return', 'VARIABLE', '+', 'VARIABLE', '+', 'VARIABLE'])]
# print(len([e for e in es if e != "VARIABLE"]))

#
for i in range(2,20):
    print(i)
    a = [x for x in range(i)]
    b = [x for x in range(i)]
    rare_case_count = 0
    start = time.time()
    c = [x for x in find_alignments2(a,b,4)]
    print(time.time()-start)
    print(len(c))
    print()

def get_next_t_estimate2(english_pseudo,t):
    t_counts = defaultdict(float)
    p_total_count = defaultdict(float)
    for english,pseudo in english_pseudo:
        alignment_to_prob = []
        for alignment in find_alignments2(english, pseudo,3):
            prob_alignment = 1
            for e,p in alignment:
                prob_alignment *= t[(e,p)]
            alignment_to_prob.append((alignment.copy(),prob_alignment))
        total_prob = sum([prob for a,prob in alignment_to_prob])
        p_a_given_ep = [(a,prob/total_prob) for a,prob in alignment_to_prob]
        for align,prob_align in p_a_given_ep:
            for e,p in align:
                t_counts[(e,p)] += prob_align
                p_total_count[p] += prob_align
    next_t = {}
    # print(t_counts)
    for (e,p),v in t_counts.items():
        next_t[(e,p)] = v/p_total_count[p]
    return next_t


def train(english_pseudo,loop_count):
    t = get_initial(english_pseudo)
    with_null_token = [(x,["NULL"]+y) for x,y in english_pseudo]
    print("Got initial")
    for i in range(loop_count):
        print("Loop: "+str(i+1))
        t = get_next_t_estimate2(english_pseudo,t)
    return t


if __name__ == "__main__":
    english_pseudo = [("casa verde".split(" "),"green house".split(" ")),("la casa".split(" "),"the house".split(" "))]
    english_pseudo_orig = english_pseudo.copy()
    t1 = train(english_pseudo, 1)
    assert(t1 == {('verde', 'green'): 0.5, ('verde', 'house'): 0.25, ('casa', 'house'): 0.5, ('casa', 'green'): 0.5, ('casa', 'the'): 0.5, ('la', 'house'): 0.25, ('la', 'the'): 0.5})
    t2 = train(english_pseudo, 2)
    assert(t2 == {('casa', 'green'): 0.42857142857142855, ('verde', 'green'): 0.5714285714285714, ('casa', 'house'): 0.5999999999999999, ('verde', 'house'): 0.19999999999999998, ('la', 'the'): 0.5714285714285715, ('casa', 'the'): 0.4285714285714286, ('la', 'house'): 0.19999999999999998})
    assert(english_pseudo == english_pseudo_orig)

    pairs = [(['VARIABLE', 'equals', 'VARIABLE', 'times', 'NUMBER'], ['VARIABLE', '=', 'VARIABLE', '*', 'NUMBER']),
             (['VARIABLE', 'equals', 'VARIABLE', 'plus', 'VARIABLE', 'times', 'NUMBER'],['VARIABLE', '=', 'VARIABLE', '+', 'VARIABLE', '*', 'NUMBER']),
             (['return', 'VARIABLE', 'plus', 'VARIABLE', 'plus', 'VARIABLE'],['return', 'VARIABLE', '+', 'VARIABLE', '+', 'VARIABLE'])]
    t9 = train(pairs,9)
    # print(t9)
    t9_sorted = sorted([x for x in t9.items()], key=lambda x:x[1])
    print([x[0] for x in t9_sorted])
