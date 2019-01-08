from itertools import product
from collections import defaultdict

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
    print("Got initial")
    for i in range(loop_count):
        if i % 20 == 19:
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


def get_alignment(t_e_given_f, t_f_given_e, fs, es, null_flag=True):
    # http://ivan-titov.org/teaching/elements.ws13-14/elements-7.pdf alg from here
    # likely can be improved using a data structure
    if null_flag:
        fs = ["NULL"] + fs
        es = ["NULL"] + es
    f_given_e_pairing = get_best_pairing(t_f_given_e, fs.copy(), es.copy())
    e_given_f_pairing = get_best_pairing(t_e_given_f, es.copy(), fs.copy())
    e_given_f_rev = [(y,x) for x,y in e_given_f_pairing]

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

    if null_flag:
        alignment = [(f,e) for f,e in alignment if f*e != 0]
    return alignment


def extract_phrase(e_start, e_end, f_start, f_end, alignment, f_len, null_flag=True):
    if f_end is -1:
        return []
    for f, e in alignment:
        if f_start <= f <= f_end and (e < e_start or e > e_end):
            return []
    f_aligned = [j for _,j in alignment]
    phrases = []
    fs = f_start
    min_fs = 1 if null_flag else 0
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


def get_phrases(alignment, fs, es, null_flag=True):
    # alg at: https://stackoverflow.com/questions/24970434/how-to-get-phrase-tables-from-word-alignments
    phrases = set()
    f_len = len(fs)
    for e_start in range(1, len(es)):
        for e_end in range(e_start, len(es)):
            f_start = f_len
            f_end = -1
            for f,e in alignment:
                if e_start <= e <= e_end:
                    f_start = min(f_start,f)
                    f_end = max(f_end,f)
            phrase = extract_phrase(e_start, e_end, f_start, f_end, alignment, f_len, null_flag=null_flag)
            if phrase:
                for ei,ej,fi,fj in phrase:
                    phrases.add((" ".join(fs[fi:fj + 1])," ".join(es[ei:ej + 1])))
    return phrases


def get_phrase_probabilities(alignments,sentance_pairs,null_flag=True):
    if null_flag:
        sentance_pairs = [(["NULL"]+fs,["NULL"]+es) for fs,es in sentance_pairs]
    phrase_count = defaultdict(int)
    f_phrase_count = defaultdict(int)
    for i,align in enumerate(alignments):
        fs = sentance_pairs[i][0]
        es = sentance_pairs[i][1]
        phrases = get_phrases(align,fs,es,null_flag=null_flag)
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

if __name__ == "__main__":
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]

    # sentance_pairs = [(["la"],["the"]),(["la","pez"],["the"]),(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"]),(["casa","verde"],["green","shop"])]
    t_e_given_f = train(sentance_pairs, 100)
    reversed = [(x,y) for y,x in sentance_pairs]
    t_f_given_e = train(reversed, 100)
    # sentance_pairs_with_null = [(["NULL"]+es,["NULL"]+ps) for es,ps in sentance_pairs]
    alignments = [get_alignment(t_e_given_f, t_f_given_e, es, ps, null_flag=True) for es, ps in sentance_pairs]
    phrase_probs = get_phrase_probabilities(alignments,sentance_pairs,null_flag=True)
    print("qq",alignments)
# confident that this is right but that having NULL in small corpora does work:
# since both casa and null tokens in every sentance so indistiguishable as far as the model is concerned
    print(phrase_probs)
    # prune_phrase_table(phrase_probs,max_length=2)
    # print(phrase_probs)
