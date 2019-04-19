from itertools import product
from collections import defaultdict
from smt import ibm_models, test_models
from smt.constants import forced_mappings
from smt.ibm_models import get_best_pairing
from smt.test_models import print_alignment
from tools.find_resource_in_project import get_path


def get_initial(sentance_pairs,fm_flag=False):
    f_lexicon = set()
    for f,_ in sentance_pairs:
        f_lexicon.update(f)
    uniform = 1/len(f_lexicon)
    t_initial = defaultdict(lambda:uniform)
    if fm_flag:
        for k in forced_mappings:
            t_initial[(k,forced_mappings[k])] = 1
    return t_initial


def get_next_t_estimate(sentence_pairs, t_e_given_f,fm_flag=False):
    # using algoritm from http://mt-class.org/jhu/slides/lecture-ibm-model1.pdf
    # gives t(e|f)
    count = defaultdict(float)
    total = defaultdict(float)
    lexicon_e = set()
    lexicon_f = set()
    for fs,es in sentence_pairs:
        s_total = defaultdict(float)
        for f,e in product(fs,es):
            s_total[e] += t_e_given_f[(e, f)]
            lexicon_e.add(e)
            lexicon_f.add(f)
        for f,e in product(fs,es):
            count[(e,f)] += t_e_given_f[(e, f)] / s_total[e]
            total[f] += t_e_given_f[(e, f)] / s_total[e]
    for f,e in product(lexicon_f,lexicon_e):
        if fm_flag and f in forced_mappings:
            t_e_given_f[(e,f)] = 1 if forced_mappings[f] == e else 0
        else:
            t_e_given_f[(e, f)] = count[(e, f)] / total[f]
    return t_e_given_f


def train(sentence_pairs, loop_count, null_flag=True,fm_flag=False):
    if null_flag:
        sentence_pairs = [(["NULL"]+f,e) for f,e in sentence_pairs]
    t_e_given_f = get_initial(sentence_pairs,fm_flag=fm_flag)
    for i in range(loop_count):
        if i % 20 == 19 and __name__ != "__main__":
            print("Loop: "+str(i+1))
        t_e_given_f = get_next_t_estimate(sentence_pairs,t_e_given_f,fm_flag=fm_flag)
    return t_e_given_f


def get_phrase_alignment(t_e_given_f, t_f_given_e, fs, es, null_flag=True):
    # http://ivan-titov.org/teaching/elements.ws13-14/elements-7.pdf alg from here
    # likely can be improved using a data structure
    if null_flag:
        fs_null = ["NULL"] + fs
        es_null = ["NULL"] + es

        f_given_e_pairing = ibm_models.get_best_pairing(t_f_given_e, fs, es_null)
        f_given_e_pairing = [(f,e-1) for f,e in f_given_e_pairing if e != 0]

        e_given_f_pairing = ibm_models.get_best_pairing(t_e_given_f, es, fs_null)
        e_given_f_pairing = [(e,f-1) for e,f in e_given_f_pairing if f != 0]
        e_given_f_rev = [(y,x) for x,y in e_given_f_pairing]

        phrase_alignment = ibm_models.get_phrase_alignment_by_symmetry(f_given_e_pairing, e_given_f_rev)
        return phrase_alignment
    else:
        f_given_e_pairing = ibm_models.get_best_pairing(t_f_given_e, fs, es)
        e_given_f_pairing = ibm_models.get_best_pairing(t_e_given_f, es, fs)
        e_given_f_rev = [(y,x) for x,y in e_given_f_pairing]

        phrase_alignment = ibm_models.get_phrase_alignment_by_symmetry(f_given_e_pairing, e_given_f_rev)
        return phrase_alignment


def get_alignment_models_1(sentence_pairs,epoch=100,null_flag=True,fm_flag=False):
    t_e_given_f = train(sentence_pairs,epoch,null_flag,fm_flag=fm_flag)
    rev_pairs = [(y,x) for x,y in sentence_pairs]
    t_f_given_e = train(rev_pairs,epoch,null_flag,fm_flag=fm_flag)
    return t_e_given_f,t_f_given_e


def get_alignments_1(sentence_pairs,epoch=100,null_flag=True,fm_flag=False):
    t_e_given_f,t_f_given_e = get_alignment_models_1(sentence_pairs,epoch,null_flag,fm_flag)
    return [get_phrase_alignment(t_e_given_f,t_f_given_e,fs,es,null_flag) for fs,es in sentence_pairs]


def get_phrase_table_m1(alignments,sentence_pairs):
    return ibm_models.get_phrase_probabilities(alignments, sentence_pairs)


def save_t(t:defaultdict,filename):
    with open(get_path("/t_models/"+filename),"w") as file:
        file.write(str(t.default_factory())+"\n")
        for k,v in t.items():
            file.write(str(k[0])+"qq"+str(k[1]) +" q:q "+ str(v)+"\n")


def open_t(filename):
    with open(get_path("/t_models/"+filename),"r") as file:
        first_line = file.readline()
        t = defaultdict(lambda: float(first_line))
        for line in file.readlines():
            line = line.strip("\n")
            k,v = line.split(" q:q ")
            t[tuple(k.split("qq"))] = float(v)
    return t

if __name__ == "__main__":
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]

    t_e_given_f = train(sentance_pairs, 100, False)
    reversed = [(e,f) for f,e in sentance_pairs]
    t_f_given_e = train(reversed, 100, False)
    alignments = [get_phrase_alignment(t_e_given_f, t_f_given_e, es, ps, null_flag=False) for es, ps in sentance_pairs]
    print("ALIGN",alignments)
    phrase_probs = ibm_models.get_phrase_probabilities(alignments, sentance_pairs)

    # print("qq",alignments)

    log_phrase_table = ibm_models.get_log_phrase_table(phrase_probs)
# confident that this is right but that having NULL in small corpora doesnt work:
# since both casa and null tokens in every sentance so indistiguishable as far as the model is concerned
    print()
    ibm_models.print_phrase_table(phrase_probs)
    print()
    ibm_models.print_phrase_table(log_phrase_table)
    fs = "c a b".split(" ")
    es = "x y".split(" ")
    print(ibm_models.get_phrases([(1, 1)], fs, es))

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
    calculated = ibm_models.get_phrase_alignment_by_symmetry(f_given_e_pairing, e_given_f_rev)
    print(5, answer == calculated)

    # get_phrases()
    # again the this is the "Mary did not slap the green witch example"
    fs = "Maria no dio ́una bofetada a la bruja verde".split(" ")
    es = "Mary did not slap the green witch".split(" ")
    phrase_alignment = {(1, 2), (6, 4), (0, 0), (3, 3), (7, 6), (2, 3), (4, 3), (8, 5), (1, 1)}
    answer = {('verde', 'green'), ('dio ́una bofetada', 'slap'), ('no dio ́una bofetada', 'did not slap'), ('bruja', 'witch'), ('no dio ́una bofetada a la bruja verde', 'did not slap the green witch'), ('Maria', 'Mary'), ('dio ́una bofetada a la', 'slap the'), ('la', 'the'), ('Maria no dio ́una bofetada a la bruja verde', 'Mary did not slap the green witch'), ('no dio ́una bofetada a la', 'did not slap the'), ('bruja verde', 'green witch'), ('Maria no dio ́una bofetada', 'Mary did not slap'), ('no', 'did not'), ('a la', 'the'), ('no dio ́una bofetada a', 'did not slap'), ('dio ́una bofetada a', 'slap'), ('dio ́una bofetada a la bruja verde', 'slap the green witch'), ('Maria no dio ́una bofetada a', 'Mary did not slap'), ('a la bruja verde', 'the green witch'), ('Maria no dio ́una bofetada a la', 'Mary did not slap the'), ('Maria no', 'Mary did not'), ('la bruja verde', 'the green witch')}
    calculated = ibm_models.get_phrases(phrase_alignment, fs, es)
    print(6, calculated == answer)

    # get_phrase_probabilities()
    alignments = [[(0, 1), (0, 0)], [(0, 1), (2, 0), (1, 0)], [(0, 0)]]
    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]
    calculated = ibm_models.get_phrase_probabilities(alignments, sentance_pairs)
    check_list = [(('la','the big house'), 0.5), (('la','the big'),0.5),
                  (('la casa', 'the big'), 0.5), (('la casa', 'the big house'), 0.5),
                  (('pez verde', 'green'), 1.0), (('casa pez verde', 'green house'), 1.0),
                  (('casa', 'house'), 0.5), (('casa', 'shop'), 0.5)]
    print(calculated)
    print(7,all([calculated[alignment[0]][alignment[1]] == prob for alignment,prob in check_list]))
