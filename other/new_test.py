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
#
# a = [i for i in range(10)]
# a.insert(3,"x")
# print(a)
#
#
# def get_unused_phrase_boundaries(translated_phrases,len_source):
#     boundaries = [(0,len_source-1)]
#     for e_start,e_end,_ in translated_phrases:
#         remove_i = False
#         for i,phrase in enumerate(boundaries):
#             start_phrase,end_phrase = phrase
#             if e_start <= end_phrase:
#                 if start_phrase <= e_start-1:
#                     boundaries[i] = (start_phrase,e_start-1)
#                 else:
#                     remove_i = True
#
#                 if e_end+1 <= end_phrase:
#                     boundaries.insert(i+1,(e_end+1,end_phrase))
#                 break
#         if remove_i:
#             boundaries.pop(i)
#     return boundaries
#
# bounds = (get_unused_phrase_boundaries([(7,7,"a"),(16,19,"b"),(21,22,"c")],23))
#
# used_word_count = 23
# for start, end in bounds:
#     used_word_count -= end - start + 1
# print(used_word_count)
from smt import ibm_models, ibmmodel1, test_models
from smt.ibm_models import get_best_pairing

# test_pair = (['VARIABLE_0', 'equals', 'VARIABLE_0', 'multiplied', 'by', 'NUMBER', 'then', 'VARIABLE_0', 'equals', 'VARIABLE_0', 'multiplied', 'by', 'NUMBER', 'then', 'return', 'VARIABLE_0'], ['VARIABLE_0', '=', 'VARIABLE_0', '*', 'NUMBER', 'VARIABLE_0', '=', 'VARIABLE_0', '*', 'NUMBER', 'return', 'VARIABLE_0'])
#
# t_table_rev = ibmmodel1.open_t("t_3.txt")
# t_table_norm = ibmmodel1.open_t("t_2.txt")
#
# pairing1 = get_best_pairing(t_table_norm,test_pair[0],test_pair[1])
# pairing2 = get_best_pairing(t_table_rev, test_pair[1],test_pair[0])
#
# test_models.print_alignment(pairing1,test_pair)
# test_models.print_alignment(pairing2,(test_pair[1],test_pair[0]))

# print([1,2,3,4,5][3:4])
#
# alignment = [(0,0),(0,1),(1,2),(2,3),(3,3),(4,5),(5,4)]
#
#
# def get_smallest_phrase_set(alignment):
#     max_x = max([x for x,_ in alignment])
#     start_x = 0
#     phrases = []
#     while start_x <= max_x:
#         new_points = True
#         end_x = start_x
#         cur_set = []
#         while new_points:
#             cur_set = [(x,y) for x,y in alignment if start_x <= x <= end_x]
#             len_cur_set = len(cur_set)
#             ys = [y for _,y in cur_set]
#             min_y,max_y = min(ys),max(ys)
#             cur_set = [(x,y) for x,y in alignment if min_y <= y <= max_y]
#             new_points = not(len(cur_set) == len_cur_set)
#             end_x = max([x for x,_ in cur_set])
#         phrases.append((start_x,end_x,min_y,max_y))
#         start_x = end_x+1
#     return phrases
#
# def get_distances(phrases):
#     distances = []
#     sorted_ps = sorted(phrases,key=lambda x:x[2])
#     prev = (-1,-1,-1,-1)
#     for cur in sorted_ps:
#         dist = abs(cur[0] - prev[1] - 1)
#         distances.append(dist)
#         prev = cur
#     return distances
#
# alpha = 0.1
# def probability_distance(d,n,i):
#     num = math.pow(alpha,d)
#     den = 0
#     for j in range(n):
#         power = abs(i-j)
#         den += math.pow(alpha,power)
#     return num/den
#
# ps = (get_smallest_phrase_set(alignment))
# ds = get_distances(ps)
# print(ps)
# print(ds)
# for i,d in enumerate(ds):
#     print(probability_distance(d,5,i))

a = [1,2,3,4,5]
print(a[:1]+a[2:])
print(a[:0]+a[1:])
print(a[:4]+a[5:])