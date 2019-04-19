import datetime
import gc
import matplotlib.pyplot as plt

from baseline import baseline_functions
from data_prep_tools.constants import base_dir_2, base_dir_1
from generate_folds import RANDOM_SHUFFLE_ORDER
from get_baseline_results import total_edit_distance_baseline
from get_data import sentence_pair_folds, train_test_split, split_data
from other.get_wav_duration import get_audio_lengths_of_fold_1
from smt import smt_functions, decoder_with_log
import time

from test1 import total_edit_distance_smt
from tools.find_resource_in_project import get_path
from traditional_MT import load_dep_parse
from traditional_MT.graph_to_expression import get_output_string

def combine_split_times(test,split_test,split_times):
    cur_length = 0
    cur_index = 0
    count = 0
    data_to_num_splits = []
    for i, split in enumerate(split_test):
        cur_length += len(split[0])
        count += 1
        if cur_length == len(test[cur_index][0]):
            data_to_num_splits.append(count)
            print(count)
            count = 0
            cur_index += 1
            cur_length = 0

    fold_times = []
    start_index = 0
    for num_splits in data_to_num_splits:
        fold_times.append(sum(split_times[start_index:start_index+num_splits]))
        start_index += num_splits
    return fold_times

def baseline_time(train,test,stem,threshold):
    lang_model = smt_functions.get_language_model(train, 1)
    pseudocode_tokens = baseline_functions.get_pseudocode_tokens(train)
    results = []
    for trans,pseudo in test:
        start = time.time()
        prediction = baseline_functions.get_output_baseline(trans,lang_model,pseudocode_tokens,stem,threshold)
        end = time.time()
        results.append(end-start)
    return results


def traditional_time():
    toks1,deps1 = load_dep_parse.get_token_deps(base_dir_2)
    toks2,deps2 = load_dep_parse.get_token_deps(base_dir_1)
    toks = toks1 + toks2
    deps = deps1 + deps2

    pairs = [x for x in zip(toks,deps)]
    fold_indecies = RANDOM_SHUFFLE_ORDER[:15]
    fold_pairs = []
    for i in fold_indecies:
        fold_pairs.append(pairs[i])
    results = []
    for tok,dep in fold_pairs:
        start = time.time()
        get_output_string(tok,dep)
        end = time.time()
        results.append(end-start)
    return results


def smt_time(test,train,ibmmodel1_flag,split_flag,alpha,omega):
    if split_flag:
        og_test = test
        test = split_data(test)
        train = split_data(train)
    n = 2
    epoch = 100
    null_flag = True
    if ibmmodel1_flag:
        alignments = smt_functions.get_alignment_1(train, epoch, null_flag)
        log_phrase_table = smt_functions.get_log_phrase_table1(train, alignments)
    else:
        alignments = smt_functions.get_alignment_2(train, epoch, null_flag)
        log_phrase_table = smt_functions.get_log_phrase_table2(train, alignments)

    lang_model = smt_functions.get_language_model(train, n)
    decoder_with_log.set_alpha(alpha)
    decoder_with_log.set_omega(omega)
    results = []
    for trans,pseudo in test:
        gc.collect()
        start = time.time()
        smt_functions.run_smt(lang_model,log_phrase_table,trans)
        end = time.time()
        results.append(end-start)
    if split_flag:
        return combine_split_times(og_test,test,results)
    return results


if __name__ == "__main__":
    test,train = train_test_split[0]
    # audio = get_audio_lengths_of_fold_1()
    audio = [13.704, 26.04, 56.616, 23.304, 16.896, 7.056, 16.344, 28.416, 31.584, 23.424, 26.544, 25.464, 21.024, 45.576,
     41.064]
    # baseline_stem = baseline_time(train,test,True,0)
    baseline_stem = [0.06007099151611328, 0.12194108963012695, 0.4350569248199463, 0.08037281036376953, 0.06321883201599121, 0.02895498275756836, 0.11785292625427246, 0.10208487510681152, 0.2236180305480957, 0.12479090690612793, 0.07775068283081055, 0.11345219612121582, 0.09642815589904785, 0.17246103286743164, 0.09328484535217285]
    # baseline_no_stem = baseline_time(train,test,False,0)
    baseline_no_stem = [0.001361846923828125, 0.0024738311767578125, 0.008814096450805664, 0.0016789436340332031, 0.0012009143829345703, 0.0005979537963867188, 0.0022699832916259766, 0.0019588470458984375, 0.004804134368896484, 0.0024030208587646484, 0.0016658306121826172, 0.0018680095672607422, 0.0017819404602050781, 0.003376007080078125, 0.0019350051879882812]
    # traditional = traditional_time()
    # we already have the dependency parse and so this is not included
    traditional = [0.015233755111694336, 0.009486198425292969, 0.0027048587799072266, 0.005510091781616211, 0.0028429031372070312, 0.007013082504272461, 0.003701925277709961, 0.007691860198974609, 0.013170957565307617, 0.003656148910522461, 0.009801149368286133, 0.004567146301269531, 0.0028798580169677734, 0.00829315185546875, 0.01567697525024414]
    # smt_1 = smt_time(test, train, True, False, alpha=0.7788829380260138, omega=0.9)
    smt_1 = [133.9984257221222, 469.1988637447357, 3190.638761997223, 175.3460669517517, 37.73295307159424, 14.284887075424194, 300.72114872932434, 387.34864807128906, 982.5837571620941, 494.37969613075256, 302.1599192619324, 285.2865889072418, 164.053218126297, 727.2064180374146, 353.56832098960876]
    # smt_2 = smt_time(test, train, False, False, alpha = 0.7042902967121091,omega = 3.5)
    smt_2 = [22.835576057434082, 79.31231594085693, 1300.957997083664, 36.37908887863159, 13.581125020980835, 2.702191114425659, 70.38090085983276, 87.75209426879883, 359.158814907074, 95.65740084648132, 37.54171586036682, 60.851832151412964, 34.308842182159424, 159.02343678474426, 55.525102853775024]
    # smt_1_split = smt_time(test, train, True, True, alpha=0.4725864123957092, omega=2.6)
    smt_1_split = [76.87348985671997, 39.296112298965454, 558.2528364658356, 18.059808015823364, 7.628370046615601, 5.972321033477783, 121.08550596237183, 114.69073033332825, 158.06545877456665, 64.74805784225464, 103.75315809249878, 137.8399097919464, 104.65644383430481, 28.25788402557373, 58.58047103881836]
    # smt_2_split = smt_time(test, train, False, True, alpha=0.5451790111763591, omega=1.5)
    smt_2_split = [23.158511877059937, 25.333509922027588, 307.3691668510437, 7.515406370162964, 4.804509878158569, 5.002076864242554, 68.1297538280487, 20.917881965637207, 108.29013180732727, 25.596248149871826, 43.38949918746948, 33.2870614528656, 45.14101314544678, 15.725060224533081, 48.54063177108765]

    plt.plot(audio,label="audio")
    plt.plot(baseline_stem,label="baseline+stem")
    # plt.plot(baseline_no_stem,label="baseline")
    plt.plot(traditional,label = 'traditional')
    # plt.plot(smt_1,label = 'smt_v1')
    # plt.plot(smt_2,label = 'smt_v2')
    # plt.plot(smt_1_split,label = 'split_1')
    plt.plot(smt_2_split,label = 'split_2')
    plt.yscale('log')
    plt.legend()
    plt.show()


