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

a = [i for i in range(10)]
a.insert(3,"x")
print(a)


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

bounds = (get_unused_phrase_boundaries([(7,7,"a"),(16,19,"b"),(21,22,"c")],23))

used_word_count = 23
for start, end in bounds:
    used_word_count -= end - start + 1
print(used_word_count)