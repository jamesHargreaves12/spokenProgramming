from itertools import product
from collections import defaultdict

def get_initial(english_pseudo):
    e_lexicon = set()
    p_lexicon = set()
    for english,pseudo in english_pseudo:
        e_lexicon.update(english)
        p_lexicon.update(pseudo)

    t_initial = {}
    for eng,pseudo in product(e_lexicon,p_lexicon):
        t_initial[(eng,pseudo)] = 1/len(p_lexicon)
    return t_initial


def combinations(input):
    combinations = []
    so_far = []
    for i in input:
        new_combinations_l = [(l + [i],r) for l,r in combinations]
        new_combinations_r = [(l,r + [i]) for l,r in combinations]
        combinations = new_combinations_l + new_combinations_r
        combinations.append(([i],so_far))
        so_far = so_far + [i]
    combinations.append([[],input])
    return combinations


def find_alignments(e,ps):
    if len(ps) == 1:
        return [[(ps[0],e)]]
    p = ps[-1]
    choice_pairs = combinations(e)
    alignemnts = []
    for l,r in choice_pairs:
        if r == []:
            alignemnts += [[(p,l)]]
        elif l == []:
            alignemnts += find_alignments(r,ps[0:-1])
        else:
            rest_align = find_alignments(r,ps[0:-1])
            alignemnts += [ali + [(p,l)] for ali in rest_align]
    return alignemnts


def get_next_t_estimate2(english_pseudo,t):
    t_counts = defaultdict(float)
    p_total_count = defaultdict(float)
    for english,pseudo in english_pseudo:
        alignment_to_prob = []
        for alignment in find_alignments(english, pseudo):
            prob_alignment = 1
            for p,e_list in alignment:
                for e in e_list:
                    prob_alignment *= t[(e,p)]
            alignment_to_prob.append((alignment,prob_alignment))
        total_prob = sum([prob for a,prob in alignment_to_prob])
        p_a_given_ep = [(a,prob/total_prob) for a,prob in alignment_to_prob]
        for align,prob_align in p_a_given_ep:
            for p,e_list in align:
                for e in e_list:
                    t_counts[(e,p)] += prob_align
                    p_total_count[p] += prob_align
    next_t = {}
    for (e,p),v in t_counts.items():
        next_t[(e,p)] = v/p_total_count[p]
    return next_t


def train(english_pseudo,loop_count):
    t = get_initial(english_pseudo)
    for i in range(loop_count):
        print("Loop: "+str(i))
        t = get_next_t_estimate2(english_pseudo,t)
    return t


if __name__ == "__main__":
    english_pseudo = [("casa verde".split(" "),"green house".split(" ")),("la casa".split(" "),"the house".split(" "))]
    english_pseudo_orig = english_pseudo.copy()
    initial = get_initial(english_pseudo)
    t1 = get_next_t_estimate2(english_pseudo,initial)
    assert(t1 == {('verde', 'green'): 0.5, ('verde', 'house'): 0.25, ('casa', 'house'): 0.5, ('casa', 'green'): 0.5, ('casa', 'the'): 0.5, ('la', 'house'): 0.25, ('la', 'the'): 0.5})
    t2 = get_next_t_estimate2(english_pseudo,t1)
    assert(t2 == {('casa', 'house'): 0.6000000000000001, ('verde', 'house'): 0.2, ('verde', 'green'): 0.5714285714285715, ('casa', 'green'): 0.4285714285714286, ('la', 'house'): 0.2, ('casa', 'the'): 0.4285714285714286, ('la', 'the'): 0.5714285714285715})
    assert(english_pseudo == english_pseudo_orig)
    assert(t2 == train(english_pseudo, 2))