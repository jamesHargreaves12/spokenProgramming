from smt import ibmmodel1, ibmmodel2, ibm_models, decoder_with_log
from smt.faster_lang_model import LanguageModel

# assume for now that the sentance_pairs are tokenized
# Constants = n
def train_lang_model(sentance_pairs):
    return LanguageModel([p for _,p in sentance_pairs],n=2)

# Constants = epoch,null_flag
# TODO check works with null_flag = False
# from ibmmodels (applies also to model2) = PREVENT_VARIABLE_TO_NULL_MAP
def train_ibmmodel1(sentance_pairs):
    return ibmmodel1.get_phrase_table_m1(sentance_pairs, epoch=100, null_flag=True)

# Constants = m1_loop_count,m2_loop_count,null_flag
# Constants in File = D_SIGMA
# can prune = constants = e_max_length, f_max_length
def train_ibmmodel2(sentance_pairs):
    phrase_t = ibmmodel2.get_phrase_table_m2(sentance_pairs,100,100,True)
    return ibm_models.prune_phrase_table(phrase_t, e_max_length=9, f_max_length=15)

def get_log_phrase_table(sentance_pairs):
    phrase_t = train_ibmmodel2(sentance_pairs)
    return ibm_models.get_log_phrase_table(phrase_t)

# source = string
# Constants(in file decoder) = alpha,omega
def run_smt(lang_model,log_phrase_table,source):
    return decoder_with_log.beam_search_stack_decoder_with_back_track(source, lang_model, log_phrase_table)
