from data_prep_tools import get_data
from collections import defaultdict
from itertools import permutations

def get_n_grams(unigrams,n):
    n_grams = []
    for i in range(len(unigrams)-n+1):
        n_grams.append(unigrams[i:i+n])
    return n_grams

def get_unigrams_from_text(text):
    unigrams = ["START"]
    unigrams.extend([x for x in text if x != ''])
    unigrams.append("END")
    return unigrams

def get_pseudocode_n_gram_counts(n):
    counts = defaultdict(int)
    pseudocode_data = get_data.get_data_from_directory("/pseudocode_simplified/")
    for pseudocode in pseudocode_data:
        unigrams = get_unigrams_from_text(pseudocode.split(" "))
        n_grams = get_n_grams(unigrams,n)
        for gram in n_grams:
            counts[tuple(gram)] += 1
    return counts

def get_most_likely_ordering(transcript, n, threshold):
    n_gram_counts = get_pseudocode_n_gram_counts(n)
    unigrams = get_unigrams_from_text(transcript)
    for i in range(len(unigrams)-n+1):
        gram = tuple(unigrams[i:i+n])
        gram_count = n_gram_counts[gram]
        best_perm = gram
        max_perm_count = gram_count
        for perm in permutations(gram):
            perm_count = n_gram_counts[perm]
            if perm_count > max_perm_count:
                max_perm_count = perm_count
                best_perm = perm
        if max_perm_count - gram_count > threshold:
            for j in range(n):
                unigrams[i+j]=best_perm[j]
    return " ".join(unigrams[1:-1])


if __name__ == "__main__":
    n_gram_counts = get_pseudocode_n_gram_counts(4)
    ordered_counts = sorted(n_gram_counts.items(), key=lambda x: x[1], reverse=True)
    print(ordered_counts[0:10])
