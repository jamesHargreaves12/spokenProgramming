from itertools import product
from collections import defaultdict

def get_initial(sentance_pairs):
    p_lexicon = set()
    for e,p in sentance_pairs:
        p_lexicon.update(p)
    uniform = 1/len(p_lexicon)
    t_initial = defaultdict(lambda:uniform)
    return t_initial


def get_next_t_estimate(sentance_pairs,t):
    # using algoritm from http://mt-class.org/jhu/slides/lecture-ibm-model1.pdf
    count = defaultdict(float)
    total = defaultdict(float)
    lexicon_p = set()
    lexicon_e = set()
    for es,ps in sentance_pairs:
        s_total = defaultdict(float)
        for e,p in product(es,ps):
            s_total[e] += t[(e,p)]
            lexicon_p.add(p)
            lexicon_e.add(e)
        for e,p in product(es,ps):
            count[(e,p)] += t[(e,p)]/s_total[e]
            total[p] += t[(e,p)]/s_total[e]
    for e,p in product(lexicon_e,lexicon_p):
        t[(e,p)] = count[(e,p)]/total[p]
    return t


def train(sentance_pairs,loop_count):
    t = get_initial(sentance_pairs)
    with_null_token = [(x,["NULL"]+y) for x,y in sentance_pairs]
    print("Got initial")
    for i in range(loop_count):
        if i % 20 == 19:
            print("Loop: "+str(i+1))
        t = get_next_t_estimate(with_null_token,t)
    return t

def get_best_pairing(t,es,ps):
    alignemt = set()
    for _ in range(len(es)):
        max_pairing_e = 0
        max_pairing_p = 0
        max_score = 0
        for i,e in enumerate(es):
            for j,p in enumerate(ps):
                if e != "" and t[(e,p)] > max_score:
                    max_score = t[(e,p)]
                    max_pairing_e = i
                    max_pairing_p = j
        es[max_pairing_e] = ""
        alignemt.add((max_pairing_e,max_pairing_p))
    return alignemt


def get_neighbours(point):
    x=point[0]
    y=point[1]
    points = [(x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1)]
    return filter(lambda a:a[0]>=0 and a[1]>=0,points)


def get_non_diag_neighbours(point):
    x=point[0]
    y=point[1]
    return [(x,y-1),(x-1,y),(x+1,y),(x,y+1)]


def in_unique_row_col(point,cur_points):
    unique_row = True
    unique_col = True
    for cur_point in cur_points:
        if cur_point[0]== point[0]:
            unique_row = False
        if cur_point[1] == point[1]:
            unique_col = False
    return unique_row, unique_col


def get_alignment(t_p_to_e,t_e_to_p,es,ps):
    # http://ivan-titov.org/teaching/elements.ws13-14/elements-7.pdf alg from here
    # likely can be improved using a data structure
    p_to_e_pairing = get_best_pairing(t_p_to_e,es.copy(),ps.copy())
    e_to_p_pairing = get_best_pairing(t_e_to_p,ps.copy(),es.copy())
    reversed_e_to_p = [(y,x) for x,y in e_to_p_pairing]

    alignment = p_to_e_pairing.intersection(reversed_e_to_p)
    union = p_to_e_pairing.union(reversed_e_to_p).difference(alignment)
    to_check_stack = list(alignment)
    # diagonal
    while to_check_stack:
        point = to_check_stack.pop()
        for neighbour in union.intersection(get_neighbours(point)):
            unique_row,unique_col = in_unique_row_col(neighbour,alignment)
            if unique_row or unique_col:
                alignment.add(neighbour)
                to_check_stack.append(neighbour)
                union.remove(neighbour)
    #finalise
    for point in union:
        unique_row, unique_col = in_unique_row_col(point, alignment)
        if unique_row and unique_col:
            alignment.add(point)
    return alignment

def extract_phrase(e_start,e_end,f_start,f_end,alignment):
    if f_end is -1:
        return []
    for e, f in alignment:
        if f_start <= f <= f_end and (e < e_start or e > e_end):
            return []
    f_aligned = [j for _,j in alignment]
    f_largest = max(f_aligned)
    phrases = []
    fs = f_start
    while True:
        fe = f_end
        while True:
            phrases.append((e_start,e_end,fs,fe))
            fe += 1
            if fe in f_aligned or fe > f_largest:
                break
        fs -= 1
        if fs in f_aligned or fs < 0:
            break
    return phrases

def get_phrases(alignment, es, ps):
    # alg at: https://stackoverflow.com/questions/24970434/how-to-get-phrase-tables-from-word-alignments
    phrases = []
    for e_start in range(len(es)):
        for e_end in range(e_start,len(es)):
            f_start = len(ps)
            f_end = -1
            for e,f in alignment:
                if e_start <= e <= e_end:
                    f_start = min(f_start,f)
                    f_end = max(f_end,f)
            phrase = extract_phrase(e_start, e_end, f_start, f_end, alignment)
            if phrase:
                for ei,ej,fi,fj in phrase:
                    phrases.append((es[ei:ej+1],ps[fi:fj+1]))
    return phrases


def get_phrase_probabilities(alignments,sentance_pairs):
    phrase_count = defaultdict(int)
    e_phrase_count = defaultdict(int)
    for i,align in enumerate(alignments):
        es = sentance_pairs[i][0]
        ps = sentance_pairs[i][1]
        phrases = get_phrases(align,es,ps)
        for e,p in phrases:
            e_key = " ".join(e)
            p_key = " ".join(p)
            phrase_count[(e_key,p_key)] += 1
            e_phrase_count[e_key] += 1
    for e,p in phrase_count.keys():
        phrase_count[(e,p)] /= e_phrase_count[e]
    print(phrase_count)


if __name__ == "__main__":
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]
    # No Null currently
    with_pad = [(x,y) for x,y in sentance_pairs]
    p_to_e = train(sentance_pairs,100)
    reversed = [(x,y) for y,x in sentance_pairs]
    reversed_with_pad = [(x,y) for x,y in reversed]
    e_to_p = train(reversed_with_pad,100)
    alignments = [get_alignment(p_to_e,e_to_p,es,ps) for es,ps in sentance_pairs]
    get_phrase_probabilities(alignments,sentance_pairs)

    # es = "Mary did not slap the green witch".split(" ")
    # ps = "Maria no dio una bofetada a la bruja verde".split(" ")
    # alignment = [(0,0),(1,1),(2,1),(3,2),(3,3),(3,4),(4,5),(4,6),(5,8),(6,7)]
    # phrases = get_phrases(alignment,es,ps)
    # for e,p in phrases:
    #     print(" ".join(e) + "  =  " + " ".join(p))