from collections import defaultdict
import re
from itertools import permutations
import statistics
import matplotlib.pyplot as plt
from nltk.stem import PorterStemmer
from termcolor import colored,cprint
import math
import time
import random
from heapq import heappush, heappushpop
import threading
import multiprocessing
from math import exp,log
import os
# tokens = {'multiplied by': '*', 'i': 'i', 'FUNCTION_CALL': 'FUNCTION_CALL', 'for': 'for', 'out': '>', 'zap': '>', 'tac': '>', 'write to': '>', 'right angle': '>', 'gozinta': '>', 'right broket': '>', 'ket': '>', 'greater than': '>', 'into (or towards)': '>', 'blow': '>', 'right angle bracket': '>', 'plus': '+', 'intersection': '+', 'cross': '+', 'add': '+', 'left bracket': '[', 'bracket': '[', 'u turn turn back': '[', 'left square bracket': '[', 'opening bracket': '[', 'square': '[', 'right bracket': ']', 'unbracket': ']', 'u turn back': ']', 'right square bracket': ']', 'closing bracket': ']', 'unsquare': ']', 'newline': '\\n', 'backslash n': '\\n', 'in': '<', 'star': '*', 'asterisk': '*', 'glob': '*', 'wildcard': '*', 'aster': '*', 'Nathan Hale': '*', 'spider': '*', 'splat': '*', 'dingle': '*', 'twinkle': '*', 'gear': '*', 'mult': '*', 'times': '*', 'spider aster': '*', 'return': 'return', 'fizz': 'fizz', 'while': 'while', '0.2': '0.2', 'if': 'if', 'half-mesh': '=', 'equals': '=', 'quadrathorpe': '=', 'gets': '=', 'takes': '=', 'already': ')', 'right': ')', 'closing parenthesis': ')', 'close paren': ')', 'rparen': ')', 'closing round bracket': ')', 'right paren': ')', 'unparenthisey': ')', 'close': ')', 'thesis': ')', 'right ear': ')', 'wane': ')', 'right round bracket': ')', 'right parenthesis': ')', '100': '100', 'buzz': 'buzz', '1.1': '1.1', 'else': 'else', 'VARIABLE': 'VARIABLE', 'double-oh-seven': '%', 'grapes': '%', 'percent sign': '%', 'mod': '%', 'true': 'true', 'two-spot': ':', 'colon': ':', 'dots': ':', '1.2': '1.2', 'pretzel': '&', 'amper': '&', 'and sign': '&', 'reference': '&', 'amp': '&', 'ampersand': '&', 'address': '&', 'bitand': '&', 'and': 'and', 'background': '&', 'andpersand': '&', 'quotation marks': '"', 'double quote': '"', 'dirk': '"', 'rabbit-ears': '"', 'quote': '"', 'dirk rabbit-ears': '"', 'double-glitch': '"', 'double prime': '"', 'dieresis': '"', 'literal mark': '"', 'n': 'n', '9': '9', '1': '1', 'continue': 'continue', '20': '20', 'full stop': '.', 'decimal point': '.', 'spot': '.', 'dot': '.', 'point': '.', 'radix point': '.', 'period': '.', '2': '2', '5': '5', 'hyphen': '-', 'minus': '-', 'bithorpe': '-', 'worm': '-', 'option': '-', 'dak': '-', 'dash': '-', 'or': 'or', 'so': '(', 'left': '(', 'opening parenthesis': '(', 'open paren': '(', 'lparen': '(', 'opening round bracket': '(', 'left paren': '(', 'parenthisey': '(', 'open': '(', 'paren': '(', 'left ear': '(', 'wax': '(', 'left round bracket': '(', 'left parenthesis': '(', '21': '21', 'false': 'false', 'crunch': '<', 'tic': '<', 'read from to': '<', 'left angle': '<', 'comes-from': '<', 'left broket': '<', 'bra': '<', 'less than': '<', 'from (or towards)': '<', 'suck': '<', 'left angle bracket': '<', '11': '11', '3': '3', 'soldier': '!', 'excl': '!', 'factorial': '!', 'exclam': '!', 'wow': '!', 'eureka': '!', 'not': '!', 'bang': '!', 'spark-spot': '!', 'wham': '!', 'pling': '!', 'boing': '!', 'smash': '!', 'yell': '!', 'exclamation mark': '!', 'hey': '!', 'control': '!', 'shriek': '!', 'cuss': '!', 'stroke': '/', 'diagonal': '/', 'slash': '/', 'solidus': '/', 'over': '/', 'slant': '/', 'forward slash': '/', 'virgule': '/', 'slak': '/', 'slat': '/', 'u': 'u', '0': '0', '0.1': '0.1'}
# string = "VARIABLE equals VARIABLE multiplied by 1.2 then VARIABLE equals VARIABLE multiplied by 1.1 then return VARIABLE"
# cur_index = 0
# copy = ""
# while cur_index < len(string):
#     cur_max = 0
#     max_tok = ""
#     for tok in tokens.keys():
#         if cur_index + len(tok) <= len(string) and string[cur_index:cur_index + len(tok)] == tok \
#            and (cur_index + len(tok) == len(string) or string[cur_index + len(tok)] == " "):
#
#             cur_max = max(len(tok)+1,cur_max)
#             max_tok = tok
#     if cur_max == 0:
#         while cur_index < len(string):
#             if string[cur_index] == " ":
#                 cur_index += 1
#                 break
#             else:
#                 cur_index += 1
#     else:
#         copy += tokens[max_tok] + " "
#         cur_index += cur_max
# print(string)
# print(copy)
# print("VARIABLE = VARIABLE * 1.2 VARIABLE = VARIABLE * 1.1 return VARIABLE")
#
# transcript_data = " let variable VARIABLE equal 1.2 times VARIABLE variable VARIABLE equal 1.1 times VARIABLE return VARIABLE"
# print(re.sub(r'[0-9].{0,1}[0-9]*', "NUMBER", transcript_data))
def mode(a):
    numeral=[(a.count(nb), nb) for nb in a]
    numeral = list(set(numeral))
    numeral.sort(key=lambda x:x[0], reverse=True)
    return(numeral[0][1])
x = []
x.insert(1,"a")
print(x)
# data = sorted(data)
# print(data)
# histogram = plt.hist(data,bins=20)
# plt.show()
# print(statistics.mean(data))
# print(mode(data))
# print(statistics.median(data))

# stemmer = PorterStemmer()
#
#
# def is_first_token_equal(transcript_words, token_identifier):
#     global stemmer
#     tok_words = token_identifier.split(" ")
#     for i,tok in enumerate(tok_words):
#         if i >= len(transcript_words) or not stemmer.stem(tok) == stemmer.stem(transcript_words[i]):
#             return False
#     return True
#
#
# def transcript_to_code_tokens(transcript, token_map):
#     transcript_tokens = transcript.split(" ")
#     orig_tokens = transcript_tokens
#     toks = token_map.keys()
#     removed = []
#     mapped = []
#     result = []
#     while True:
#         longest_tok = ""
#         length_longest_tok = 0
#         for tok in toks:
#             if is_first_token_equal(transcript_tokens, tok):
#                 length_tok = len(tok.split(" "))
#                 if length_tok > length_longest_tok:
#                     length_longest_tok = length_tok
#                     longest_tok = tok
#         if length_longest_tok == 0:
#             removed.append(transcript_tokens.pop(0))
#         else:
#             mapped.append((transcript_tokens[:length_longest_tok],token_map[longest_tok]))
#             transcript_tokens = transcript_tokens[length_longest_tok:]
#             result.append(token_map[longest_tok])
#
#         if len(transcript_tokens) == 0:
#             print_text = ""
#             i = 0
#             while i < len(orig_tokens):
#                 tok = orig_tokens[i]
#                 if tok == removed[0]:
#                     print_text += colored(" ".join(tok), "red")
#                     removed.pop(0)
#                     i += 1
#                 else:
#                     value = mapped.pop(0)
#                     i += len(value[0])
#                     original = " ".join(value[0])
#                     new = value[1]
#                     if original == new:
#                         print_text += colored(" ".join(value[0]),"blue")
#                     else:
#                         print_text += colored(" ".join(value[0])+"("+value[1]+")","blue")
#             print(print_text)
#             return result
#
# token_map = {"a": "a", "b c":"b", "a c":"c"}
# transcript = "a b b c a c d d c"
#
# print(transcript_to_code_tokens(transcript,token_map))

# data_not_stem = [0, 0, 0, 3, 8, 7, 0, 2, 0, 2, 7, 3, 3, 1, 2, 3, 7, 4, 4, 0, 1, 4, 1, 3, 11, 5, 2, 4, 3, 33, 16, 30, 11, 3, 2, 7, 1, 6, 6, 2, 2, 4, 5, 2, 8, 2, 1, 3, 10, 3, 19, 8, 6, 6, 10, 7, 6, 14, 0, 0, 1, 6, 0, 12, 3, 13, 29, 36, 23, 45, 16, 6, 8, 0, 1, 8, 5, 1, 9, 2, 2, 1, 3, 4, 3, 2]
# data_stem     = [0, 0, 0, 3, 8, 7, 0, 2, 0, 2, 7, 3, 3, 1, 2, 3, 7, 4, 4, 0, 1, 4, 1, 2, 11, 5, 2, 4, 3, 32, 16, 30, 12, 3, 2, 7, 1, 5, 7, 2, 2, 4, 5, 2, 8, 2, 1, 3, 10, 3, 20, 9, 6, 6, 10, 7, 6, 14, 0, 0, 1, 6, 0, 12, 3, 13, 29, 36, 23, 45, 16, 6, 8, 0, 1, 8, 5, 1, 9, 2, 2, 1, 3, 4, 3, 2]
# error_not_stem = [0.0, 0.0, 0.0, 0.15, 0.6666666666666666, 0.7777777777777778, 0.0, 0.1111111111111111, 0.0, 0.14285714285714285, 0.3888888888888889, 0.15789473684210525, 0.3, 0.07142857142857142, 0.5, 0.21428571428571427, 0.5384615384615384, 0.23529411764705882, 0.3076923076923077, 0.0, 0.0625, 0.26666666666666666, 0.3333333333333333, 0.11538461538461539, 0.6470588235294118, 0.3333333333333333, 0.16666666666666666, 0.5, 0.21428571428571427, 0.75, 0.35555555555555557, 0.7317073170731707, 0.3055555555555556, 0.17647058823529413, 0.07407407407407407, 0.28, 0.038461538461538464, 0.3, 0.3, 0.14285714285714285, 0.125, 0.2222222222222222, 0.35714285714285715, 0.125, 0.47058823529411764, 0.2, 0.06666666666666667, 0.3, 0.625, 0.2, 0.6129032258064516, 0.21621621621621623, 0.21428571428571427, 0.18181818181818182, 0.4166666666666667, 0.2692307692307692, 0.18181818181818182, 0.4117647058823529, 0.0, 0.0, 0.058823529411764705, 0.3157894736842105, 0.0, 0.631578947368421, 0.06976744186046512, 0.34210526315789475, 0.6744186046511628, 0.3870967741935484, 0.23, 0.6923076923076923, 0.8421052631578947, 0.3333333333333333, 0.5333333333333333, 0.0, 0.05, 0.5333333333333333, 0.25, 0.045454545454545456, 0.42857142857142855, 0.125, 0.125, 0.0625, 0.21428571428571427, 0.25, 0.1875, 0.15384615384615385]
#
# print(sum(error_not_stem)/len(error_not_stem))
# # print(sum(data_not_stem))
# # print(sum(data_stem))
# # print(mode(data_stem))
# # print(statistics.median(data_stem))
# print()
# histogram = plt.hist(error_not_stem,bins=20)
# plt.show()
#
# for i in range(len(data_stem)):
#     if data_stem[i]>data_not_stem[i]:
#         print(i)

def increment_alignment_with_count(i,alignment_mapping, counts):
    alignment_mapping[i] += 1
    while alignment_mapping[i] == len(counts):
        alignment_mapping[i] = 0
        counts[-1] -= 1
        counts[0] += 1
        i += 1
        if i == len(alignment_mapping):
            return
        alignment_mapping[i] += 1
    counts[alignment_mapping[i]-1] -= 1
    counts[alignment_mapping[i]] += 1

# randsx = [random.random() for _ in range(1000000)]
# randsy = [random.random() for _ in range(1000000)]
# start = time.time()
# for x,y in zip(randsx,randsy):
#     a = max(x,y)
# print(time.time()-start)
#
# start = time.time()
# for x,y in zip(randsx,randsy):
#     a = x if x > y else y
# print(time.time()-start)


def add_to_hypothesis_stack(stack,item):
    cost = item
    if len(stack) >= 6:
        if cost <= stack[0]:
            # this item is worse than all the items on the stack so do nothing
            return
        else:
            # add the item to the stack and then pop the worst
            heappushpop(stack,item)
    else:
        heappush(stack,item)


def transform(x):
    for i in range(1000):
        y = exp(log(exp(log(exp(log(pow(x,3.23)))))))
    return x


def transform_and_append(x,output_list):
    output_list.append(transform(x))
# input_list = [random.random() for _ in range(10000)]
# output_list =[]
# start = time.time()
# for x in input_list:
#     output_list.append(transform(x))
# print("Single Worker", time.time()-start)

# input_list = [random.random() for _ in range(10000)]
# output_list =[]
# start = time.time()
# pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
# for i in input_list:
#     pool.apply_async(func=transform_and_append,args=(i,output_list))
# pool.close()
# pool.join()
# print(len(output_list))
# print("Pooled Workers",time.time()- start)
#
# transform_and_append(3,output_list)
# print(output_list)
#
# dir_names = ["audio","transcripts","pseudocode","transcripts_var_replaced","pseudocode_simplified","variable_list"]
# for i in range(1, 17):
#     dir = base_dir + str(i)
#     if not(os.path.exists(dir)):
#         os.mkdir(dir)
#     for name in dir_names:
#         os.mkdir(dir+"/"+name)

#
# test = "asf's"
# test = re.sub(r"([a-z]?)'([a-z]?)",r"\1\2",test)
#
# # replacements = {r"([a-z]?)'([a-z]?)" : r"\1\2"}
# print(test)
# test = re.compile(r" \|([a-z+0-9_]+?):([0-9]+?)_([A-Z0-9]+?)\| \|([a-z+0-9_]+?):([0-9]+?)_([A-Z0-9]+?)\| [_]?\)\n")
# test = re.compile(r"\(\|([a-z]+?)\|( _| \|[a-z]+\|){0,1} \|([a-z+0-9_]+?):([0-9]+?)_([A-Z&0-9]+?)\| \|([a-z+0-9_]+?):([0-9]+?)_([A-Z0-9&]+?)\|( _| \|[a-z]+\|){0,1}\)\n")
# test = re.compile(r"\(\|([a-z]+?)\| \|([a-z+0-9_]+?):([0-9]+?)_([A-Z&0-9]+?)\|\)\n")

# test = re.compile(r"\(\|([a-z0-9]+?)\|( _| \|[a-z]+\|){0,1} \|([a-z+0-9_]+?):([0-9]+?)_([A-Z&0-9]+?)\| \|([a-z+0-9_]+?):([0-9]+?)_([A-Z0-9&]+?)\|( _| \|[a-z]+\|){0,1}\)\n")

test = re.compile(r"\(\|([\'a-z+0-9_]+?)\|(?: _| \|[a-z]+\|){0,1}(?: \|(?:[\'A-Za-z+0-9_]+):(?:[0-9]+)_(?:[A-Z&0-9$]+)\|){0,1} \|([\'A-Za-z+0-9_]+?):([0-9]+?)_([A-Z&0-9$]+?)\| \|([\'A-Za-z+0-9_]+?):([0-9]+?)_([A-Z0-9&$]+?)\|( _| \|[a-z]+\|){0,1}\)\n")

# test = re.compile(r"\(\|([a-z]+?)\| \|([a-z+0-9_]+?):([0-9]+?)_([A-Z&0-9]+?)\|\)\n")

# test = re.compile(r"\|([a-z+0-9_]+?):([0-9]+?)_([A-Z&0-9]+?)\|")
str1 = r'''(|ncsubj| |equal+s:1_VVZ| |variable_1:0_NP1| _)
'''
str2 = r'''(|dobj| |time+s:3_VVZ| |number:4_NN1|)
'''
str3 = r'''(|ncsubj| |equal+s:6_VVZ| |variable_2:5_NP1| _)
'''
str4 = r'''(|ncmod| _ |return:14_VV0| |then:13_RR|)
'''
str5 = r'''(|passive| |name+ed:10_VVN|)
'''
str6 = r'''(|ncsubj| |name+ed:10_VVN| |variable:9_NN1| |obj|)
'''
str7 = r'''(|ncmod| |num| |return:13_NN1| |next:12_MD|)
'''
str8 = r'''(|obj2| |add:4_VV0| |variable_1:11_&FO|)
'''
str9 = r'''(|ccomp| |that:35_CST| |store:34_NN1| |end:38_VV0|)
'''
str10 = r'''(|ncsubj| |return:11_VV0| |I:10_PPIS1| _)
'''
str11 =r'''(|arg_mod| _ |be+s:11_VBZ| |where:9_RRQ|)
'''
str12 =r'''(|det| |value:36_NN1| |our:34_APP$|)
'''

strings = [str1,str2,str3,str4,str5,str6,str7,str8,str9,str10,str11,str12]
for str in strings:
    print(test.match(str))


# print()
# print()
#
# print(test.match(str1)[1] == 'ncsubj')
# print(test.match(str1)[2] == 'equal+s')
# print(test.match(str1)[3] == '1')
# print(test.match(str1)[4] == 'VVZ')
# print(test.match(str1)[5] == 'variable_1')
# print(test.match(str1)[6] == '0')
# print(test.match(str1)[7] == 'NP1')
#
# str = "\\n"
# tokens_re = re.compile(r'\\n')
# print(tokens_re.match(str))
# for i in range(0,13):
#     print(test.match(str1)[i])


indices = [i for i in range(133)]
