from data_prep_tools import get_data
import ibmmodel1
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
alignments = [ibmmodel1.get_alignment(p_to_e, e_to_p, es, ps,null_flag=True) for es, ps in sentance_pairs]
phrase_table = ibmmodel1.get_phrase_probabilities(alignments, sentance_pairs,null_flag=True)
# ibmmodel1.prune_phrase_table(phrase_table,6)
ibmmodel1.save_phrase_table(phrase_table,"phrase_table.txt")
