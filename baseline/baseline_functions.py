# Constants = Stem_Flag, and size of langauge model (n)
from baseline import get_n_gram_reordering
from baseline.baseline_run import transcript_to_code_tokens
from langModel.faster_lang_model import LanguageModel
from baseline import get_pseudocode_token_list

# assumptions train data is a zipped list of transcript_simplified and pseudocode_simplified
# each of transcript is represented by a list of tokens

# Constants = n
def get_language_model(train_data,n):
    pseudocode_toks = [p for _,p in train_data]
    return LanguageModel(pseudocode_toks,n)


def get_pseudocode_tokens(train_data):
    pseudocode_toks = [p for _,p in train_data]
    return get_pseudocode_token_list.get_pseudocode_tokens(pseudocode_toks)


# infered constants = n in lang_model
# Constants = stem_flag, threshold
# transcript = stream of toks
def get_output_baseline(transcript, lang_model:LanguageModel, pseudocode_tokens, stem_flag, threshold):
    only_posible_tokens = transcript_to_code_tokens(transcript, pseudocode_tokens, stem_flag)
    return get_n_gram_reordering.get_most_likely_ordering_v2(only_posible_tokens, lang_model, threshold=threshold)
