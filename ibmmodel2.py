from collections import defaultdict
from scipy.stats import norm
from itertools import product
import general
from math import inf
import ibmmodel1
from types import FunctionType
import time
import ibm_models
import test_models

d_cache = {}
def load_d_cache():
    count = 0
    with open("default_d_cache/cache.txt","r") as file:
        for line in file.readlines():
            count += 1
            line.strip("\n")
            maps = line.split(" ")
            if len(maps) < 5:
                print(count,maps,line)
            d_cache[(int(maps[0]),int(maps[1]),int(maps[2]),int(maps[3]))] = float(maps[4])


D_SIGMA = lambda x: x/1.96
load_d_cache()
d_cache_file = open("default_d_cache/cache.txt","a")
def default_d(i,j,l,m):
    if (i,j,l,m) in d_cache:
        return d_cache[(i,j,l,m)]
    # l = len e
    # m = len f
    # i -> e
    # j -> f
    sigma = D_SIGMA(l/2)
    mu = j * (l-1) / (m-1)
    start = ((i - 0.5) - mu) / sigma
    end = ((i + 0.5) - mu) / sigma
    total_start = ((-0.5) - mu) / sigma
    total_end = ((l - 0.5) - mu) / sigma
    # print(start,end,total_start,total_end,mu,sigma)
    value = (norm.cdf(end) - norm.cdf(start))/(norm.cdf(total_end) - norm.cdf(total_start))
    d_cache_file.write(str(i) + " " + str(j) + " " + str(l) + " " + str(m) + " " + str(value) + "\n")
    return value

def get_initial_t(sentance_pairs, m1_loop_count, null_flag=True):
    # probably would like to get this from a file for speed
    return ibmmodel1.train(sentance_pairs,m1_loop_count,null_flag=null_flag)

def d_fn(d_dict:dict,i,j,l,m):
    if((j,l,m) in d_dict and i in d_dict[(j,l,m)]):
        return d_dict[(j,l,m)][i]
    return default_d(i,j,l,m)


def get_next_estimate(t:dict,d:dict,sentence_pairs):
    # http://www.ai.mit.edu/courses/6.891-nlp/l11.pdf
    # get the alignment probabilities

    a_ijk = {}
    n = len(sentence_pairs)
    for k in range(n):
        fs,es = sentence_pairs[k]
        l = len(es)
        m = len(fs)
        for j in range(m):
            total_for_i = 0
            for i in range(l):
                a_ijk[(i,j,k)] = d_fn(d,i,j,l,m)*t[es[i],fs[j]]
                total_for_i += a_ijk[(i,j,k)]
            # normalise
            if total_for_i > 0:
                for i in range(l):
                    a_ijk[(i,j,k)] /= total_for_i
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
    d = defaultdict(lambda: defaultdict(float))
    for e,f in product(lexicon_e,lexicon_f):
        t[(e,f)] = t_count[(e,f)]/s_count[e]

    for k in range(n):
        fs,es = sentence_pairs[k]
        l = len(es)
        m = len(fs)
        for j in range(m):
            for i in range(l):
                # if k == 3:
                #     print(a_count[(i,j,l,m)],tot_a_count[(j,l,m)],l,m)
                d[(j,l,m)][i] = a_count[(i,j,l,m)]/tot_a_count[(j,l,m)]
    return t,d

def train(sentence_pairs, m1_loop_count, m2_loop_count, null_flag=True,t_filename=None):
    print("Train IBM_M1")
    d = {}
    if t_filename:
        t = ibmmodel1.open_t(t_filename)
    else:
        t = get_initial_t(sentence_pairs, m1_loop_count, null_flag)
        ibmmodel1.save_t(t,"t_2.txt")

    print("Train IBM_M2")
    if null_flag:
        sentence_pairs = [(["NULL"]+x,y) for x,y in sentence_pairs]
    for i in range(m2_loop_count):
        print("Loop count:",i+1)
        t, d = get_next_estimate(t, d, sentence_pairs)
        # print(d)
    # print(t)
    return t,d

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


def get_phrase_alignment_2(t_e_given_f,d_e_given_f, t_f_given_e, d_f_given_e, fs, es, null_flag=True):
    # http://ivan-titov.org/teaching/elements.ws13-14/elements-7.pdf alg from here
    # likely can be improved using a data structure
    # es_2 = es
    # fs_2 = fs
    if null_flag:
        fs = ["NULL"] + fs
        es = ["NULL"] + es

    f_given_e_pairing = ibm_models.get_best_pairing(t_f_given_e, fs, es, d_f_given_e)
    e_given_f_pairing = ibm_models.get_best_pairing(t_e_given_f, es, fs, d_e_given_f)
    # print(f_given_e_pairing)
    # print(e_given_f_pairing)
    # print()

    # print(t_f_given_e)
    # print(d_e_given_f)
    # print(ibm_models.get_best_pairing(t_f_given_e, fs, es_2))
    e_given_f_rev = [(y,x) for x,y in e_given_f_pairing]

    phrase_alignment = ibm_models.get_phrase_alignment_by_symmetry(f_given_e_pairing, e_given_f_rev)
    if null_flag:
        # if maps to null then drop it in either direction and reduce the index by 1
        phrase_alignment = [(f-1,e-1) for f,e in phrase_alignment if f*e != 0]
    return phrase_alignment

def print_specific_d(d,l,m):
    for j in range(m):
        print(j,d[(j,l,m)])

def get_phrase_table_m2(sentence_pairs,m1_loop_count,m2_loop_count,null_flag=True):
    test_index = 3
    test_pairs = sentence_pairs[test_index]
    # print(test_pairs,len(test_pairs[1]),len(test_pairs[0]))

    t_e_given_f,d_e_given_f = train(sentence_pairs,m1_loop_count,m2_loop_count,null_flag,t_filename="t_1.txt")
    # print_specific_d(d_e_given_f,len(test_pairs[1]),len(test_pairs[0]))

    rev_pairs = [(y,x) for x,y in sentence_pairs]
    t_f_given_e,d_f_given_e = train(rev_pairs,m1_loop_count,m2_loop_count,null_flag,t_filename="t_2.txt")
    # print_specific_d(d_f_given_e,len(test_pairs[0]),len(test_pairs[1]))
    # alignment =(get_phrase_alignment_2(t_e_given_f, d_e_given_f, t_f_given_e, d_f_given_e, test_pairs[1],test_pairs[0],null_flag))

    alignments = [get_phrase_alignment_2(t_e_given_f, d_e_given_f, t_f_given_e, d_f_given_e, es,fs,null_flag) for fs,es in sentence_pairs]
    test_models.print_alignment([(y,x)  for x,y in alignments[test_index]],test_pairs)
    print(ibm_models.get_phrases([(y,x) for x,y in alignments[test_index]],test_pairs[0],test_pairs[1]))
    # print(ibm_models.get_phrases(alignments[test_index],test_pairs[0],test_pairs[1]))
    return ibm_models.get_phrase_probabilities(alignments,sentence_pairs,null_flag=null_flag)


# sentence_pairs = general.get_sentance_pairs()
# get_phrase_table_m2(sentence_pairs)


# ibm_models.save_ phrase_table(t,"new_phrase_table_m2.txt")

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