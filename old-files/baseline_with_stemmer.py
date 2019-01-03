from baseline.get_pseudocode_token_list import get_pseudocode_tokens
from data_prep_tools import get_data
from termcolor import colored
from baseline import get_n_gram_reordering
from tools.minimum_edit_distance import minimum_edit_distance
import math
from other.matrix_to_image import show_heatmap
from nltk.stem import PorterStemmer

def print_coloured_changes(removed,mapped,orig_tokens):
    print_text = ""
    i = 0
    while i < len(orig_tokens):
        tok = orig_tokens[i]
        if len(removed) > 0 and tok == removed[0]:
            print_text += colored(tok + " ", "red")
            removed.pop(0)
            i += 1
        else:
            value = mapped.pop(0)
            i += len(value[0])
            original = " ".join(value[0])
            new = value[1]
            if original == new:
                print_text += colored(" ".join(value[0]) + " ", "blue")
            else:
                print_text += colored(" ".join(value[0]) + "(" + value[1] + ") ", "blue")
    print(print_text)


stemmer = PorterStemmer()

def is_first_token_equal_stem(transcript_words, token_identifier, start_index):
    global stemmer
    tok_words = token_identifier.split(" ")
    for i,tok in enumerate(tok_words):
        if start_index+i >= len(transcript_words) or ((stemmer.stem(tok) != stemmer.stem(transcript_words[start_index+i])) or (tok.isupper()!=transcript_words[start_index+i].isupper())):
            return False
    return True

def is_first_token_equal_no_stem(transcript_words, token_identifier, start_index):
    tok_words = token_identifier.split(" ")
    for i,tok in enumerate(tok_words):
        if start_index+i >= len(transcript_words) or (tok != transcript_words[start_index+i]):
            return False
    return True


def transcript_to_code_tokens(transcript, token_map):
    transcript_tokens = [x for x in transcript.split(" ") if not x == ""]
    orig_tokens = transcript_tokens[:]
    removed = []
    mapped = []
    result = []
    cur_index = 0
    while True:
        longest_tok = ""
        length_longest_tok = 0
        for tok in token_map.keys():
            if is_first_token_equal_no_stem(transcript_tokens, tok, cur_index):
                length_tok = len(tok.split(" "))
                if length_tok > length_longest_tok or length_tok == length_longest_tok and transcript_tokens[cur_index:cur_index+length_tok] == tok.split(" "):
                    length_longest_tok = length_tok
                    longest_tok = tok
        if length_longest_tok == 0:
            removed.append(transcript_tokens[cur_index])
            cur_index += 1
        else:
            mapped.append((transcript_tokens[cur_index:cur_index+length_longest_tok],token_map[longest_tok]))
            cur_index += length_longest_tok
            result.append(token_map[longest_tok])

        if len(transcript_tokens) == cur_index:
            print_coloured_changes(removed, mapped, orig_tokens)
            return [x for x in result if x != "NOT_A_TOKEN"]

def baseline():
    pseudocode_tokens = get_pseudocode_tokens()
    transcripts_simplified = get_data.get_data_from_directory("/transcripts_var_replaced/")
    truth = get_data.get_data_from_directory("/pseudocode_simplified/")

    best_score = math.inf
    scores = []
    for n in range(1,7):
        cur_scores = []
        for t in range(0, 15):
            with_reordering_distance = []
            for i in range(len(transcripts_simplified)):
                print()
                print(i)
                transcript = transcripts_simplified[i]
                only_posible_tokens = transcript_to_code_tokens(transcript.strip("\n"),pseudocode_tokens)
                pseudocode_attempt = get_n_gram_reordering.get_most_likely_ordering(only_posible_tokens, n, t)
                reordered = [x for x in pseudocode_attempt.split(" ") if not x == ""]
                actual = [x for x in truth[i].split(" ") if not x == ""]
                with_reordering_distance.append(minimum_edit_distance(reordered,actual))
            total_distance = sum(with_reordering_distance)
            print("n = " + str(n) + " t = "+ str(t) + " score ==     " + str(total_distance))
            print(with_reordering_distance)
            best_score = min(best_score,total_distance)
            cur_scores.append(total_distance)
        scores.append(cur_scores)
    print(best_score)

    show_heatmap(scores)

    # for small dataset 80 - does best when no reordering ie data set is clearly too small

baseline()