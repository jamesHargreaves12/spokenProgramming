import re

from termcolor import colored

from get_data import train_test_data, validation_set, split_data, new_exp_keywords, remove_start_tokens, \
    train_test_split
from other.log_module import write_to_log
from smt import smt_functions, get_alpha_value
from test1 import total_edit_distance_smt_enhanced, total_edit_distance_smt
from tools.find_resource_in_project import get_path
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

n=2
epoch = 100
null_flag = True
fm_flag = True
block_keywords = ["while","for","if","else","loop","block","function"]
also_removed_following_toks = ["statement","loop","and","then","next","block","there","the","you","so"]
split_tokens = ["then","next","start","let","and"]
dead_tokens = ["call","where","inclusive","start","the","this","so","by","variable","next","then","a","do","that"]
non_stem = ["else","false","true"]

def print_split_coloured(split,start,end):
    text = colored(" ".join(split[:start]),"blue")
    text += " " + colored(" ".join(split[start:end+1]),"red")
    text += " " + colored(" ".join(split[end+1:]),"blue")
    print(text)


def does_map_pseud_direct(tok:str):
    return tok.startswith("VARIABLE_") or tok.startswith("FUNCTION_CALL_") \
            or tok in ["return","false","true","NUMBER","if","else","while","STRING_CONST"]


def get_certain_tokens_range(transcript,start,end):
    certain_tokens_before = []
    for i in range(end-start):
        tok = transcript[start+i]
        if does_map_pseud_direct(tok):
            certain_tokens_before.append(tok)
        elif stemmer.stem(tok) in ["return"]:
            certain_tokens_before.append("return")
    return certain_tokens_before


def get_pseud_split_loc(trans, pseud, start_split, end_split):
    before_toks = get_certain_tokens_range(trans,0,start_split)
    after_toks = get_certain_tokens_range(trans,end_split+1,len(trans))
    # simple first test
    pseud_index = 0
    for tok in before_toks:
        while pseud_index < len(pseud) and \
                pseud[pseud_index] != tok:
            pseud_index += 1
    if pseud_index < len(pseud) and after_toks and \
           after_toks[0] == pseud[pseud_index+1]:
        return pseud_index
    else:
        raise Exception("Not split")


def bag_of_words_check(pseud,toks):
    # this is using a function not supposed for use but for now it works
    pseud_toks = get_certain_tokens_range(pseud,0,len(pseud))
    return sorted(pseud_toks) == sorted(toks)


def get_pseud_split_loc_2(trans, pseud, start_split, end_split):
    before_toks = get_certain_tokens_range(trans,0,start_split)
    after_toks = get_certain_tokens_range(trans,end_split+1,len(trans))
    last_before = before_toks[-1]
    hyps = [i for i,x in enumerate(pseud) if x == last_before]
    for hyp in hyps:
        if bag_of_words_check(pseud[:hyp+1],before_toks) or \
                bag_of_words_check(pseud[hyp+1:],after_toks):
            return hyp
    raise Exception("no location found")


def get_last_index(item,list_items):
    last_index = -1
    for i,x in enumerate(list_items):
        if x == item:
            last_index = i
    return last_index


def get_splits(trans,pseud,start_split,group_length):
    while start_split + group_length + 1 < len(trans) and \
            trans[start_split + group_length + 1] in also_removed_following_toks:
        group_length += 1
    if start_split + group_length + 1 == len(trans):
        return [(trans[:start_split], pseud)]
    else:
        try:
            pseud_loc = get_pseud_split_loc_2(trans, pseud, start_split, start_split + group_length)
            result = [(trans[:start_split], pseud[:pseud_loc + 1])]
            if len(pseud) > pseud_loc + 1:
                result.append((trans[start_split + group_length + 1:], pseud[pseud_loc + 1:]))
            # print_split_coloured(trans,start_split,start_split+group_length)
            # print(" ".join(pseud[:pseud_loc+1]))
            # print(" ".join(pseud[pseud_loc+1:]))
            # print()
            return result
        except:
            return [(trans[:start_split] + trans[start_split + group_length + 1:], pseud)]
            # print_split_coloured(trans,end_index,end_index+group_length)
            # print(" ".join(pseud))
            # print()


def splits_on_end_toks(splits):
    next_splits = splits
    changed = True
    while changed:
        changed = False
        splits = next_splits
        next_splits = []
        for trans,pseud in splits:
            end_index = get_last_index("end",trans)
            if end_index == -1:
                next_splits.append((trans,pseud))
            else:
                group_length = 0
                for i in range(1,4):
                    if end_index+i < len(trans) and \
                            trans[end_index+i] in block_keywords:
                        group_length = i
                        break

                if group_length > 0:
                    changed = True
                    split_pair = get_splits(trans,pseud,end_index,group_length)
                    next_splits.extend(split_pair)
    return next_splits


def get_potential_splits(trans):
    indecies= []
    for i, word in enumerate(trans):
        if word in split_tokens:
            indecies.append(i)
    return indecies


def split_files_further(splits):
    next_splits = splits
    changed = True
    while changed:
        changed = False
        splits = next_splits
        next_splits = []
        for trans,pseud in splits:
            split_hyps = get_potential_splits(trans)
            if len(split_hyps) > 0:
                for split_start in split_hyps:
                    group_length = 0
                    changed = True
                    split_pair = get_splits(trans, pseud, split_start, group_length)
                    next_splits.extend(split_pair)
                    break
            else:
                next_splits.append((trans,pseud))

    return next_splits


def stem_all_words(data):
    stemmed_data = []
    for trans,pseud in data:
        should_stem = lambda tok:tok[0].islower() and tok not in non_stem
        stemmed_trans = [stemmer.stem(tok) if should_stem(tok) else tok for tok in trans]
        stemmed_data.append((stemmed_trans,pseud))
    return stemmed_data


def remove_dead_tokens(data):
    result = []
    for trans,pseud in data:
        trans = [x for x in trans if x not in dead_tokens]
        result.append((trans,pseud))
    return result


def smt_enhanced_preprocessing(data,miss_which=-1):
    splits = data
    splits = split_data(splits)
    if miss_which != 1:
        splits = splits_on_end_toks(splits)
    if miss_which != 2:
        splits = stem_all_words(splits)
    if miss_which != 4:
        splits = split_files_further(splits)
    if miss_which != 3:
        splits = remove_dead_tokens(splits)
    return split_data(splits)


def validate_ibmmodel2(miss_index,omega_range):
    print("Validate ibmmodel2")
    preprocessed_train = smt_enhanced_preprocessing(train_test_data,miss_index)
    preprocessed_valid = smt_enhanced_preprocessing(validation_set,miss_index)
    lang_model = smt_functions.get_language_model(preprocessed_train,n)
    alignments = smt_functions.get_alignment_2(preprocessed_train,epoch,null_flag)
    log_phrase_table = smt_functions.get_log_phrase_table2(preprocessed_train,alignments)
    alpha = get_alpha_value.get_alpha(alignments)
    results = []
    for omega in omega_range:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        ted = total_edit_distance_smt(preprocessed_valid, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}\n".format(ted))
        results.append((omega,ted))
    return results


def get_edit_dists_omega(filename):
    edit_dists = []
    omega = -1
    ed_re = re.compile(r"Edit distance = (\d+)\n")
    o_re = re.compile(r"omega ([0-9.]+)\n")
    omega_preds = []
    with open(get_path(filename), "r") as file:
        for line in file.readlines():
            if ed_re.match(line):
                ed = int(ed_re.match(line).group(1))
                edit_dists.append((omega,ed))
            elif o_re.match(line):
                omega = float(o_re.match(line).group(1))
    return edit_dists


def get_ted_for_fold_v2():
    print("GET TED v2 test")
    results = []
    for test,train in train_test_split:
        split_test = smt_enhanced_preprocessing(test)
        split_train = smt_enhanced_preprocessing(train)
        n = 2
        epoch = 100
        null_flag = True
        alignments = smt_functions.get_alignment_2(split_train, epoch, null_flag)
        log_phrase_table = smt_functions.get_log_phrase_table2(split_train, alignments)
        lang_model = smt_functions.get_language_model(split_train, n)
        alpha = get_alpha_value.get_alpha(alignments)
        omega = 3.5
        ted = total_edit_distance_smt(split_test, alpha, omega, lang_model, log_phrase_table)
        print(ted)
        write_to_log("Edit distance = {}\n".format(ted))
        results.append(ted)
    return results

if __name__ == "__main__":
    message = "test enhanced v2 new\n"
    print(message)
    write_to_log(message)

    print(get_ted_for_fold_v2())


    # print(get_alpha_v1())
    # 0.5059993143640726
    # print(get_alpha_v2())
    # 0.5870109847754866
    # print(validate_ibmmodel1())
    # results = []
    # So omega = 2.6
    # print(validate_ibmmodel2())
    # results = [(0.5,579),(0.8,567),(0.9,567),(1.0,566),(1.1,565),(1.2,565),(1.3,563),(1.4,562),(1.5,556),(1.6,559),(1.7,559)(2.0,560),(2.5,566)
    # So omega = 1.5

    # print(get_alpha_v2())
    # 0.5638317246403205

    # message = "with extended dead logs\n"
    # miss_index = -1
    all_preprocess = [(0.5, 441), (1.0, 442), (1.5, 439), (2.0, 440), (2.5, 431)]
    # message = "with no end token split\n"
    # miss_index = 1
    without_end = [(0.5, 541), (1.0, 536), (1.5, 531), (2.0, 530), (2.5, 524)]
    # message = "with no stem"
    # miss_index = 2
    without_stem = [(0.5, 456), (1.0, 444), (1.5, 445), (2.0, 440), (2.5, 444)]
    # message = "with no dead\n"
    # miss_index = 3
    no_dead = [(0.5, 471), (1.0, 465), (1.5, 465), (2.0, 463), (2.5, 460)]
    # message = "split on end\n"
    # miss_index = 4
    split_on_end = [(0.5, 427), (1.0, 426), (1.5, 416), (2.0, 416), (2.5, 410)] \
        + [(3.0, 411), (3.5, 411), (4.0, 407)]
    # message = "split on more\n"
    # miss_index = -1
    extra_splits = [(0.5, 415), (1.0, 412), (1.5, 407), (2.0, 411), (2.5, 406)] \
        + [(3.0, 405), (3.5, 402), (4.0, 406)] \
        + [(3.1, 405), (3.2, 405), (3.3, 405), (3.4, 402), (3.6, 402), (3.7, 402), (3.8, 403), (3.9, 404)]


    # print(message)
    # write_to_log(message)
    # validate_ibmmodel2(miss_index, [i/10 for i in range(31,40) if i != 35])

    # data = train_test_data
    # data = smt_enhanced_preprocessing(data,-1)
    # lengths = [len(trans) for trans,pseud in data]
    # for l in range(40):
    #     print(l,lengths.count(l))
    # for trans,pseud in data:
    #     if len(trans) > 20:
    #         print(" ".join(trans))
    #         print(" ".join(pseud))
    #         print()

    # print(get_edit_dists_omega("logs/extra_splits_omega.txt"))
    # print(get_edit_dists_omega("logs/extra_splits_omega_2.txt"))
    # print(get_edit_dists_omega("logs/extra_splits_omega_3.txt"))

