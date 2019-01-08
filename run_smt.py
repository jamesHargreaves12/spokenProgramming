import ibmmodel1
import decoder
from language_model import LanguageModel
from data_prep_tools import get_data
import time

transcripts = get_data.get_data_from_directory("/transcripts_var_replaced/")
pseudocode = get_data.get_data_from_directory("/pseudocode_simplified/")
tokenized_pseudocode = []
tokenized_transcripts = []
for i,pseudo in enumerate(pseudocode):
    tokenized_pseudocode.append([y.strip("\n") for y in pseudo.split(" ") if y != ""])
    tokenized_transcripts.append([y.strip("\n") for y in transcripts[i].split(" ") if y != ""])

sentance_pairs = list(zip(tokenized_transcripts,tokenized_pseudocode))
lang_model = LanguageModel([p for _, p in sentance_pairs], n=2)
phrase_table = ibmmodel1.open_phrase_table("phrase_table.txt")
source = "take the VARIABLE and multiply it by NUMBER get the VARIABLE multiply VARIABLE by NUMBER to get the VARIABLE and return the VARIABLE".split(" ")
print(decoder.beam_search_stack_decoder(source,lang_model,phrase_table))