import collections
import math
import random

from data_prep_tools import get_data

RANDOM_SHUFFLE_ORDER = [126, 123, 68, 80, 2, 120, 72, 37, 29, 97, 58, 76, 63, 33, 114, 86, 0, 51, 12, 71, 83, 129, 49, 53, 16, 9, 31, 15, 105, 101, 85, 57, 98, 113, 24, 103, 46, 1, 69, 18, 93, 110, 52, 115, 7, 54, 4, 39, 19, 132, 32, 128, 35, 66, 34, 89, 36, 131, 48, 75, 116, 65, 90, 82, 11, 102, 112, 96, 40, 79, 117, 26, 95, 23, 20, 127, 41, 99, 73, 42, 122, 67, 22, 28, 43, 62, 92, 14, 8, 59, 104, 119, 106, 130, 64, 118, 50, 38, 78, 125, 100, 81, 109, 5, 25, 45, 27, 47, 91, 87, 21, 61, 88, 60, 111, 74, 3, 30, 17, 6, 108, 55, 10, 70, 77, 107, 44, 94, 56, 121, 84, 124, 13] + [i for i in range(133,147) ]

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

def get_folds(num_folds,method="RAN",with_shuffle = True):
    transcripts,pseudocode = _get_all_files()
    all_data = [x for x in zip(transcripts,pseudocode)]
    if with_shuffle:
        all_data_shuffled = []
        for i in RANDOM_SHUFFLE_ORDER:
            all_data_shuffled.append(all_data[i])
        all_data = all_data_shuffled

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
    print(get_folds(10,"SEQ",with_shuffle=True)[-1] == get_folds(10,"SEQ",with_shuffle=False)[-1])
    print(len(get_folds(10,"SEQ",with_shuffle=True)) == len(get_folds(10,"SEQ",with_shuffle=False)))
    for x,y in zip(get_folds(10,"SEQ",True),get_folds(10,"SEQ",False)):
        print(len(x) == len(y))
