import math
from heapq import heappop,heappush
import ibmmodel1
from language_model import LanguageModel
from collections import defaultdict
import time
def d(start_i,last_end_i):
    # alpha^|start_i-last_end_i-1|
    alpha = 0.9
    return math.pow(alpha,abs(start_i-last_end_i-1))

def cur_cost(current_hyp, source, phrase_probs, lang_model: LanguageModel):
    translated_phrases = [x for _,_,x in current_hyp]
    translated_tokens = []
    for phrase in translated_phrases:
        translated_tokens.extend(phrase.split(" "))
    lang_model_probs = lang_model.get_prob_sentance(translated_tokens,padded_left=True,padded_right=False)

    translation_prob = 1
    distortion_prob = 1
    last_end_f = -1
    for cur_phrase in current_hyp:
        start_f,end_f,e = cur_phrase
        foreign_phrase = " ".join(source[start_f:end_f+1])
        translation_prob *= phrase_probs[foreign_phrase][e]
        if last_end_f != -1:
            distortion_prob *= d(start_f,last_end_f)
        last_end_f = end_f
    # print(translation_prob)
    # print(distortion_prob)
    # print(lang_model_probs)
    return lang_model_probs*distortion_prob*translation_prob

def get_start_poss_of_phrase(ticked,source,phrase):
    # could this be a nice FSM like in lexer?
    phrase_i = 0
    source_i = 0
    start_poss = []
    while source_i - phrase_i <= len(source) - len(phrase):
        if ticked[source_i]:
            phrase_i = 0
            source_i += 1
        elif phrase[phrase_i] == source[source_i]:
            phrase_i += 1
            source_i += 1
            if phrase_i == len(phrase):
                source_i -= phrase_i-1
                phrase_i = 0
                start_poss.append(source_i-1)
        else:
            source_i -= phrase_i -1
            phrase_i = 0
    return start_poss


def get_max_prob_estimate(sequence_of_words,phrase_to_max_prob):
    # initially this will just be the phrase_table eventually I would like this to be phrase_table with a language model applied to it in a preprocessing step
    # would be nice to have just phrase to probability mapping
    # http://www.statmt.org/book/slides/06-decoding.pdf computing table from here
    N = len(sequence_of_words)
    table = defaultdict(lambda :defaultdict(float))
    for n in range(N):
        for first_pos in range(N-n):
            phrase = " ".join(sequence_of_words[first_pos:first_pos+n+1])
            if phrase in phrase_to_max_prob:
                max_prob = phrase_to_max_prob[phrase]
            else:
                max_prob = 0
            for size_end in range(0,n):
                max_prob = max(max_prob,
                               table[n-1-size_end][first_pos]*table[size_end][first_pos+n-size_end])
            table[n][first_pos] = max_prob
    return table[N-1][0]


def future_cost(translated_phrases, source:list, phrase_to_max_prob):
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
    future_prob = 1
    for start,end in phrases:
        prob = get_max_prob_estimate(source[start:end+1],phrase_to_max_prob)
        future_prob *= prob
    return future_prob


# def future_cost(translated_phrases, source: list, phrase_table, lang_model:LanguageModel):
#     # estimated_lang_model just unigrams for now
#     translated_tokens = []
#     remaining_toks= source.copy()
#     for start_f,end_f,e in translated_phrases:
#         translated_tokens.extend(e.split(" "))
#         for tok in source[start_f:end_f+1]:
#             remaining_toks.remove(tok)
#     future_prob = 1
#     while remaining_toks:
#         # this can be improved since over generous:
#         possible_phrases = []
#         for i in range(len(remaining_toks)):
#             for j in range(i, len(remaining_toks)):
#                 possible_phrases.append(remaining_toks[i:j+1])
#
#         max_prob = 0
#         next_translation = ("","")
#         # print("START")
#         for pos_phrase in possible_phrases:
#             # print(pos_phrase)
#             for trans,trans_prob in phrase_table[" ".join(pos_phrase)].items():
#                 # print(pos_phrase, trans)
#                 trans_toks = trans.split(" ")
#                 lang_prob = lang_model.get_probability_next_phrase(translated_tokens,trans_toks)
#                 if trans_prob*lang_prob > max_prob:
#                     # print(trans_prob)
#                     # print(lang_prob)
#                     # print("HERE")
#                     max_prob = trans_prob*lang_prob
#                     next_translation = pos_phrase,trans_toks
#         if next_translation == ("",""):
#             # no possible translation so tokens map to NULL
#             break
#         for used_toks in next_translation[0]:
#             remaining_toks.remove(used_toks)
#         translated_tokens.extend(next_translation[1])
#         # print(next_translation)
#         # print(translated_tokens)
#         # print()
#         future_prob *= max_prob
#     return future_prob

def get_new_hyps(translated_phrases,phrase_table,source):
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
                if phrase in phrase_table:
                    for translation in phrase_table[phrase].keys():
                        new_hyp = translated_phrases.copy()
                        new_hyp.append((start_phrase,end_phrase,translation))
                        new_hyps.append((new_hyp,sum(ticked)+end_phrase-start_phrase+1))
    return new_hyps
    # for phrase,trans_prob in phrase_table.items():
    #     for trans,prob in trans_prob.items():
    #         phrase_toks = phrase.split(" ")
    #         for start_pos in get_start_poss_of_phrase(ticked,source,phrase_toks):
    #             new_hyp = translated_phrases.copy()
    #             new_hyp.append((start_pos,start_pos+len(phrase_toks)-1,trans))
    #             new_hyps.append((new_hyp,sum(ticked)+len(phrase_toks)))
    # return new_hyps

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

def beam_search_stack_decoder(source,lang_model,phrase_table):
    # using pseudocode on page 908 of J&M 2 edition
    # (items of form (-cost,translations)
    initial_value = (0,[])
    hypothesis_stacks = [[] for _ in range(1+len(source))]
    heappush(hypothesis_stacks[0],initial_value)
    phrase_to_max_prob = get_phrase_to_max_prob(phrase_table)

    for i,stack in enumerate(hypothesis_stacks):
        if i == len(source):
            break
        # print()
        if i != 0:
            print(time.time()-start)
        print('******************')
        print(i)
        start = time.time()
        while stack:
            current_hyp = heappop(stack)
            # print("Considering: " + str(current_hyp))
            for new_hyp,covered_count in get_new_hyps(current_hyp[1],phrase_table,source):
                cur_cost_hyp = cur_cost(new_hyp,source,phrase_table,lang_model)
                fut_cost_hyp = future_cost(new_hyp,source,phrase_to_max_prob)
                cost = cur_cost_hyp*fut_cost_hyp
                heappush(hypothesis_stacks[covered_count],(-cost,new_hyp))
                prune_stack(hypothesis_stacks[covered_count])
    return hypothesis_stacks[len(source)].pop(0)[1]


if __name__ == "__main__":

    def print_or_value(id, calculated, value):
        if value == calculated:
            print(True)
            # print()
        else:
            print(id,calculated)
            print()

    sentance_pairs = [(["la", "casa"],["the","big","house"]),(["casa", "pez","verde"],["green","house"]),(["casa"],["shop"])]
    t_f_given_e = ibmmodel1.train(sentance_pairs, 100)
    reversed = [(x,y) for y,x in sentance_pairs]
    t_e_given_f = ibmmodel1.train(reversed, 100)
    alignments = [ibmmodel1.get_alignment(t_f_given_e, t_e_given_f, fs, es) for fs, es in sentance_pairs]

    phrase_table = ibmmodel1.get_phrase_probabilities(alignments,sentance_pairs)
    lang_model = LanguageModel([e for _,e in sentance_pairs], n=2)
    ibmmodel1.print_phrase_table(phrase_table)
    # Tests:
    foreign_sentence = "la casa".split(" ")
    print_or_value(1, cur_cost([], foreign_sentence, phrase_table, lang_model), 1)
    print_or_value(2, cur_cost([(0,0,"the big")], foreign_sentence, phrase_table, lang_model), 0.041666666666666664)
    print_or_value(3, cur_cost([(1,1,"shop")], foreign_sentence, phrase_table, lang_model), 0.125)
    print_or_value(4, cur_cost([(0,0,"the big house")], foreign_sentence, phrase_table, lang_model), 0.013888888888888888)
    print_or_value(5, cur_cost([(0,0,"the big"),(1,1,"shop")], foreign_sentence, phrase_table, lang_model), 0.003472222222222222)

    phrase_to_max_prob = get_phrase_to_max_prob(phrase_table)
    print_or_value(6, future_cost([], foreign_sentence, phrase_to_max_prob), 0.25)
    print_or_value(7, future_cost([(0,0,"the big")], foreign_sentence, phrase_to_max_prob), 0.5)
    print_or_value(8, future_cost([(1,1,"shop")], foreign_sentence, phrase_to_max_prob), 0.5)
    print_or_value(9, future_cost([(0,0,"the big house")], foreign_sentence, phrase_to_max_prob), 0.5)
    print_or_value(10, future_cost([(0,0,"the big"),(1,1,"shop")], foreign_sentence, phrase_to_max_prob), 1)

    print_or_value(11, beam_search_stack_decoder(["la","casa"],lang_model, phrase_table), [(0, 0, 'the big'),(1,1,'house')])
    print_or_value(12, beam_search_stack_decoder(["la"],lang_model, phrase_table), [(0, 0, 'the big')])
