import generate_folds


def flatten(lss):
    return [item for sublist in lss for item in sublist]

sentence_pair_folds = generate_folds.get_folds(10, "SEQ")
validation_set = sentence_pair_folds[-1]
train_test_folds = sentence_pair_folds[:-1]
train_test_data = flatten(train_test_folds)
