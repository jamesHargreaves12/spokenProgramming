from heapq import heappop,heappush,heappushpop

from smt import ibmmodel1
from langModel.faster_lang_model import LanguageModel
import time
from math import log,inf
alpha = 0.7
omega = 2
log_omega = log(omega)
log_alpha = log(alpha)
print_on = True


def set_alpha(value):
    global alpha,log_alpha
    alpha = value
    log_alpha = log(value)


def set_omega(value):
    global omega,log_omega
    omega = value
    log_omega = log(value)


def log_short_sentance_penalty(len_e):
    return len_e*log_omega


def log_d(start_i,last_end_i):
    # alpha^|start_i-last_end_i-1|
    return abs(start_i-last_end_i-1)*log_alpha


def log_cur_cost(cur_cost:float, new_hyp:tuple, targ_so_far:str, cur_end_f_word:int, source, log_phrase_probs, lang_model: LanguageModel):
    new_start_f,new_end_f,new_e = new_hyp
    # likely can replace this next line
    if targ_so_far == "":
        translated_tokens = []
    else:
        translated_tokens = targ_so_far.split(" ")

    new_tokens = new_e.split(" ")
    new_foreign_phrase = " ".join(source[new_start_f:new_end_f+1])
    delta_lang_model = lang_model.get_log_prob_next_phrase(translated_tokens, new_tokens)
    delta_translation = log_phrase_probs[new_foreign_phrase][new_e]
    delta_short_sentance = log_short_sentance_penalty(len(new_tokens))

    if cur_end_f_word == -1:
        delta_distortion = 0
    else:
        delta_distortion = log_d(new_start_f,cur_end_f_word)
    return cur_cost+delta_lang_model+delta_translation+delta_distortion+delta_short_sentance


# need to be careful to wipe this between new sentences
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
    add_to_cache(cache_key,estimate)
    return estimate


def get_unused_phrase_boundaries(translated_phrases,len_source):
    boundaries = [(0,len_source-1)]
    for e_start,e_end,_ in translated_phrases:
        remove_i = False
        for i,phrase in enumerate(boundaries):
            start_phrase,end_phrase = phrase
            if e_start <= end_phrase:
                if start_phrase <= e_start-1:
                    boundaries[i] = (start_phrase,e_start-1)
                else:
                    remove_i = True

                if e_end+1 <= end_phrase:
                    boundaries.insert(i+1,(e_end+1,end_phrase))
                break
        if remove_i:
            boundaries.pop(i)
    return boundaries


def log_future_cost(hyp_bounds, source:list, phrase_to_max_log_prob):
    log_future_prob = 0
    for start,end in hyp_bounds:
        log_prob = get_max_log_prob_estimate(source[start:end+1],phrase_to_max_log_prob)
        log_future_prob += log_prob
    return log_future_prob


def get_new_hyps(current_bounds,log_phrase_table,source,len_source):
    # might be an idea to pre-compute the possible phrases
    new_hyps = []
    used_word_count = len_source
    for start,end in current_bounds:
        used_word_count -= end-start+1

    for start_sec,end_sec in current_bounds:
        for start_phrase in range(start_sec,end_sec+1):
            for end_phrase in range(start_phrase,end_sec+1):
                phrase = " ".join(source[start_phrase:end_phrase+1])
                if phrase in log_phrase_table:
                    for translation in log_phrase_table[phrase].keys():
                        new_hyp = (start_phrase,end_phrase,translation)
                        new_hyps.append((new_hyp, used_word_count + end_phrase - start_phrase + 1))
                        # new_hyp = translated_phrases.copy()
                        # new_hyp.append((start_phrase,end_phrase,translation))
                        # new_hyps.append((new_hyp,used_word_count+end_phrase-start_phrase+1))
    return new_hyps


def get_phrase_to_max_prob(phrase_table):
    phrase_to_max_prob = {}
    for phrase in phrase_table:
        max_translation = max(phrase_table[phrase], key=lambda key: phrase_table[phrase][key])
        phrase_to_max_prob[phrase] = phrase_table[phrase][max_translation]
    return phrase_to_max_prob


def add_to_hypothesis_stack(stacks,item,thresh,i):
    cost = item
    stack = stacks[i]
    if len(stack) >= 1000:
        if cost <= stack[0]:
            # this item is worse than all the items on the stack so do nothing
            return
        else:
            # add the item to the stack and then pop the worst
            heappushpop(stack,item)
            thresh[i] = stack[0][0]
    else:
        heappush(stack,item)
        if len(stack) == 1000:
            thresh[i] = stack[0][0]


def remove_section_from_bounds(bounds,section):
    start_sec,end_sec = section
    remove_i = False
    for i, phrase in enumerate(bounds):
        start_phrase, end_phrase = phrase
        if start_sec <= end_phrase:
            if start_phrase <= start_sec - 1:
                bounds[i] = (start_phrase, start_sec - 1)
            else:
                remove_i = True

            if end_sec + 1 <= end_phrase:
                bounds.insert(i + 1, (end_sec + 1, end_phrase))
            break
    if remove_i:
        bounds.pop(i)
    return bounds


def beam_search_stack_decoder(source,lang_model,log_phrase_table,first_trans_tok=""):
    # using pseudocode on page 908 of J&M 2 edition
    # trans_info_so_far = phrase_boundaries, most recently translated end word, target translation so far
    # if cur_end_word = -1 then it is non existant (ie 0 word translated so far)
    # (items of form (cost,trans_info_so_far,cur_cost)
    wipe_future_estimate_cache()
    phrase_to_max_log_prob = get_phrase_to_max_prob(log_phrase_table)
    len_source = len(source)
    initial_bounds = [(0,len_source-1)]
    estimate_cost = log_future_cost(initial_bounds, source, phrase_to_max_log_prob)
    initial_value = (estimate_cost,(initial_bounds,-1,first_trans_tok),0)
    hypothesis_stacks = [[] for _ in range(1+len_source)]
    thresh = [-inf for _ in range(1+len_source)]
    heappush(hypothesis_stacks[0],initial_value)
    for i,stack in enumerate(hypothesis_stacks):
        if stack:
            best_hype_so_far = stack[0]
        score_of_best = -inf
        print("{} / {} \n".format(i,len_source))
        if i == len_source:
            break
        if i != 0 and __name__ != "__main__" and print_on:
            print(time.time()-start)
            print('******************',i)
        start = time.time()
        while stack:
            current_hyp = heappop(stack)
            cur_cost_current:float = current_hyp[2]
            current_trans_info = current_hyp[1]
            current_bounds = current_trans_info[0]
            targ_so_far = current_trans_info[2]
            cur_end_f_word = current_trans_info[1]
            if cur_cost_current > score_of_best:
                score_of_best = cur_cost_current
                best_hype_so_far = current_hyp

            for new_hyp,covered_count in get_new_hyps(current_bounds,log_phrase_table,source,len_source):
                hyp_start,hyp_end,hyp_trans = new_hyp
                hyp_bounds = remove_section_from_bounds(current_bounds.copy(),(hyp_start,hyp_end))
                log_fut_cost_hyp:float = log_future_cost(hyp_bounds,source,phrase_to_max_log_prob)
                if log_fut_cost_hyp + cur_cost_current < thresh[covered_count]:
                    continue

                log_cur_cost_hyp = log_cur_cost(cur_cost_current,new_hyp,targ_so_far,cur_end_f_word,source,log_phrase_table,lang_model)
                cost = log_cur_cost_hyp+log_fut_cost_hyp

                if targ_so_far:
                    new_trans = targ_so_far+" " +hyp_trans
                else:
                    new_trans = hyp_trans
                new_hyp_item = hyp_bounds,new_hyp[1],new_trans

                add_to_hypothesis_stack(hypothesis_stacks,(cost,new_hyp_item,log_cur_cost_hyp),thresh,covered_count)
    if hypothesis_stacks[len_source]:
        best_hyp = max(hypothesis_stacks[len_source])
    else:
        best_hyp = best_hype_so_far
    return best_hyp[1][2]


def beam_search_stack_decoder_with_back_track(source,lang_model,log_phrase_table):
    # using pseudocode on page 908 of J&M 2 edition
    # trans_info_so_far = phrase_boundaries, most recently translated end word, target translation so far
    # if cur_end_word = -1 then it is non existant (ie 0 word translated so far)
    # (items of form (cost,trans_info_so_far,cur_cost,back_track)
    wipe_future_estimate_cache()
    phrase_to_max_log_prob = get_phrase_to_max_prob(log_phrase_table)
    len_source = len(source)
    initial_bounds = [(0,len_source-1)]
    estimate_cost = log_future_cost(initial_bounds, source, phrase_to_max_log_prob)
    initial_value = (estimate_cost,(initial_bounds,-1,""),0,[])
    hypothesis_stacks = [[] for _ in range(1+len_source)]
    thresh = [-inf for _ in range(1+len_source)]
    heappush(hypothesis_stacks[0],initial_value)
    for i,stack in enumerate(hypothesis_stacks):
        if i == len_source:
            break
        # print()
        if i != 0 and __name__ != "__main__":
            print(time.time()-start)
            print('******************')
            print(i)
            print(len(stack))
            best_hyp = max(stack)
            print(best_hyp)
        start = time.time()
        while stack:
            current_hyp = heappop(stack)
            # print("Considering: " + str(current_hyp))
            cur_cost_current:float = current_hyp[2]
            current_trans_info = current_hyp[1]
            current_backtrack = current_hyp[3]
            current_bounds = current_trans_info[0]
            targ_so_far = current_trans_info[2]
            cur_end_f_word = current_trans_info[1]
            for new_hyp,covered_count in get_new_hyps(current_bounds,log_phrase_table,source,len_source):
                hyp_start,hyp_end,hyp_trans = new_hyp
                hyp_bounds = remove_section_from_bounds(current_bounds.copy(),(hyp_start,hyp_end))
                log_fut_cost_hyp:float = log_future_cost(hyp_bounds,source,phrase_to_max_log_prob)
                if log_fut_cost_hyp + cur_cost_current < thresh[covered_count]:
                    continue

                log_cur_cost_hyp = log_cur_cost(cur_cost_current,new_hyp,targ_so_far,cur_end_f_word,source,log_phrase_table,lang_model)
                cost = log_cur_cost_hyp+log_fut_cost_hyp

                if targ_so_far:
                    new_trans = targ_so_far+" " +hyp_trans
                else:
                    new_trans = hyp_trans
                new_hyp_item = hyp_bounds,new_hyp[1],new_trans
                back_track = current_backtrack.copy()
                back_track.append(new_hyp)
                add_to_hypothesis_stack(hypothesis_stacks,(cost,new_hyp_item,log_cur_cost_hyp,back_track),thresh,covered_count)

    best_hyp = max(hypothesis_stacks[len_source])
    return best_hyp


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

    phrase_table = ibmmodel1.get_phrase_probabilities(alignments, sentance_pairs)
    log_phrase_table = ibmmodel1.get_log_phrase_table(phrase_table)
    lang_model = LanguageModel([e for _,e in sentance_pairs], n=2)
    # ibmmodel1.print_phrase_table(log_phrase_table)


    # Tests:
    print()
    print("Tests: ")
    print()
    foreign_sentence = "la casa".split(" ")
    # ignore the issue to short message - minor bug will fix later
    # These tests are out because of changing omega value
    # print_or_value(1, log_cur_cost(0,[], foreign_sentence, log_phrase_table, lang_model), log(1))
    print_or_value(2, log_cur_cost(0,(0,0,"the big"),"",-1, foreign_sentence, log_phrase_table, lang_model), -2.367123614131617)
    print_or_value(3, log_cur_cost(0,(1,1,"shop"),"",-1, foreign_sentence, log_phrase_table, lang_model), -1.6739764335716714)
    print_or_value(4, log_cur_cost(0,(0,0,"the big house"),"",-1, foreign_sentence, log_phrase_table, lang_model), -3.0602707946915624)
    print_or_value(5, log_cur_cost(log(0.041666666666666664),(1,1,"shop"),"the big",0, foreign_sentence, log_phrase_table, lang_model), -5.2574953720277815)
    print()
    phrase_to_max_log_prob = get_phrase_to_max_prob(log_phrase_table)
    print_or_value(6, log_future_cost([(0,1)], foreign_sentence, phrase_to_max_log_prob), log(0.5))
    # translated [(0, 0, "the big")]
    print_or_value(7, log_future_cost([(1,1)], foreign_sentence, phrase_to_max_log_prob), log(0.5))
    # translated [(1,1,"shop")]
    print_or_value(8, log_future_cost([(0,0)], foreign_sentence, phrase_to_max_log_prob), log(0.5))
    # translated [(0,0,"the big house")]
    print_or_value(9, log_future_cost([(1,1)], foreign_sentence, phrase_to_max_log_prob), log(0.5))
    # translated [(0,0,"the big"),(1,1,"shop")]
    print_or_value(10, log_future_cost([], foreign_sentence, phrase_to_max_log_prob), log(1))
    print()
    print_or_value(11, beam_search_stack_decoder(["la","casa"],lang_model, log_phrase_table), 'the big')
    print_or_value(12, beam_search_stack_decoder(["la"],lang_model, log_phrase_table), 'the big')
