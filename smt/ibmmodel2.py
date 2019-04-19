from collections import defaultdict
from itertools import product
from math import inf
from smt import test_models, ibm_models, ibmmodel1
from smt.test_models import print_alignment
from tools.find_resource_in_project import get_path


def get_initial_t(sentence_pairs, m1_loop_count, null_flag=True, fm_flag=False):
    return ibmmodel1.train(sentence_pairs, m1_loop_count, null_flag=null_flag,fm_flag=fm_flag)


def get_next_estimate(t_e_given_f:dict, d_e_given_f:dict, sentence_pairs, null_flag, fm_flag=False):
    # http://www.ai.mit.edu/courses/6.891-nlp/l11.pdf
    # get the alignment probabilities
    a_ijk = {}
    n = len(sentence_pairs)
    # calculate the expected counts
    # t_count(e,f) is expected number of times that e is aligned with f in the corpus
    # s_count(e) is expected number of times that e is aligned with any French word in the corpus
    # a_count(i,j,l,m) is expected number of times that es[k][i] is aligned to fs[k][j] in English/French sentences of lengths l and m respectively
    # lm_count(l,m) is number of times that we have sentences e and f of lengths l and m respectively
    lexicon_e = set()
    lexicon_f = set()

    t_count = defaultdict(float)
    s_count = defaultdict(float)
    a_count = defaultdict(float)
    tot_a_count = defaultdict(float)
    for k in range(n):
        fs,es = sentence_pairs[k]
        l = len(es)
        m = len(fs)
        for j in range(m):
            total_for_i = 0
            for i in range(l):
                a_ijk[(i,j,k)] = ibm_models.d_fn(d_e_given_f, i, j - 1, l, m - 1) * t_e_given_f[es[i], fs[j]]
                total_for_i += a_ijk[(i,j,k)]
            # normalise
            if total_for_i > 0:
                for i in range(l):
                    a_ijk[(i,j,k)] /= total_for_i
    for k in range(n):
        fs,es = sentence_pairs[k]
        l = len(es)
        m = len(fs)
        for j in range(m):
            f = fs[j]
            lexicon_f.add(f)
            for i in range(l):
                e = es[i]
                lexicon_e.add(e)
                t_count[(e,f)] += a_ijk[(i,j,k)]
                s_count[e] += a_ijk[(i,j,k)]
                a_count[(i,j,l,m)] += a_ijk[(i,j,k)]
                tot_a_count[(j,l,m)] += a_ijk[(i,j,k)]
    # Re-estimate the paramaters
    d_e_given_f = defaultdict(lambda: defaultdict(float))
    for e,f in product(lexicon_e,lexicon_f):
        t_e_given_f[(e, f)] = t_count[(e, f)] / s_count[e]

    for k in range(n):
        fs,es = sentence_pairs[k]
        l = len(es)
        m = len(fs)
        for j in range(m):
            for i in range(l):
                # if k == 3:
                #     print(a_count[(i,j,l,m)],tot_a_count[(j,l,m)],l,m)
                if a_count[(i,j,l,m)] == 0:
                    d_e_given_f[(j-1, l, m-1)][i] = 0
                else:
                    d_e_given_f[(j - 1, l, m - 1)][i] = a_count[(i, j, l, m)] / tot_a_count[(j, l, m)]
    return t_e_given_f, d_e_given_f


def train(sentence_pairs, m1_loop_count, m2_loop_count, null_flag=True,t_filename=None,fm_flag=False):
    print("Train IBM_M1")
    d_e_given_f = {}
    if t_filename:
        t_e_given_f = ibmmodel1.open_t(t_filename)
    else:
        t_e_given_f = get_initial_t(sentence_pairs, m1_loop_count, null_flag, fm_flag=fm_flag)

    print("Train IBM_M2")
    if null_flag:
        sentence_pairs = [(["NULL"]+f,e) for f,e in sentence_pairs]
    for i in range(m2_loop_count):
        if i % 20 == 19:
            print("Loop:",i+1)
        t_e_given_f, d_e_given_f = get_next_estimate(t_e_given_f, d_e_given_f, sentence_pairs, null_flag, fm_flag=fm_flag)
    return t_e_given_f,d_e_given_f


def remove_t_maps_to_zero(t):
    removes = []
    for x in t:
        if t[x] == 0:
            removes.append(x)
    for rem in removes:
        t.pop(rem)
    return t


def save_d(d,filename):
    with open("distribution_table/"+filename, 'w') as file:
        for jlm,i_prob in d.items():
            file.write("********** jlm = "+str(jlm)+"\n")
            for i,prob in i_prob.items():
                file.write(str(i) +": "+str(prob)+"\n")


def open_dist_table(filename):
    error_fn = lambda: print("ERROR: file not formed correctly")
    current_jlm = None
    d_table = defaultdict(lambda: defaultdict(float))
    with open("distribution_table/"+filename,'r') as file:
        for line in file.readlines():
            line = line.strip("\n")
            if line.startswith("********** jlm"):
                current_jlm = line.split(" = ")[1]
            elif ": " in line:
                if not current_jlm:
                    error_fn()
                i,prob = line.rsplit(": ",1)
                d_table[current_jlm][int(i)] = float(prob)
    return d_table


def get_log_distribution_table(d):
    log_d_table = defaultdict(lambda : defaultdict(lambda : -inf))
    for jlm,i_prob in d.items():
        for i,prob in i_prob.items():
            log_d_table[jlm][i] = ibm_models.log_with_neginf(prob)
    return log_d_table



def get_phrase_alignment_2(t_e_given_f, d_e_given_f, t_f_given_e, d_f_given_e, fs, es, null_flag=True):
    # http://ivan-titov.org/teaching/elements.ws13-14/elements-7.pdf alg from here
    # likely can be improved using a data structure
    if null_flag:
        f_given_e_pairing = ibm_models.get_best_pairing(t_f_given_e, fs, ["NULL"]+es, d_f_given_e, null_flag)
        f_given_e_pairing = [(f,e-1) for f,e in f_given_e_pairing if e != 0]
        e_given_f_pairing = ibm_models.get_best_pairing(t_e_given_f, es, ["NULL"]+fs, d_e_given_f, null_flag)
        e_given_f_pairing = [(e,f-1) for e,f in e_given_f_pairing if f != 0]
        e_given_f_rev = [(y,x) for x,y in e_given_f_pairing]
        # print_alignment(f_given_e_pairing,(fs,es))
        # print_alignment(e_given_f_pairing,(es,fs))
        phrase_alignment = ibm_models.get_phrase_alignment_by_symmetry(f_given_e_pairing, e_given_f_rev)
        return phrase_alignment
    else:
        f_given_e_pairing = ibm_models.get_best_pairing(t_f_given_e, fs, es, d_f_given_e)
        e_given_f_pairing = ibm_models.get_best_pairing(t_e_given_f, es, fs, d_e_given_f)
        e_given_f_rev = [(y,x) for x,y in e_given_f_pairing]

        phrase_alignment = ibm_models.get_phrase_alignment_by_symmetry(f_given_e_pairing, e_given_f_rev)
        return phrase_alignment


def print_specific_d(d,l,m):
    for j in range(m):
        print(j,d[(j,l,m)])

def get_alignment_models_2(sentence_pairs, m1_loop_count, m2_loop_count, null_flag=True,fm_flag=False):
    t_e_given_f, d_e_given_f = train(sentence_pairs,m1_loop_count,m2_loop_count,null_flag,fm_flag=fm_flag)

    rev_pairs = [(y,x) for x,y in sentence_pairs]
    t_f_given_e, d_f_given_e = train(rev_pairs     ,m1_loop_count,m2_loop_count,null_flag,fm_flag=fm_flag)
    return t_e_given_f,d_e_given_f,t_f_given_e,d_f_given_e

def get_alignments_2(sentence_pairs, m1_loop_count, m2_loop_count, null_flag=True,fm_flag=False):
    t_e_given_f, d_e_given_f, t_f_given_e, d_f_given_e = get_alignment_models_2(sentence_pairs,m1_loop_count,m2_loop_count,null_flag,fm_flag)
    return [get_phrase_alignment_2(t_e_given_f, d_e_given_f, t_f_given_e, d_f_given_e, fs, es, null_flag) for fs,es in sentence_pairs]


def get_phrase_table_m2(sentence_pairs, alignments):
    # alignments = get_alignments_2(sentence_pairs,m1_loop_count,m2_loop_count,null_flag)
    # for i in range(5):
    #     test_pairs = sentence_pairs[i]
    #     get_phrase_alignment_2(t_e_given_f,d_e_given_f,t_f_given_e,d_f_given_e, test_pairs[0], test_pairs[1], null_flag)
    #     l,m =len(test_pairs[0]),len(test_pairs[1])
    #     print(l, m, (0, l, m) in d_e_given_f, (0, l, m) in d_f_given_e)
    #     test_models.print_alignment(alignments[i], test_pairs)
    return ibm_models.get_phrase_probabilities(alignments, sentence_pairs)



if __name__ == "__main__":
    f1 = "le chien".split(" ")
    e1 = "the dog".split(" ")
    f2 = "le chat".split(" ")
    e2 = "the cat".split(" ")
    f3 = "l autobus".split(" ")
    e3 = "the bus".split(" ")
    f4 = "chat".split(" ")
    e4 = "cat".split(" ")
    sentence_pairs = [(f1,e1),(f2,e2),(f3,e3),(f4,e4)]
    print(get_phrase_table_m2(sentence_pairs,100,1,True))
    # t_e_given_f,d_e_given_f = train(sentence_pairs,20,1,True)
    # print(t_e_given_f)
    # print(d_e_given_f)