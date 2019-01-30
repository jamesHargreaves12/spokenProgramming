from collections import defaultdict
from math import inf,log
import test_models


PREVENT_VARIABLE_TO_NULL_MAP = True

def prune_phrase_table(phrase_table, e_max_length=-1, f_max_length=-1):
    f_deletes = []
    e_deletes = []
    for f,e_prob in phrase_table.items():
        if len(f.split(" ")) > f_max_length and f_max_length > 0:
            f_deletes.append(f)
            continue
        for e,prob in e_prob.items():
            if len(e.split(" ")) > e_max_length and e_max_length > 0:
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


def get_best_pairing(t_f_given_e, fs, es, d_f_given_e=None):
    alignment = set()
    for j,f in enumerate(fs):
        max_score = -1
        max_index = -1
        for i,e in enumerate(es):
            score = t_f_given_e[(f,e)]
            if d_f_given_e:
                score *= d_f_given_e[(j,len(es),len(fs))][i]
            if score >= max_score and not (PREVENT_VARIABLE_TO_NULL_MAP and f.startswith("VARIABLE") and e == "NULL"):
                max_score = score
                max_index = i
        if max_score  == -1:
            print("ISSUE with pairing")
        else:
            alignment.add((j,max_index))

    # if '=' in fs:
    #     print(1)
    #     for_print_a = [(y,x) for x,y in alignment]
    #     test_models.print_alignment(for_print_a,(es,fs))
    # else:
    #     print(0)
    #     test_models.print_alignment(alignment,(fs,es))

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


def get_phrase_alignment_by_symmetry(f_given_e_pairing, e_given_f_rev):
    # print(f_given_e_pairing)
    # print(e_given_f_rev)
    alignment = f_given_e_pairing.intersection(e_given_f_rev)
    # print(alignment)
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
    # print("Mid way:")
    # print(alignment)
    #finalise
    for point in union:
        unique_row, unique_col = in_unique_row_col(point, alignment)
        if unique_row and unique_col:
            alignment.add(point)
    # print("end")
    # print(alignment)
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
    # from Philip Koehn's Statistical MT book, pp. 133
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
    # NULL FLAG?
    phrase_count = defaultdict(int)
    f_phrase_count = defaultdict(int)
    for i,align in enumerate(alignments):
        fs = sentance_pairs[i][0]
        es = sentance_pairs[i][1]
        phrases = get_phrases([(y,x) for x,y in align],fs,es)
        for f,e in phrases:
            phrase_count[(f,e)] += 1
            f_phrase_count[f] += 1
    phrase_probs = defaultdict(lambda :defaultdict(float))
    for f,e in phrase_count.keys():
        phrase_probs[f][e] = phrase_count[(f,e)] / f_phrase_count[f]
    return phrase_probs

p_table = open_phrase_table("p_table_m2.txt")
log_p_table = get_log_phrase_table(p_table)
save_phrase_table(log_p_table,"log_p_table_m2.txt")