from data_prep_tools import get_data


def get_sentance_pairs():
    transcripts = get_data.get_data_from_directory("/transcripts_var_replaced/")
    pseudocode = get_data.get_data_from_directory("/pseudocode_simplified/")
    tokenized_pseudocode = []
    tokenized_transcripts = []
    for i, pseudo in enumerate(pseudocode):
        tokenized_pseudocode.append([y.strip("\n") for y in pseudo.split(" ") if y != ""])
        tokenized_transcripts.append([y.strip("\n") for y in transcripts[i].split(" ") if y != ""])

    return list(zip(tokenized_transcripts, tokenized_pseudocode))
