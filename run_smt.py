import ibmmodel1
import decoder_with_log
from faster_lang_model import LanguageModel
from data_prep_tools import get_data
import time
import general
import ibm_models


sentence_pairs = general.get_sentance_pairs()
lang_model = LanguageModel([p for _, p in sentence_pairs], n=2)
# log_phrase_table = ibm_models.open_phrase_table("log_new_var_id_phrase_table_m1.txt")
log_phrase_table = ibm_models.open_phrase_table(" .txt")
# log_phrase_table = ibm_models.open_phrase_table("log_pruned_var2var_phrase_table_m1.txt")
source = "VARIABLE_0 equals VARIABLE_0 multiplied by NUMBER then VARIABLE_0 equals VARIABLE_0 multiplied by NUMBER then return VARIABLE_0".split(" ")
# for key in log_phrase_table:
#     if key.startswith("it ") and len(key) < 10:
#         print(key)
#         print(log_phrase_table[key])

start_time = time.time()
answer = decoder_with_log.beam_search_stack_decoder_with_back_track(source,lang_model,log_phrase_table)
for start,end,value in answer[3]:
    print(start,end,value,source[start:end+1])
print("In total:",time.time() - start_time)