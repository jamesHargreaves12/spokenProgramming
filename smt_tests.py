import os

import useful_functions
from other.log_module import write_to_log
from smt import smt_functions, get_alpha_value, decoder_with_log
from smt.test_models import print_alignment
from tests.alignment_accuracy_simplified import get_pred_align_test_2, get_pred_align_test_1, score_alignment_recall, \
    combine_split_aligns, score_alignment_precision, print_alignment_compare
from tests.bag_of_words_test import bag_of_words_test
from tests.get_times_for_systems import get_time_for_files
from tests.minimum_edit_distance import minimum_edit_distance, minimum_edit_distance_per_token
from tools.find_resource_in_project import get_path
from tools.get_results_from_file import get_translations_results
from tools.get_test_data import split_data, test_train_split, train_test_data, validation_set, get_splits, flatten
# from traditional_tests import form_folds

n = 2
epoch = 100
null_flag = True


def get_translator(train,omega,fm_flag=False,model_num=2):
    if model_num == 2:
        alignments = smt_functions.get_alignment_2(train, epoch, null_flag,fm_flag=fm_flag)
    elif model_num == 1:
        alignments = smt_functions.get_alignment_1(train,epoch,null_flag,fm_flag)
    else:
        print("Unrecognised model num")
    log_phrase_table = smt_functions.get_log_phrase_table(train, alignments)
    lang_model = smt_functions.get_language_model(train, n, True)
    alpha = get_alpha_value.get_alpha(alignments)
    decoder_with_log.set_alpha(alpha)
    decoder_with_log.set_omega(omega)
    translator = lambda trans: smt_functions.run_smt(lang_model,log_phrase_table,trans).split(" ")
    return translator


def validate_ibmmodel(omega_range, model_num=2, split_type="none", fm_flag=False):
    print("Validate ibmmodel{}".format(model_num))
    preprocessed_train = get_splits(train_test_data, split_type)
    preprocessed_valid = get_splits(validation_set, split_type)
    results = []
    for omega in omega_range:
        message = "omega {}\n".format(omega)
        write_to_log(message)
        print("omega",omega)
        translator = get_translator(preprocessed_train,omega,fm_flag,model_num)
        med,_,_ = useful_functions.get_med_bow_norm(translator,preprocessed_valid)
        print(med)
        write_to_log("Edit distance = {}\n".format(med))
        results.append((omega,med))
    return results


def get_results(omega, model_num=2, split_type="none",fm_flag=False):
    med_results = []
    norm_med_results = []
    bow_results = []
    for pair in test_train_split:
        train = get_splits(pair[1],split_type)
        test  = get_splits(pair[0],split_type)
        translator = get_translator(train,omega,fm_flag,model_num)
        med,bow,norm_med = useful_functions.get_med_bow_norm(translator,test)
        write_to_log("Edit distance = {}\n".format(med))
        med_results.append(med)
        bow_results.append(bow)
        norm_med_results.append(norm_med)
    return med_results,bow_results,norm_med_results


def get_timings(omega,split_type="none",fm_flag=False,model_num=2):
    test,train = test_train_split[0]
    train = get_splits(train, split_type)
    # test = get_splits(test, split_type)
    translator = get_translator(train,omega,fm_flag,model_num)
    return get_time_for_files(translator,test,split_type)


def get_combined_predict_from_file(filename,train_test_folds,type_split):
    predicts = get_translations_results(filename)
    data = train_test_folds
    combined_predicts = []
    for fold in range(len(predicts)):
        fold_predicts = []
        preds = [x.split(" ") for x in predicts[fold]]
        preds_i = 0
        test,train = data[fold]
        for pair in test:
            split_pair = get_splits([pair], type_split=type_split)
            number_splits = len(split_pair)
            prediction = []
            for i in range(number_splits):
                if preds_i < len(preds):
                    prediction.extend(preds[preds_i])
                else:
                    print("not enough preds")
                preds_i += 1
            fold_predicts.append(prediction)
        combined_predicts.append(fold_predicts)
    return combined_predicts


def get_results_from_file(filename, type_split="none"):
    data = test_train_split
    predict_folds = get_combined_predict_from_file(filename,data,type_split)
    results_med = []
    results_bow = []
    print(" ".join(predict_folds[8][4]))
    print(" ".join(data[8][0][4][0]))
    print(" ".join(data[8][0][4][1]))
    results_norm_med = []
    for fold in range(len(predict_folds)):
        test,_ = data[fold]
        predicts = predict_folds[fold]
        med,bow,norm_med = 0,0,0
        assert(len(predicts) == len(test))
        print()
        print("FOLD NUM: ",fold)
        for pred,test_pair in zip(predicts,test):
            truth = test_pair[1]
            print(minimum_edit_distance(pred,truth))
            med += minimum_edit_distance(pred,truth)
            bow += bag_of_words_test(pred,truth)
            norm_med += minimum_edit_distance_per_token(pred,truth)
        results_med.append(med)
        results_bow.append(bow)
        results_norm_med.append(norm_med/len(test))
    return results_med,results_bow,results_norm_med


def get_results_from_file_with_split(filename, type_split="none"):
    predicts = get_translations_results(filename)
    results = []
    for fold,pair in enumerate(test_train_split):
        test,train = pair
        preds = predicts[fold]
        tot_med = 0
        num_split_per_file = [len(get_splits([pair],type_split)) for pair in test]
        test = get_splits(test,type_split)
        # print(num_split_per_file)
        print()
        print("FOLD NUM: ",fold)
        file_index = 0
        file_med = 0
        split_index = 0
        if not len(test) == len(preds):
            print("test != preds")
            print(len(test))
            print(len(preds))
        for pred,pair in zip(preds,test):
            trans,truth = pair
            med = minimum_edit_distance(pred.split(" "),truth)
            file_med += med
            tot_med += med
            split_index += 1
            if fold == 8 and file_index == 4:
                print(pred)
                print(" ".join(truth))
                print(" ".join(trans))
                print()
            if split_index == num_split_per_file[file_index]:
                split_index = 0
                file_index += 1
                print(file_med)
                file_med = 0
        results.append(tot_med)
    return results


def get_alignment_accuracies(split_type="none",fm_flag=False,model_num=2):
    test,train = test_train_split[0]
    split_train = get_splits(train,split_type)
    split_test = get_splits(test,split_type)
    if model_num == 2:
        pred_aligns = get_pred_align_test_2(split_train,split_test,fm_flag)
    elif model_num == 1:
        pred_aligns = get_pred_align_test_1(split_train,split_test,fm_flag)
    else:
        raise("Model number not known")
    alignments = combine_split_aligns(pred_aligns,test,split_test)
    # print_i = 2
    # print_alignment_compare(alignments[print_i],print_i,(test[print_i]))
    return score_alignment_recall(alignments),score_alignment_precision(alignments)


# def get_results_for_traditional_files(filename,split_type):
#     data = test_train_split
#     predict_folds = get_combined_predict_from_file(filename, data, split_type)
#     preds = flatten(predict_folds)
#     test = data[0]
#     test = [y for _,y in flatten(test)]
#     folds = form_folds(preds,test,9,without_train_flag=True)
#     print(len(flatten(folds)))
#     results = []
#     results_meds = []
#     for fold in folds:
#         print(len(fold))
#         med = 0
#         for pred,truth in fold:
#             med += minimum_edit_distance(pred,truth)
#             results_meds.append(minimum_edit_distance(pred,truth))
#         results.append(med)
#     return results,results_meds

def mean_2dp(test_list):
    return round((sum(test_list)/len(test_list)),2)

if __name__ == "__main__":
    # get min edit distance per fold
    # omega = 2.4
    # med,bow,norm_med = get_results(2.4, 2, split_type="enhanced")
    # print(med)
    # print(bow)
    # print(norm_med)

    # timings = get_timings(2.4,split_type="enhanced")

    # med,bow,norm = get_results_from_file("logs/results_enhanced.txt","enhanced")
    # print(med)
    # print(bow)
    # print(norm)
    # print(sum(med))

    # message = "split omega v2"
    # print(message)
    # write_to_log(message)
    # print(validate_ibmmodel2([2.9,3.1,2.8,3.2], split_type="split"))

    # med,bow,norm = get_results_from_file("logs/results_enhanced.txt","enhanced")
    # print(med)
    # print(bow)
    # print(norm)
    # med =   [199, 118, 170, 280, 115, 184, 75, 58, 161]
    # bl_med =[161, 107, 134, 187, 89, 137, 88, 80, 129]
    # print(sum(med))
    # print(sum(bl_med))

    test_num = 3

    if test_num == 0:
        message = "omega v1 100"
        print(message)
        write_to_log(message)
        decoder_with_log.beam_size = 100
        omegas = [3.0,2.7,2.3]
        validate_ibmmodel(omegas, 1, "none", False)
    elif test_num == 1:
        message = "enhanced omega v2"
        print(message)
        write_to_log(message)
        omegas = [3.0]
        validate_ibmmodel(omegas,2,"enhanced",True)
    elif test_num == 2:
        message = "results split v2"
        print(message)
        write_to_log(message)
        split_v2_omega = 2.9
        get_results(split_v2_omega,2,"split",False)
    elif test_num == 3:
        message = "results v2"
        print(message)
        write_to_log(message)
        split_v2_omega = 2.9
        get_results(split_v2_omega,2,"none",False)
    elif test_num == 4:
        message = "results split v1"
        print(message)
        write_to_log(message)
        split_v1_omega = 1.5
        get_results(split_v1_omega,1,"split",False)
    elif test_num == 5:
        message = "results enhanced"
        print(message)
        write_to_log(message)
        enhanced_omega = 2.6
        get_results(enhanced_omega,2,"enhanced",True)
    elif test_num == 6:
        print("Alignment accuracies")
        print("v2")
        v2_alignment= get_alignment_accuracies("none",False,2)
        # v2_alignment = ([0.85, 0.7575757575757576, 0.40963855421686746, 0.47368421052631576, 0.8181818181818182, 0.8333333333333334, 0.9090909090909091, 0.8571428571428571], [0.8947368421052632, 0.8148148148148148, 0.4827586206896552, 0.5454545454545454, 0.75, 0.7142857142857143, 0.76, 0.8518518518518519])
        print(mean_2dp(v2_alignment[0]))
        print(mean_2dp(v2_alignment[1]))
        print("split v1")
        split_v1_alignment = get_alignment_accuracies("split",False,1)
        # split_v1_alignment = ([0.3, 0.7878787878787878, 0.4578313253012048, 0.8947368421052632, 1.0, 0.8333333333333334, 0.6818181818181818, 0.5714285714285714], [1.0, 0.7241379310344828, 0.7073170731707317, 0.85, 0.7692307692307693, 1.0, 0.8666666666666667, 0.6666666666666666])
        print(mean_2dp(split_v1_alignment[0]))
        print(mean_2dp(split_v1_alignment[1]))

        print("split v2")
        split_v2_alignment = get_alignment_accuracies("split",False,2)
        # split_v2_alignment = ([0.85, 0.9090909090909091, 0.5903614457831325, 0.6842105263157895, 0.9090909090909091, 0.8333333333333334, 0.9090909090909091, 0.6428571428571429], [1.0, 0.8518518518518519, 0.6056338028169014, 0.6470588235294118, 0.9, 1.0, 0.9523809523809523, 0.7727272727272727])
        print(mean_2dp(split_v2_alignment[0]))
        print(mean_2dp(split_v2_alignment[1]))

        # number_aligns = len(v2_alignment[0])
        # print(sum(v2_alignment[0])/number_aligns, sum(v2_alignment[1])/number_aligns)
        # print(sum(split_v1_alignment[0])/number_aligns, sum(split_v1_alignment[1])/number_aligns)
        # print(sum(split_v2_alignment[0])/number_aligns, sum(split_v2_alignment[1])/number_aligns)
        # NOT WORKING
        # print("enhanced")
        # print(get_alignment_accuracies("enhanced",False,2))
    elif test_num == 7:
        print(get_alignment_accuracies("split", False, 2))
    elif test_num == 8:
        pass
        # print(get_results_for_traditional_files("logs/results_split_v2.txt","split"))
    elif test_num == 9:
        alignments = []
        test,train = test_train_split[0]
        split_train = get_splits(train,"enhanced")
        split_test =  get_splits(test,"enhanced")

        aligns = get_pred_align_test_2(split_train,split_train,True)
        alignments.extend(aligns)
        for i in range(10,20):
            print(" ".join(split_train[i][0]))
            print(" ".join(split_train[i][1]))
            print_alignment(alignments[i],split_train[i])
    elif test_num == 10:
        test,train = test_train_split[0]
        splits_test_norm = get_splits(test,"enhanced")
        splits_train_norm = get_splits(test,"enhanced")
        indexed = []
        for trans,pseud in test:
            trans = [(x,i) for i,x in enumerate(trans)]
            pseud = [(x,i) for i,x in enumerate(pseud)]
            indexed.append((trans,pseud))
        splits = get_splits(indexed,"enhanced_index")
        alignments = get_pred_align_test_2(splits_train_norm,splits_test_norm,True)
        new_alignments = []
        for split_pair,alignment in zip(splits,alignments):
            ts_split,ps_split = split_pair
            # transform alignment into original indecies:
            new_alignment = []
            for t_i,p_i in alignment:
                new_alignment.append((ts_split[t_i][1],ps_split[p_i][1]))
            new_alignments.append(new_alignment)


        # Combine the mappings
        combined_alignments = []
        start_alignment = 0
        for test_pair in test:
            num_splits = len(get_splits([test_pair], "enhanced"))
            comb_align = []
            for i in range(start_alignment,start_alignment+num_splits):
                comb_align.extend(new_alignments[i])
            combined_alignments.append(comb_align)
            start_alignment += num_splits

        for i,align in enumerate(combined_alignments):
            if i >= 8:
                break
            print(align)
            print_alignment_compare(align,i,test[i])
        recall = score_alignment_recall(combined_alignments)
        precision = score_alignment_precision(combined_alignments)
        print(recall)
        print(mean_2dp(recall))
        print(precision)
        print(mean_2dp(precision))


    elif test_num == 11:
        results = get_results_from_file("logs/results_enhanced_system_final.txt","enhanced")[0]
        # results = get_results_from_file_with_split("logs/results_enhanced_system_final.txt","enhanced")
        print(results)
        print(sum(results))
    elif test_num == 12:
        message = "Get Timings"
        print(message)
        write_to_log(message)
        split_v2_omega = 2.9
        results = get_timings(2.9, "split", False, 2)
        print(results)
    elif test_num == 13:
        message = "Get Timings enhanced"
        print(message)
        write_to_log(message)
        results = get_timings(2.6, "enhanced", True, 2)
        print(results)
    elif test_num == 14:
        test,train = test_train_split[8]
        test_pair = test[4]
        # print(test_pair)
        splits = get_splits([test_pair],"enhanced")
        # for split in splits:
        #     print(" ".join(split[0]))
        #     print(" ".join(split[1]))
        #     print()
    elif test_num == 15:
        results = get_results_from_file("logs/results_split_v2.txt","split")
        print(results)
        results = get_results_for_traditional_files("logs/results_split_v2.txt","split")
        print(results)
        print(sum(results[0]))
    else:
        # RESULTS
        log_result_files = os.listdir(get_path("logs"))
        log_result_files = [x for x in log_result_files if x.startswith("results") and not x.endswith("logs")]

        for filename in log_result_files:
            # if filename != "results_enhanced_new.txt":
            #     continue
            type_split = str(filename.split("_")[1])
            if "enhanced" in filename:
                type_split = "enhanced"
            elif "split" in filename:
                type_split = "split"
            else:
                type_split = "none"
            print(filename)
            results = get_results_from_file("logs/{}".format(filename),type_split)
            print(results[0])
            print(sum(results[0]))
            print()

        # print(get_results_from_file("logs/results_split_v2.txt","split"))
        # print(get_results_from_file("logs/results_enhanced_new.txt","enhanced"))
        # print(sum([191, 106, 165, 250, 112, 181, 78, 62, 134]))
        # TIMINGs
        # split v2
        # print(get_timings(2.9,"split",False,2))




