import generate_folds

trans_folds,pseudo_folds = generate_folds.get_folds(5,method="SEQ")
validation_trans = trans_folds[-1]
validation_pseudo = pseudo_folds[-1]
train_test_trans = trans_folds[:-1]
train_test_pseudo = pseudo_folds[:-1]

# TODO backup on github
# TODO backup project data 2 on github
# todo baseline to smt_functions file
# TODO check decoder works with ibmmodel2 version
# TODO Form validation set optimizer
# TODO Using ^ get result for the other 4 folds
