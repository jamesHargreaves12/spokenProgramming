from langModel.faster_lang_model import LanguageModel
from smt import ibmmodel1, ibmmodel2, ibm_models, decoder_with_log
from smt.general import get_sentance_pairs

# Constants = n
from smt.ibmmodel1 import get_alignments_1
from smt.test_models import print_alignment


def get_language_model(train_data,n,norm_toks_flag=False):
    pseudocode_toks = [p for _,p in train_data]
    return LanguageModel(pseudocode_toks,n,norm_toks_flag=norm_toks_flag)

# Constants = epoch,null_flag
# from ibmmodels (applies also to model2) = PREVENT_VARIABLE_TO_NULL_MAP
def get_alignment_1(sentence_pairs: list, epoch: int, null_flag: bool,fm_flag=False):
    return get_alignments_1(sentence_pairs, epoch, null_flag,fm_flag=fm_flag)


def get_p_table_1(sentence_pairs, alignments):
    return ibmmodel1.get_phrase_table_m1(alignments, sentence_pairs)


# Constants = m1_loop_count,m2_loop_count,null_flag
# Constants in File = D_SIGMA
# prune Constants = e_max_length, f_max_length
# sentance_pairs are zipped
def get_alignment_2(sentence_pairs: list, epoch: int, null_flag: bool,fm_flag=False):
    align = ibmmodel2.get_alignments_2(sentence_pairs, epoch, epoch, null_flag,fm_flag=fm_flag)
    return align

def get_p_table2(sentance_pairs,alignment):
    phrase_t = ibmmodel2.get_phrase_table_m2(sentance_pairs,alignment)
    return phrase_t


# sentance_pairs are zipped
def get_log_phrase_table(sentence_pairs,alignments):
    phrase_t = ibm_models.get_phrase_probabilities(sentence_pairs,alignments)
    ibm_models.prune_phrase_table(phrase_t, e_max_length=9, f_max_length=15)
    return ibm_models.get_log_phrase_table(phrase_t)


# Constants(in file decoder) = alpha,omega
def run_smt(lang_model,log_phrase_table,source,initial_trans=""):
    return decoder_with_log.beam_search_stack_decoder(source, lang_model, log_phrase_table,first_trans_tok=initial_trans)

