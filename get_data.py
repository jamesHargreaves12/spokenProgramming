from termcolor import colored

import generate_folds

def find_next_location(word, tokens,start_pos):
    for i in range(start_pos, len(tokens)):
        if tokens[i] == word:
            return i
    return -1


def split_data(data):
    splits = []
    keywords = ["while", "for", "if", "else", "return"]
    end_words = ["end"]
    for ts,ps in data:
        ps_split_start = 0
        ts_split_start = 0
        end_discount = 0
        for i in range(2,len(ts)):
            if ts[i] in keywords:
                if end_discount > 0:
                    end_discount = 0
                    continue
                split_end = find_next_location(ts[i],ps,ps_split_start+1)
                if split_end == -1 or split_end-ps_split_start <= 1:
                    continue
                splits.append((ts[ts_split_start:i],ps[ps_split_start:split_end]))
                ps_split_start = split_end
                ts_split_start = i
            elif ts[i] in end_words:
                end_discount = 2
            else:
                end_discount -= 1
        if len(ts) - ts_split_start > 1:
            splits.append((ts[ts_split_start:len(ts)],ps[ps_split_start:len(ps)]))

    return splits

def flatten(lss):
    return [item for sublist in lss for item in sublist]

def get_train_test_split(train_test_folds,i):
    test = train_test_folds[i]
    train_folds = train_test_folds[:i]+train_test_folds[i+1:]
    return test,flatten(train_folds)


sentence_pair_folds = generate_folds.get_folds(10, "SEQ")
validation_set = sentence_pair_folds[-1]
train_test_folds = sentence_pair_folds[:-1]
train_test_data = flatten(train_test_folds)
train_test_split = [get_train_test_split(train_test_folds,i) for i in range(len(train_test_folds))]

if __name__ == "__main__":
    # splits = split_data(train_test_data)
    # for ts,ps in splits:
    #     if len(ts) == 1 or len(ps) == 1:
    #         print(ts,ps)

    data = train_test_data
    splits = split_data(data)
    pair_start = 0
    for i in range(len(data)):
        sum = 0
        ts_col_string = ""
        ps_col_string = ""
        toggle = False
        while sum < len(data[i][0]):
            pair = splits[pair_start]
            ts_col_string += colored(" ".join(pair[0]) + "   ", "blue" if toggle else "red")
            ps_col_string += colored(" ".join(pair[1]) + "   ", "blue" if toggle else "green")
            toggle = not toggle
            sum += len(splits[pair_start][0])
            pair_start += 1
        print(ts_col_string)
        print(ps_col_string)

        print()
        print()
