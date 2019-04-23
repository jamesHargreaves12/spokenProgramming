from termcolor import colored
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()


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
            or tok in ["output","false","true","NUMBER","if","else","while","STRING_CONST"]


def get_certain_tokens_range(transcript,start,end):
    certain_tokens_before = []
    for i in range(end-start):
        tok = transcript[start+i]
        if does_map_pseud_direct(tok):
            certain_tokens_before.append(tok)
        elif stemmer.stem(tok) in ["return"]:
            certain_tokens_before.append("output")
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


def get_splits_from_location(trans, pseud, start_split, group_length, index_include_flag=False):
    orig_trans = trans
    orig_pseud = pseud
    if index_include_flag:
        trans = [x for x,_ in trans]
        pseud = [x for x,_ in pseud]

    while start_split + group_length + 1 < len(trans) and \
            trans[start_split + group_length + 1] in also_removed_following_toks:
        group_length += 1
    if start_split + group_length + 1 == len(trans):
        return [(orig_trans[:start_split], orig_pseud)]
    else:
        try:
            pseud_loc = get_pseud_split_loc_2(trans, pseud, start_split, start_split + group_length)
            result = [(orig_trans[:start_split], orig_pseud[:pseud_loc + 1])]
            if len(pseud) > pseud_loc + 1:
                if trans[start_split] != "set":
                    result.append((orig_trans[start_split + group_length + 1:], orig_pseud[pseud_loc + 1:]))
                else:
                    result.append((orig_trans[start_split:], orig_pseud[pseud_loc + 1:]))
            return result
        except:
            if trans[start_split] != "set":
                return [(orig_trans[:start_split] + orig_trans[start_split + group_length + 1:], orig_pseud)]
            else:
                return [(orig_trans, orig_pseud)]


def splits_on_end_toks(splits,index_included_flag=False):
    next_splits = splits
    changed = True
    while changed:
        changed = False
        splits = next_splits
        next_splits = []
        for splits_index in range(len(splits)):
            trans,pseud = splits[splits_index]
            if index_included_flag:
                trans = [x for x,_ in trans]
                pseud = [x for x,_ in pseud]

            end_index = get_last_index("end",trans)
            if end_index == -1:
                next_splits.append(splits[splits_index])
            else:
                group_length = 0
                for i in range(1,4):
                    if end_index+i < len(trans) and \
                            trans[end_index+i] in block_keywords:
                        group_length = i
                        break

                if group_length > 0:
                    changed = True
                    split_pair = get_splits_from_location(splits[splits_index][0], splits[splits_index][1], end_index, group_length,index_included_flag)
                    next_splits.extend(split_pair)
                else:
                    next_splits.append(splits[splits_index])
    return next_splits


def get_potential_splits(trans):
    indecies= []
    len_trans = len(trans)
    for i, word in enumerate(trans):
        if word in split_tokens:
            indecies.append(i)
        elif word == "set" and len_trans>i+1 and \
                (trans[i+1] in ["a","the"] or trans[i+1].startswith("VARIABLE")):
            indecies.append(i)
    return indecies


def split_files_further(splits, index_included_flag=False):
    next_splits = splits
    changed = True
    while changed:
        changed = False
        splits = next_splits
        next_splits = []
        for trans,pseud in splits:
            orig_trans = trans
            orig_pseud = pseud
            if index_included_flag:
                trans = [x for x,_ in trans]
            # print()
            split_hyps = get_potential_splits(trans)
            if len(split_hyps) > 0:
                havent_added = True
                for split_start in split_hyps:
                    group_length = 0
                    split_pairs = get_splits_from_location(orig_trans, orig_pseud, split_start, group_length, index_included_flag)
                    if len(split_pairs[0][0]) != len(orig_trans):
                        changed = True
                        havent_added = False
                        next_splits.extend(split_pairs)
                        break
                if havent_added:
                    next_splits.append((orig_trans,orig_pseud))
            else:
                next_splits.append((orig_trans,orig_pseud))

    return next_splits


def stem_all_words(data,index_included_flag=False):

    stemmed_data = []
    for trans,pseud in data:
        if index_included_flag:
            should_stem = lambda tok:tok[0].islower() and tok not in non_stem
            stemmed_trans = [(stemmer.stem(tok),index) if should_stem(tok) else (tok,index) for tok,index in trans]
            stemmed_data.append((stemmed_trans,pseud))
        else:
            should_stem = lambda tok:tok[0].islower() and tok not in non_stem
            stemmed_trans = [stemmer.stem(tok) if should_stem(tok) else tok for tok in trans]
            stemmed_data.append((stemmed_trans,pseud))
    return stemmed_data


def remove_dead_tokens(data,index_included_flag=False):
    result = []
    for trans,pseud in data:
        if index_included_flag:
            trans = [x for x in trans if x[0] not in dead_tokens]
        else:
            trans = [x for x in trans if x not in dead_tokens]
        result.append((trans,pseud))
    return result


