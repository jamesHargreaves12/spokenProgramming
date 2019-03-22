from smt import ibmmodel2, ibm_models

from data_prep_tools import get_data


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
# print(sentance_pairs[0][0])
# print(sentance_pairs[1][0])
# print(sentance_pairs[2][0])
# print(sentance_pairs[3][0])
# print(sentance_pairs[4][0])
# p_table1 = ibmmodel1.get_phrase_table_m1(sentance_pairs)
p_table2 = ibmmodel2.get_phrase_table_m2(sentance_pairs, 100, 100, null_flag=False)
ibm_models.prune_phrase_table(p_table2, e_max_length=9, f_max_length=15)

ibm_models.save_phrase_table(p_table2, "p_table_m2.txt")

# log_phrase_table = ibm_models.get_log_phrase_table(p_table2)
# ibm_models.save_phrase_table(log_phrase_table,"log_new_var_id_phrase_table_m1.txt")
