import collections
import math
import random

from data_prep_tools import get_data


def _get_all_files():
    base_dir1 = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"
    base_dir2 = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData_2/"

    transcripts_1 = get_data.get_data_from_directory("/transcripts_var_replaced/",base_dir1)
    pseudocode_1 = get_data.get_data_from_directory("/pseudocode_simplified/",base_dir1)
    print("Project Data part 1/2 loaded")
    transcripts_2 = get_data.get_data_from_directory("/transcripts_var_replaced/",base_dir2)
    pseudocode_2 = get_data.get_data_from_directory("/pseudocode_simplified/",base_dir2)
    print("Project Data part 2/2 loaded")

    return transcripts_1 + transcripts_2, pseudocode_1 + pseudocode_2


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


def _get_folds_random(long_list_1,long_list_2,num_chunks):
    assert(len(long_list_1) == len(long_list_2))
    indices = [x for x in range(len(long_list_1))]
    random.shuffle(indices)
    indices_per_fold = _get_folds_sequential(indices,num_chunks)
    list1_folds = [[long_list_1[i] for i in indxs] for indxs in indices_per_fold]
    list2_folds = [[long_list_2[i] for i in indxs] for indxs in indices_per_fold]
    return list1_folds,list2_folds


def get_folds(num_folds,method="RAN"):
    transcripts,pseudocode = _get_all_files()
    if method == "RAN":
        return _get_folds_random(transcripts,pseudocode,num_folds)
    elif method == "SEQ":
        return _get_folds_sequential(transcripts,num_folds),\
               _get_folds_sequential(pseudocode,num_folds)
    else:
        return _get_folds_rr(transcripts,num_folds),\
               _get_folds_rr(pseudocode,num_folds)
