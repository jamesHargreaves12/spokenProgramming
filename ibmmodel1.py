from itertools import product
from collections import defaultdict
from math import log,inf


def get_initial(sentance_pairs):
    e_lexicon = set()
    for _,e in sentance_pairs:
        e_lexicon.update(e)
    uniform = 1/len(e_lexicon)
    t_initial = defaultdict(lambda:uniform)
    return t_initial


def get_next_t_estimate(sentance_pairs,t):
    # using algoritm from http://mt-class.org/jhu/slides/lecture-ibm-model1.pdf
    # gives t(e|f)
    count = defaultdict(float)
    total = defaultdict(float)
    lexicon_e = set()
    lexicon_f = set()
    for fs,es in sentance_pairs:
        s_total = defaultdict(float)
        for f,e in product(fs,es):
            s_total[e] += t[(e,f)]
            lexicon_e.add(e)
            lexicon_f.add(f)
        for f,e in product(fs,es):
            count[(e,f)] += t[(e,f)]/s_total[e]
            total[f] += t[(e,f)]/s_total[e]
    for f,e in product(lexicon_f,lexicon_e):
        t[(e,f)] = count[(e,f)]/total[f]
    return t


def train(sentance_pairs,loop_count):
    with_null_token = [(["NULL"]+f,e) for f,e in sentance_pairs]
    t = get_initial(with_null_token)
    if __name__ != "__main__":
        print("Got initial")
    for i in range(loop_count):
        if i % 20 == 19:
            if __name__ != "__main__":
                print("Loop: "+str(i+1))
        t = get_next_t_estimate(with_null_token,t)
    return t

def get_best_pairing(t_f_given_e, fs, es):
    alignment = set()
    for _ in range(len(fs)):
        max_pairing_f = 0
        max_pairing_e = 0
        max_score = 0
        for i,f in enumerate(fs):
            for j,e in enumerate(es):
                if f != "" and t_f_given_e[(f,e)] >= max_score:
                    max_score = t_f_given_e[(f,e)]
                    max_pairing_f = i
                    max_pairing_e = j
        fs[max_pairing_f] = ""
        alignment.add((max_pairing_f,max_pairing_e))
    return alignment


def get_neighbours(point):
    x=point[0]
    y=point[1]
    points = [(x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1)]
    return filter(lambda a:a[0]>=0 and a[1]>=0,points)


def in_unique_row_col(point,cur_points):
    unique_row = True
    unique_col = True
    for cur_point in cur_points:
        if cur_point[0]== point[0]:
            unique_row = False
        if cur_point[1] == point[1]:
            unique_col = False
    return unique_row, unique_col


def get_phrase_alignment(t_e_given_f, t_f_given_e, fs, es, null_flag=True):
    # http://ivan-titov.org/teaching/elements.ws13-14/elements-7.pdf alg from here
    # likely can be improved using a data structure
    if null_flag:
        fs = ["NULL"] + fs
        es = ["NULL"] + es
    f_given_e_pairing = get_best_pairing(t_f_given_e, fs.copy(), es.copy())
    e_given_f_pairing = get_best_pairing(t_e_given_f, es.copy(), fs.copy())
    e_given_f_rev = [(y,x) for x,y in e_given_f_pairing]

    phrase_alignment = _get_phrase_alignmnet_by_symmetry(f_given_e_pairing,e_given_f_rev)
    if null_flag:
        # if maps to null then drop it in either direction and reduce the index by 1
        phrase_alignment = [(f-1,e-1) for f,e in phrase_alignment if f*e != 0]
    return phrase_alignment


def _get_phrase_alignmnet_by_symmetry(f_given_e_pairing,e_given_f_rev):
    alignment = f_given_e_pairing.intersection(e_given_f_rev)
    union = f_given_e_pairing.union(e_given_f_rev).difference(alignment)
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


def _extract_phrase(e_start, e_end, f_start, f_end, alignment, f_len):
    if f_end is -1:
        return []
    for f, e in alignment:
        if f_start <= f <= f_end and (e < e_start or e > e_end):
            return []
    f_aligned = [j for j,_ in alignment]
    phrases = []
    fs = f_start
    min_fs = 0
    while True:
        fe = f_end
        while True:
            phrases.append((e_start,e_end,fs,fe))
            fe += 1
            if fe in f_aligned or fe >= f_len:
                break
        fs -= 1
        if fs in f_aligned or fs < min_fs:
            break
    return phrases


def get_phrases(phrase_alignment, fs, es):
    # alg at: https://stackoverflow.com/questions/24970434/how-to-get-phrase-tables-from-word-alignments
    phrases = set()
    f_len = len(fs)
    for e_start in range(len(es)):
        for e_end in range(e_start, len(es)):
            f_start = f_len-1
            f_end = -1
            for f,e in phrase_alignment:
                if e_start <= e <= e_end:
                    f_start = min(f_start,f)
                    f_end = max(f_end,f)
            phrase = _extract_phrase(e_start, e_end, f_start, f_end, phrase_alignment, f_len)
            if phrase:
                for ei,ej,fi,fj in phrase:
                    phrases.add((" ".join(fs[fi:fj + 1])," ".join(es[ei:ej + 1])))
    return phrases


def get_phrase_probabilities(alignments,sentance_pairs,null_flag=True):
    if null_flag:
        sentance_pairs = [(fs,es) for fs,es in sentance_pairs]
    phrase_count = defaultdict(int)
    f_phrase_count = defaultdict(int)
    for i,align in enumerate(alignments):
        fs = sentance_pairs[i][0]
        es = sentance_pairs[i][1]
        phrases = get_phrases(align,fs,es)
        for f,e in phrases:
            phrase_count[(f,e)] += 1
            f_phrase_count[f] += 1
    phrase_probs = defaultdict(lambda :defaultdict(float))
    for f,e in phrase_count.keys():
        phrase_probs[f][e] = phrase_count[(f,e)] / f_phrase_count[f]
    return phrase_probs

def prune_phrase_table(phrase_table, max_length=5):
    f_deletes = []
    e_deletes = []
    for f,e_prob in phrase_table.items():
        if len(f.split(" ")) > max_length:
            f_deletes.append(f)
            continue
        for e,prob in e_prob.items():
            if len(e.split(" ")) > max_length:
                e_deletes.append((f,e))
    for f in f_deletes:
        phrase_table.pop(f)
    for f,e in e_deletes:
        phrase_table[f].pop(e)
        if len(phrase_table[f].keys()) == 0:
            phrase_table.pop(f)

def print_phrase_table(phrase_table):
    for f,e_prob in phrase_table.items():
        e_prob_string = "{"
        for e,prob in e_prob.items():
            e_prob_string += "'" + str(e) + "' = " + str(prob) + ", "
        print("'"+str(f) +"':" + e_prob_string + "}")


def save_phrase_table(phrase_table:defaultdict, filename):
    with open("phrase_table/"+filename, 'w') as file:
        file.write("Default = " + str(phrase_table.default_factory().default_factory())+"\n")
        for f,e_prob in phrase_table.items():
            file.write("********** f = "+f+"\n")
            for e,prob in e_prob.items():
                file.write(e +": "+str(prob)+"\n")


def open_phrase_table(filename):
    error_fn = lambda: print("ERROR: file not formed correctly")
    state = "DEFAULT"
    current_f = "qq"
    with open("phrase_table/"+filename,'r') as file:
        for line in file.readlines():
            line = line.strip("\n")
            if state == "DEFAULT":
                if line.startswith("Default = "):
                    default_val = float(line[len("Default = "):])
                    phrase_table = defaultdict(lambda : defaultdict(lambda : default_val))
                    state = "FIND_VALS"
                else:
                    error_fn()
                    break
            elif state == "FIND_VALS":
                if line.startswith("********** f"):
                    current_f = line.split(" = ")[1]
                elif ": " in line:
                    e,prob = line.rsplit(": ",1)
                    phrase_table[current_f][e] = float(prob)
    return phrase_table

def log_with_neginf(value):
    return log(value) if value != 0 else -inf

def get_log_phrase_table(phrase_table):
    default = phrase_table.default_factory().default_factory()
    log_default = log_with_neginf(default)
    log_phrase_table = defaultdict(lambda : defaultdict(lambda : log_default))
    for f,e_prob in phrase_table.items():
        for e,prob in e_prob.items():
            log_phrase_table[f][e] = log_with_neginf(prob)
    return log_phrase_table


if __name__ == "__main__":
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]

    t_e_given_f = train(sentance_pairs, 100)
    reversed = [(e,f) for f,e in sentance_pairs]
    t_f_given_e = train(reversed, 100)
    alignments = [get_phrase_alignment(t_e_given_f, t_f_given_e, es, ps, null_flag=True) for es, ps in sentance_pairs]
    phrase_probs = get_phrase_probabilities(alignments,sentance_pairs,null_flag=True)
    print("qq",alignments)

    log_phrase_table = get_log_phrase_table(phrase_probs)
# confident that this is right but that having NULL in small corpora does work:
# since both casa and null tokens in every sentance so indistiguishable as far as the model is concerned
    print()
    print_phrase_table(phrase_probs)
    print()
    print_phrase_table(log_phrase_table)
    print("HERE")
    fs = "c a b".split(" ")
    es = "x y".split(" ")
    print(get_phrases([(1,1)],fs,es))

    print(phrase_probs)
    # prune_phrase_table(phrase_probs,max_length=2)
    # print(phrase_probs)

# Testing:
    # get_initial()
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]
    calculated = get_initial(sentance_pairs)
    print(1,calculated.default_factory() == 0.2)

    # get_next_t_estimate()
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]
    initial_t = get_initial(sentance_pairs)
    next_t = get_next_t_estimate(sentance_pairs,initial_t)
    check_list = [(('the', 'la'), 0.3333333333333333), (('big', 'la'), 0.3333333333333333),
                  (('house', 'la'), 0.3333333333333333), (('the', 'casa'), 0.15789473684210528),
                  (('big', 'casa'), 0.15789473684210528), (('house', 'casa'), 0.2631578947368421),
                  (('green', 'casa'), 0.10526315789473684), (('green', 'pez'), 0.5),
                  (('house', 'pez'), 0.5), (('green', 'verde'), 0.5),
                  (('house', 'verde'), 0.5), (('shop', 'casa'), 0.31578947368421056),
                  (('shop', 'verde'), 0.0), (('the', 'verde'), 0.0),
                  (('big', 'verde'), 0.0), (('green', 'la'), 0.0),
                  (('shop', 'la'), 0.0), (('shop', 'pez'), 0.0),
                  (('the', 'pez'), 0.0), (('big', 'pez'), 0.0)]
    print(2,all([next_t[alignment] == prob for alignment,prob in check_list]))

    # train()
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]
    calculated = train(sentance_pairs, 100)
    check_list = [(('the', 'NULL'), 0.06886674196123023), (('big', 'NULL'), 0.06886674196123023),
                  (('house', 'NULL'), 0.5433997741163255), (('the', 'la'), 0.5),
                  (('big', 'la'), 0.5), (('house', 'la'), 4.166137961348552e-23),
                  (('the', 'casa'), 0.06886674196123023), (('big', 'casa'), 0.06886674196123023),
                  (('house', 'casa'), 0.5433997741163255), (('green', 'NULL'), 4.137935444428883e-39),
                  (('green', 'casa'), 4.137935444428883e-39), (('green', 'pez'), 0.7716998870581483),
                  (('house', 'pez'), 0.22830011294185173), (('green', 'verde'), 0.7716998870581483),
                  (('house', 'verde'), 0.22830011294185173), (('shop', 'NULL'), 0.318866741961214),
                  (('shop', 'casa'), 0.318866741961214)]
    print(3,all([calculated[alignment] == prob for alignment,prob in check_list]))

    #get_phrase_alignment()
    # this isnt a perfect test due to the dependency on the train function
    # but good enough for now
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]
    t_e_given_f = train(sentance_pairs, 100)
    reversed = [(e,f) for f,e in sentance_pairs]
    t_f_given_e = train(reversed, 100)
    alignments = [get_phrase_alignment(t_e_given_f, t_f_given_e, es, ps, null_flag=True) for es, ps in sentance_pairs]
    answer = [[(0, 1), (0, 0)], [(0, 1), (2, 0), (1, 0)], [(0, 0)]]
    print(4, alignments == answer)


    # _get_phrase_alignmnet_by_symmetry()
    # this is the "Mary did not slap the green witch example"
    f_given_e_pairing = set([(0, 0), (1, 2), (2, 3), (3, 3), (4, 3), (6, 4), (7, 6), (8, 5)])
    e_given_f_rev = set([(0, 0), (1, 1), (1, 2), (4, 3), (6, 4), (7, 6), (8, 5)])
    answer = {(1, 2), (6, 4), (0, 0), (3, 3), (7, 6), (2, 3), (4, 3), (8, 5), (1, 1)}
    calculated = _get_phrase_alignmnet_by_symmetry(f_given_e_pairing,e_given_f_rev)
    print(5, answer == calculated)

    # get_phrases()
    # again the this is the "Mary did not slap the green witch example"
    fs = "Maria no dio ́una bofetada a la bruja verde".split(" ")
    es = "Mary did not slap the green witch".split(" ")
    phrase_alignment = {(1, 2), (6, 4), (0, 0), (3, 3), (7, 6), (2, 3), (4, 3), (8, 5), (1, 1)}
    answer = {('verde', 'green'), ('dio ́una bofetada', 'slap'), ('no dio ́una bofetada', 'did not slap'), ('bruja', 'witch'), ('no dio ́una bofetada a la bruja verde', 'did not slap the green witch'), ('Maria', 'Mary'), ('dio ́una bofetada a la', 'slap the'), ('la', 'the'), ('Maria no dio ́una bofetada a la bruja verde', 'Mary did not slap the green witch'), ('no dio ́una bofetada a la', 'did not slap the'), ('bruja verde', 'green witch'), ('Maria no dio ́una bofetada', 'Mary did not slap'), ('no', 'did not'), ('a la', 'the'), ('no dio ́una bofetada a', 'did not slap'), ('dio ́una bofetada a', 'slap'), ('dio ́una bofetada a la bruja verde', 'slap the green witch'), ('Maria no dio ́una bofetada a', 'Mary did not slap'), ('a la bruja verde', 'the green witch'), ('Maria no dio ́una bofetada a la', 'Mary did not slap the'), ('Maria no', 'Mary did not'), ('la bruja verde', 'the green witch')}
    calculated = get_phrases(phrase_alignment,fs,es)
    print(6, calculated == answer)

    # get_phrase_probabilities()
    alignments = [[(0, 1), (0, 0)], [(0, 1), (2, 0), (1, 0)], [(0, 0)]]
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]
    calculated = get_phrase_probabilities(alignments,sentance_pairs)
    check_list = [(('la','the big house'), 0.5), (('la','the big'),0.5),
                  (('la casa', 'the big'), 0.5), (('la casa', 'the big house'), 0.5),
                  (('pez verde', 'green'), 1.0), (('casa pez verde', 'green house'), 1.0),
                  (('casa', 'house'), 0.5), (('casa', 'shop'), 0.5)]
    print(7,all([calculated[alignment[0]][alignment[1]] == prob for alignment,prob in check_list]))
