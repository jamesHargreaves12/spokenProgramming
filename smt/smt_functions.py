from langModel.faster_lang_model import LanguageModel
from smt import ibmmodel1, ibmmodel2, ibm_models, decoder_with_log
from smt.general import get_sentance_pairs

# Constants = n
def get_language_model(train_data,n):
    pseudocode_toks = [p for _,p in train_data]
    return LanguageModel(pseudocode_toks,n)

# Constants = epoch,null_flag
# from ibmmodels (applies also to model2) = PREVENT_VARIABLE_TO_NULL_MAP
def get_log_table_1(sentance_pairs,epoch,null_flag):
    alignments = get_alignments_1(sentence_pairs,epoch,null_flag)
    return ibmmodel1.get_phrase_table_m1(sentance_pairs, epoch, null_flag)

def get_log_phrase_table1(sentance_pairs,epoch,null_flag):
    phrase_t = train_ibmmodel1(sentance_pairs,epoch,null_flag)
    ibm_models.prune_phrase_table(phrase_t, e_max_length=9, f_max_length=15)
    return ibm_models.get_log_phrase_table(phrase_t)


# Constants = m1_loop_count,m2_loop_count,null_flag
# Constants in File = D_SIGMA
# prune Constants = e_max_length, f_max_length
# sentance_pairs are zipped
def train_ibmmodel2(sentance_pairs,epoch,null_flag):
    phrase_t = ibmmodel2.get_phrase_table_m2(sentance_pairs,epoch,epoch,null_flag)
    ibm_models.prune_phrase_table(phrase_t, e_max_length=9, f_max_length=15)
    return phrase_t

# sentance_pairs are zipped
def get_log_phrase_table2(sentance_pairs,epoch,null_flag):
    phrase_t = train_ibmmodel2(sentance_pairs,epoch,null_flag)
    return ibm_models.get_log_phrase_table(phrase_t)


# Constants(in file decoder) = alpha,omega
def run_smt(lang_model,log_phrase_table,source):
    return decoder_with_log.beam_search_stack_decoder(source, lang_model, log_phrase_table)

