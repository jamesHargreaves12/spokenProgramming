import collections
import math
import random

from data_prep_tools import get_data

def tokenize(long_string):
    stripped = long_string.strip('\n')
    return [x for x in stripped.split(" ") if x != ""]

def _get_all_files():
    base_dir1 = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"
    base_dir2 = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData_2/"

    transcripts_1 = get_data.get_data_from_directory("/transcripts_var_replaced/",base_dir1)
    pseudocode_1 = get_data.get_data_from_directory("/pseudocode_simplified/",base_dir1)
    print("Project Data part 1/2 loaded")
    transcripts_2 = get_data.get_data_from_directory("/transcripts_var_replaced/",base_dir2)
    pseudocode_2 = get_data.get_data_from_directory("/pseudocode_simplified/",base_dir2)
    print("Project Data part 2/2 loaded")
    transcripts = transcripts_1 + transcripts_2
    pseudocodes = pseudocode_1 + pseudocode_2
    tokenized_transcripts = [tokenize(trans) for trans in transcripts]
    tokenized_pseudocodes = [tokenize(pseud) for pseud in pseudocodes]
    return tokenized_transcripts, tokenized_pseudocodes


def _get_folds_rr(long_list, num_chunks):
    chunks = [[] for _ in range(num_chunks)]
    current_chunk = 0
    for item in long_list:
        chunks[current_chunk].append(item)
        current_chunk = (current_chunk + 1) % num_chunks
    return chunks


def _get_folds_sequential(long_list,num_chunks):
    length_chunk = int(math.ceil(len(long_list) / num_chunks))
    if num_chunks > 1:
        rest = _get_folds_sequential(long_list[length_chunk:],num_chunks-1)
    else:
        rest = []
    return [long_list[0:length_chunk]] + rest


def _get_folds_random(long_list,num_chunks):
    random.shuffle(long_list)
    return _get_folds_sequential(long_list,num_chunks)

def get_folds(num_folds,method="RAN"):
    transcripts,pseudocode = _get_all_files()
    all_data = [x for x in zip(transcripts,pseudocode)]
    if method == "RAN":
        return _get_folds_random(all_data,num_folds)
    elif method == "SEQ":
        return _get_folds_sequential(all_data,num_folds)
    else:
        return _get_folds_rr(all_data,num_folds)

if __name__ == "__main__":
    print(sum([len(x) for x in get_folds(5)]))
    print(sum([len(x) for x in get_folds(5,"SEQ")]))
    print(sum([len(x) for x in get_folds(5,"RR")]))
