from nltk.stem import PorterStemmer
from tools import generate_folds
from tools.enhanced_split import splits_on_end_toks, stem_all_words, split_files_further, \
    remove_dead_tokens

stemmer = PorterStemmer()

new_exp_keywords = [("while","while"), ("for","for"), ("if","if"), ("else","else"), ("return","output")]


def find_next_location(word, tokens,start_pos):
    for i in range(start_pos, len(tokens)):
        if tokens[i] == word:
            return i
    return -1


def split_data(data,index_included_flag=False):
    splits = []
    trans_key_words = [x for x,_ in new_exp_keywords]
    for data_i in range(len(data)):
        ts,ps = data[data_i]
        if index_included_flag:
            ts = [x for x,_ in ts]
            ps = [x for x,_ in ps]
        ps_split_start = 0
        ts_split_start = 0
        end_discount = 0
        for i in range(2,len(ts)):
            if stemmer.stem(ts[i]) in trans_key_words or ts[i] == "else":
                if end_discount > 0:
                    end_discount = 0
                    continue
                if i+2 < len(ts) and stemmer.stem(ts[i+1]) == "it" \
                        and stemmer.stem(ts[i+2]) == "is":
                    continue
                stemmed_tsi = stemmer.stem(ts[i]) if ts[i] != "else" else ts[i]
                if ts[i] == "else":
                    pseud_tok = "else"
                else:
                    pseud_tok = new_exp_keywords[trans_key_words.index(stemmer.stem(ts[i]))][1]
                ps_split_end = find_next_location(pseud_tok,ps,ps_split_start+1)
                if ps_split_end == -1 or ps_split_end-ps_split_start <= 1:
                    continue
                splits.append((data[data_i][0][ts_split_start:i],data[data_i][1][ps_split_start:ps_split_end]))
                ps_split_start = ps_split_end
                ts_split_start = i
            elif ts[i] == "end":
                end_discount = 2
            else:
                end_discount -= 1

        if len(ts) - ts_split_start >= 1:
            splits.append((data[data_i][0][ts_split_start:len(ts)],data[data_i][1][ps_split_start:len(ps)]))

    return splits



def flatten(lss):
    return [item for sublist in lss for item in sublist]

def get_train_test_split(train_test_folds,i):
    test = train_test_folds[i]
    train_folds = train_test_folds[:i]+train_test_folds[i+1:]
    return test,flatten(train_folds)

with_shuffle = True
sentence_pair_folds = generate_folds.get_folds(10, "SEQ", with_shuffle)
validation_set = sentence_pair_folds[-1]
train_test_folds = sentence_pair_folds[:-1]
train_test_data = flatten(train_test_folds)
test_train_split = [get_train_test_split(train_test_folds, i) for i in range(len(train_test_folds))]

def get_splits(data, type_split="none"):
    if type_split is "none":
        pass
    elif type_split == "split":
        return split_data(data)
    elif type_split == "enhanced":
        return smt_enhanced_preprocessing(data)
    elif type_split == "enhanced_index":
        return smt_enhanced_preprocessing(data,index_included_flag=True)
    else:
        print("unknown data type: {}.".format(type_split))
    return data

def smt_enhanced_preprocessing(data,miss_which=-1,index_included_flag=False):
    splits = data
    splits = split_data(splits,index_included_flag=index_included_flag)
    if miss_which != 1:
        splits = splits_on_end_toks(splits,index_included_flag=index_included_flag)
    if miss_which != 2:
        splits = stem_all_words(splits,index_included_flag=index_included_flag)
    if miss_which != 4:
        splits = split_files_further(splits,index_included_flag=index_included_flag)
    if miss_which != 3:
        splits = remove_dead_tokens(splits,index_included_flag=index_included_flag)
    return split_data(splits,index_included_flag=index_included_flag)



if __name__ == "__main__":
    pass
    # splits = split_data(train_test_data)
    # for ts,ps in splits:
    #     if len(ts) == 1 or len(ps) == 1:
    #         print(ts,ps)

    # data = train_test_data
    # splits = split_data(data)
    # pair_start = 0
    # for i in range(len(data)):
    #     sum = 0
    #     ts_col_string = ""
    #     ps_col_string = ""
    #     toggle = False
    #     while sum < len(data[i][0]):
    #         pair = splits[pair_start]
    #         ts_col_string += colored(" ".join(pair[0]) + "   ", "blue" if toggle else "red")
    #         ps_col_string += colored(" ".join(pair[1]) + "   ", "blue" if toggle else "green")
    #         toggle = not toggle
    #         sum += len(splits[pair_start][0])
    #         pair_start += 1
    #     print(ts_col_string)
    #     print(ps_col_string)
    #
    #     print()
    #     print()

    # fold1,_ = train_test_split[0]
    # print(len(fold1))
    # for file,_ in fold1:
    #     # print(file)
    #     print(" ".join(file))

