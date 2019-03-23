from langModel.faster_lang_model import LanguageModel
import time
from smt import general, decoder_with_log, ibm_models

sentence_pairs = general.get_sentance_pairs()
lang_model = LanguageModel([p for _, p in sentence_pairs], n=2)
# log_phrase_table = ibm_models.get_log_phrase_table(ibmmodel1.get_phrase_table_m1(sentence_pairs))
log_phrase_table = ibm_models.open_phrase_table("log_new_var_id_phrase_table_m1.txt")

source = "VARIABLE_0 equals VARIABLE_0 multiplied by NUMBER then VARIABLE_0 equals VARIABLE_0 multiplied by NUMBER then return VARIABLE_0".split(" ")

start_time = time.time()
answer = decoder_with_log.beam_search_stack_decoder_with_back_track(source, lang_model, log_phrase_table)
for start,end,value in answer[3]:
    print(start,end,value,source[start:end+1])
print("In total:",time.time() - start_time)