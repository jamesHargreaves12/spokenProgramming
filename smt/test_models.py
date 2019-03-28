# def get_neighbours(point):
#     x=point[0]
#     y=point[1]
#     points = [(x-1,y-1),(x,y-1),(x+1,y-1),(x-1,y),(x+1,y),(x-1,y+1),(x,y+1),(x+1,y+1)]
#     return filter(lambda a:a[0]>=0 and a[1]>=0,points)
#
#
# def in_unique_row_col(point,cur_points):
#     unique_row = True
#     unique_col = True
#     for cur_point in cur_points:
#         if cur_point[0]== point[0]:
#             unique_row = False
#         if cur_point[1] == point[1]:
#             unique_col = False
#     return unique_row, unique_col

# def get_phrase_alignment(t_e_given_f, t_f_given_e, fs, es, null_flag=True):
#     # http://ivan-titov.org/teaching/elements.ws13-14/elements-7.pdf alg from here
#     # likely can be improved using a data structure
#     if null_flag:
#         fs = ["NULL"] + fs
#         es = ["NULL"] + es
#     f_given_e_pairing = ibmmodel1_with_variables.get_best_pairing(t_f_given_e, fs, es)
#     e_given_f_pairing = ibmmodel1_with_variables.get_best_pairing(t_e_given_f, es, fs)
#     e_given_f_rev = [(y,x) for x,y in e_given_f_pairing]
#
#     print(f_given_e_pairing)
#     print_alignment(f_given_e_pairing, len(fs), len(es), fs, es)
#     print()
#     print(e_given_f_rev)
#     print_alignment(e_given_f_rev, len(fs), len(es), fs, es)
#     print()
#
#     phrase_alignment = _get_phrase_alignmnet_by_symmetry(f_given_e_pairing,e_given_f_rev)
#     if null_flag:
#         # if maps to null then drop it in either direction and reduce the index by 1
#         phrase_alignment = [(f-1,e-1) for f,e in phrase_alignment if f*e != 0]
#     return phrase_alignment
#
#
# def _get_phrase_alignmnet_by_symmetry(f_given_e_pairing,e_given_f_rev):
#     alignment = f_given_e_pairing.intersection(e_given_f_rev)
#     union = f_given_e_pairing.union(e_given_f_rev).difference(alignment)
#     to_check_stack = list(alignment)
#     # diagonal
#     while to_check_stack:
#         point = to_check_stack.pop()
#         for neighbour in union.intersection(get_neighbours(point)):
#             unique_row,unique_col = in_unique_row_col(neighbour,alignment)
#             if unique_row or unique_col:
#                 alignment.add(neighbour)
#                 to_check_stack.append(neighbour)
#                 union.remove(neighbour)
#     #finalise
#     for point in union:
#         unique_row, unique_col = in_unique_row_col(point, alignment)
#         if unique_row and unique_col:
#             alignment.add(point)
#
#     return alignment


def print_alignment(align,sentence_pair):
    es, fs= sentence_pair
    max_e = len(es)
    max_f = len(fs)
    print("  "+" ".join([f[0] for f in fs]))
    for e in range(max_e):
        print_str = es[e][0]+" "
        for f in range(max_f):
            if (e,f) in align:
                print_str += "x "
            else:
                print_str += ". "
        print(print_str)

# transcripts = get_data.get_data_from_directory("/transcripts_var_replaced/")
# pseudocode = get_data.get_data_from_directory("/pseudocode_simplified/")
# tokenized_pseudocode = []
# tokenized_transcripts = []
# for i,pseudo in enumerate(pseudocode):
#     tokenized_pseudocode.append([y.strip("\n") for y in pseudo.split(" ") if y != ""])
#     tokenized_transcripts.append([y.strip("\n") for y in transcripts[i].split(" ") if y != ""])
#
# sentance_pairs = list(zip(tokenized_transcripts,tokenized_pseudocode))
#
# p_to_e = ibmmodel1_with_variables.train(sentance_pairs, 100)
# reversed = [(x, y) for y, x in sentance_pairs]
# e_to_p = ibmmodel1_with_variables.train(reversed, 100)
# es = "take the VARIABLE and multiply it by NUMBER get the VARIABLE multiply VARIABLE by NUMBER to get the VARIABLE and return the VARIABLE".split(" ")
# ps = "VARIABLE = VARIABLE * NUMBER VARIABLE = VARIABLE * NUMBER return VARIABLE".split(" ")
# alignment = get_phrase_alignment(p_to_e,e_to_p,es,ps,null_flag=True)
# print_alignment(alignment,len(es),len(ps),es,ps)
#
#
#
# # alignments = [ibmmodel1.get_phrase_alignment(p_to_e, e_to_p, es, ps,null_flag=True) for es, ps in sentance_pairs]
# # source = "take the VARIABLE and multiply it by NUMBER get the VARIABLE multiply VARIABLE by NUMBER to get the VARIABLE and return the VARIABLE".split(" ")
# # for i,es_ps in enumerate(sentance_pairs):
# #     es = es_ps[0]
# #     if source == es:
# #         print(es)
# #         print_alignment(alignments[i],len(source),12)
# #         print()
# #
# # phrase_table = ibmmodel1.get_phrase_probabilities(alignments, sentance_pairs,null_flag=True)
# # # ibmmodel1.prune_phrase_table(phrase_table,6)
# # ibmmodel1.save_phrase_table(phrase_table,"phrase_table_m1.txt")
# #
# # log_phrase_table = ibmmodel1.get_log_phrase_table(phrase_table)
# # ibmmodel1.save_phrase_table(log_phrase_table,"log_phrase_table_m1.txt")
