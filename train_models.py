from data_prep_tools import get_data
import ibmmodel1


def print_alignment(align,max_e,max_f):
    for e in range(max_e):
        print_str = ""
        for f in range(max_f):
            if (e,f) in align:
                print_str += "x "
            else:
                print_str += "o "
        print(print_str)

transcripts = get_data.get_data_from_directory("/transcripts_var_replaced/")
pseudocode = get_data.get_data_from_directory("/pseudocode_simplified/")
tokenized_pseudocode = []
tokenized_transcripts = []
for i,pseudo in enumerate(pseudocode):
    tokenized_pseudocode.append([y.strip("\n") for y in pseudo.split(" ") if y != ""])
    tokenized_transcripts.append([y.strip("\n") for y in transcripts[i].split(" ") if y != ""])

sentance_pairs = list(zip(tokenized_transcripts,tokenized_pseudocode))

p_to_e = ibmmodel1.train(sentance_pairs, 1000)
reversed = [(x, y) for y, x in sentance_pairs]
e_to_p = ibmmodel1.train(reversed, 1000)
# alignments = [ibmmodel1.get_phrase_alignment(p_to_e, e_to_p, es, ps,null_flag=True) for es, ps in sentance_pairs]
# source = "take the VARIABLE and multiply it by NUMBER get the VARIABLE multiply VARIABLE by NUMBER to get the VARIABLE and return the VARIABLE".split(" ")
# for i,es_ps in enumerate(sentance_pairs):
#     es = es_ps[0]
#     if source == es:
#         print(es)
#         print_alignment(alignments[i],len(source),12)
#         print()
#
# phrase_table = ibmmodel1.get_phrase_probabilities(alignments, sentance_pairs,null_flag=True)
# # ibmmodel1.prune_phrase_table(phrase_table,6)
# ibmmodel1.save_phrase_table(phrase_table,"phrase_table.txt")
#
# log_phrase_table = ibmmodel1.get_log_phrase_table(phrase_table)
# ibmmodel1.save_phrase_table(log_phrase_table,"log_phrase_table.txt")
