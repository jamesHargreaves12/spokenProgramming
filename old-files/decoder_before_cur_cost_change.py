import math
from heapq import heappop,heappush,heappushpop
import ibmmodel1
from faster_lang_model import LanguageModel
from collections import defaultdict
import time
from math import log,inf


def log_d(start_i,last_end_i):
    # alpha^|start_i-last_end_i-1|
    alpha = 0.7
    log_alpha = log(alpha)
    return abs(start_i-last_end_i-1)*log(alpha)

def log_cur_cost(current_hyp, source, log_phrase_probs, lang_model: LanguageModel):
    translated_phrases = [x for _,_,x in current_hyp]
    translated_tokens = []
    for phrase in translated_phrases:
        translated_tokens.extend(phrase.split(" "))
    log_lang_model_probs = lang_model.get_log_prob_sentance(translated_tokens,padded_left=True,padded_right=False)

    # log(1) = 0
    log_translation_prob = 0
    log_distortion_prob = 0
    last_end_f = -1
    for cur_phrase in current_hyp:
        start_f,end_f,e = cur_phrase
        foreign_phrase = " ".join(source[start_f:end_f+1])
        log_translation_prob += log_phrase_probs[foreign_phrase][e]
        if last_end_f != -1:
            log_distortion_prob += log_d(start_f,last_end_f)
        last_end_f = end_f
    # print(log_translation_prob)
    # print(log_distortion_prob)
    # print(log_lang_model_probs)
    print(log_lang_model_probs)
    return log_lang_model_probs+log_distortion_prob+log_translation_prob


# need to be careful to wipe this between goes
future_estimate_cache = {}
def wipe_future_estimate_cache():
    global future_estimate_cache
    future_estimate_cache = {}


def get_cache_entry(key):
    global future_estimate_cache
    if key in future_estimate_cache:
        return future_estimate_cache[key]
    return None

def add_to_cache(key, value):
    global future_estimate_cache
    future_estimate_cache[key] = value

def get_max_log_prob_estimate(sequence_of_words,phrase_to_max_log_prob):
    # initially this will just be the phrase_table eventually I would like this to be phrase_table with a language model applied to it in a preprocessing step
    # would be nice to have just phrase to probability mapping
    # http://www.statmt.org/book/slides/06-decoding.pdf computing table from here
    cache_key = " ".join(sequence_of_words)
    cache_entry = get_cache_entry(cache_key)
    if cache_entry or cache_entry == 0:
        return cache_entry

    N = len(sequence_of_words)
    log_table = [[0 for _ in range(N - i)] for i in range(N)]
    for n in range(N):
        for first_pos in range(N-n):
            phrase = " ".join(sequence_of_words[first_pos:first_pos+n+1])
            if phrase in phrase_to_max_log_prob:
                max_prob = phrase_to_max_log_prob[phrase]
            else:
                max_prob = -inf
            for size_end in range(0,n):
                table_score = log_table[n-1-size_end][first_pos]+log_table[size_end][first_pos+n-size_end]
                # more efficient than the max function
                max_prob = max_prob if max_prob > table_score else table_score
            log_table[n][first_pos] = max_prob
    estimate = log_table[N-1][0]
    # if estimate == -inf:
    #     for line in log_table:
    #         print_str = ""
    #         for cell in line:
    #             if cell == -inf:
    #                 print_str += "- "
    #             else:
    #                 print_str += ". "
    #         print(print_str)
    add_to_cache(cache_key,estimate)
    return estimate


def log_future_cost(translated_phrases, source:list, phrase_to_max_log_prob):
    ticked = [0 for _ in source]
    for e_start,e_end,_ in translated_phrases:
        ticked[e_start:e_end+1] = [1]*(e_end-e_start+1)
    phrases = []
    cur_start = 0
    for i in range(len(ticked)):
        if ticked[i] == 1:
            if cur_start != i:
                phrases.append((cur_start,i-1))
            cur_start = i+1
    if cur_start != len(ticked):
        phrases.append((cur_start,len(ticked)-1))
    log_future_prob = 0
    for start,end in phrases:
        log_prob = get_max_log_prob_estimate(source[start:end+1],phrase_to_max_log_prob)
        log_future_prob += log_prob
    return log_future_prob


def get_new_hyps(translated_phrases,log_phrase_table,source):
    # might be an idea to precomute the possible phrases
    new_hyps = []
    ticked = [0 for _ in source]
    for e_start,e_end,_ in translated_phrases:
        ticked[e_start:e_end+1] = [1]*(e_end-e_start+1)
    unused_sections = []
    cur_start = 0
    for i in range(len(ticked)):
        if ticked[i] == 1:
            if cur_start != i:
                unused_sections.append((cur_start,i-1))
            cur_start = i+1
    if cur_start != len(ticked):
        unused_sections.append((cur_start,len(ticked)-1))

    for start_sec,end_sec in unused_sections:
        for start_phrase in range(start_sec,end_sec+1):
            for end_phrase in range(start_phrase,end_sec+1):
                phrase = " ".join(source[start_phrase:end_phrase+1])
                if phrase in log_phrase_table:
                    for translation in log_phrase_table[phrase].keys():
                        new_hyp = translated_phrases.copy()
                        new_hyp.append((start_phrase,end_phrase,translation))
                        new_hyps.append((new_hyp,sum(ticked)+end_phrase-start_phrase+1))
    return new_hyps

def get_phrase_to_max_prob(phrase_table):
    phrase_to_max_prob = {}
    for phrase in phrase_table:
        max_translation = max(phrase_table[phrase], key=lambda key: phrase_table[phrase][key])
        phrase_to_max_prob[phrase] = phrase_table[phrase][max_translation]
    return phrase_to_max_prob

def prune_stack(stack):
    # this is a very bad prune method since it will not remove the worest hypotesis
    if len(stack) > 1000:
        stack.pop()

def add_to_hypothesis_stack(stack,item):
    cost = item
    if len(stack) >= 1000:
        if cost <= stack[0]:
            # this item is worse than all the items on the stack so do nothing
            return
        else:
            # add the item to the stack and then pop the worst
            heappushpop(stack,item)
    else:
        heappush(stack,item)



def beam_search_stack_decoder(source,lang_model,log_phrase_table):
    # using pseudocode on page 908 of J&M 2 edition
    # (items of form (-cost,translations)
    wipe_future_estimate_cache()
    phrase_to_max_log_prob = get_phrase_to_max_prob(log_phrase_table)

    initial_value = (log_future_cost([],source,phrase_to_max_log_prob),[])
    hypothesis_stacks = [[] for _ in range(1+len(source))]
    heappush(hypothesis_stacks[0],initial_value)
    for i,stack in enumerate(hypothesis_stacks):
        if i == len(source):
            break
        # print()
        if i != 0 and __name__ != "__main__":
            print(time.time()-start)
            print('******************')
            print(i)
        start = time.time()
        while stack:
            current_hyp = heappop(stack)
            # print("Considering: " + str(current_hyp))
            for new_hyp,covered_count in get_new_hyps(current_hyp[1],log_phrase_table,source):
                log_cur_cost_hyp = log_cur_cost(new_hyp,source,log_phrase_table,lang_model)
                log_fut_cost_hyp = log_future_cost(new_hyp,source,phrase_to_max_log_prob)
                cost = log_cur_cost_hyp+log_fut_cost_hyp
                add_to_hypothesis_stack(hypothesis_stacks[covered_count],(cost,new_hyp))
                # heappush(hypothesis_stacks[covered_count],(cost,new_hyp))
                # prune_stack(hypothesis_stacks[covered_count])
    best_hyp = max(hypothesis_stacks[len(source)])
    return best_hyp[1]


if __name__ == "__main__":

    def print_or_value(id, calculated, value):
        if type(value) == float and round(value,5) == round(calculated,5) or \
            type(value) != float and value == calculated:
            print(True)
            # print()
        else:
            print(id,calculated,value)
            print()

    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]
    t_f_given_e = ibmmodel1.train(sentance_pairs, 100)
    reversed = [(x,y) for y,x in sentance_pairs]
    t_e_given_f = ibmmodel1.train(reversed, 100)
    alignments = [ibmmodel1.get_phrase_alignment(t_f_given_e, t_e_given_f, fs, es) for fs, es in sentance_pairs]

    phrase_table = ibmmodel1.get_phrase_probabilities(alignments,sentance_pairs)
    log_phrase_table = ibmmodel1.get_log_phrase_table(phrase_table)
    lang_model = LanguageModel([e for _,e in sentance_pairs], n=2)
    # ibmmodel1.print_phrase_table(log_phrase_table)


    # Tests:
    print()
    print("Tests: ")
    print()
    foreign_sentence = "la casa".split(" ")
    # ignore the issue to short message - minor bug will fix later
    print_or_value(1, log_cur_cost([], foreign_sentence, log_phrase_table, lang_model), log(1))
    print_or_value(2, log_cur_cost([(0,0,"the big")], foreign_sentence, log_phrase_table, lang_model), log(0.041666666666666664))
    print_or_value(3, log_cur_cost([(1,1,"shop")], foreign_sentence, log_phrase_table, lang_model), log(0.125))
    print_or_value(4, log_cur_cost([(0,0,"the big house")], foreign_sentence, log_phrase_table, lang_model), log(0.013888888888888888))
    print_or_value(5, log_cur_cost([(0,0,"the big"),(1,1,"shop")], foreign_sentence, log_phrase_table, lang_model), log(0.003472222222222222))
    #
    print()
    phrase_to_max_log_prob = get_phrase_to_max_prob(log_phrase_table)
    print_or_value(6, log_future_cost([], foreign_sentence, phrase_to_max_log_prob), log(0.5))
    print_or_value(7, log_future_cost([(0,0,"the big")], foreign_sentence, phrase_to_max_log_prob), log(0.5))
    print_or_value(8, log_future_cost([(1,1,"shop")], foreign_sentence, phrase_to_max_log_prob), log(0.5))
    print_or_value(9, log_future_cost([(0,0,"the big house")], foreign_sentence, phrase_to_max_log_prob), log(0.5))
    print_or_value(10, log_future_cost([(0,0,"the big"),(1,1,"shop")], foreign_sentence, phrase_to_max_log_prob), log(1))
    print()
    print_or_value(11, beam_search_stack_decoder(["la","casa"],lang_model, log_phrase_table), [(0, 1, 'the big')])
    print_or_value(12, beam_search_stack_decoder(["la"],lang_model, log_phrase_table), [(0, 0, 'the big')])
