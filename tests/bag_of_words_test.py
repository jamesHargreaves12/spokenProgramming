from collections import defaultdict


def get_words_dict(tokens):
    words_dict = defaultdict(int)
    for tok in tokens:
        words_dict[tok] += 1
    return words_dict


def bag_of_words_test(source,target):
    source_bow = get_words_dict(source)
    target_bow = get_words_dict(target)
    keys = set.union(set(source_bow.keys()),set(target_bow.keys()))
    score = 0
    for k in keys:
        diff = abs(source_bow[k]-target_bow[k])
        score += diff
    return score
