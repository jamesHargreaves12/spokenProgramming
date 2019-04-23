from smt import ibmmodel1, ibmmodel2
from smt.test_models import print_alignment
from tools.get_test_data import get_splits

alignments = [
    [(0,1),(1,0),(2,1),(3,2),(4,3),(5,4),(6,8),(7,5),(8,6),(9,7),(10,8),(11,9),(12,10),(13,11),(14,15),(15,12),(16,13),(17,14),(18,15),(19,16)],
    [(0,0),(1,1),(2,2),(3,2),(4,2),(5,3),(6,4),(7,5),(8,5),(9,5),(10,6),(10,7),(10,8),(11,9),(12,10),(13,12),(14,14),(15,13),(16,15),(17,18),(19,19),(20,20),(21,20),(22,20),(23,20),(24,23),(26,24),(27,26),(28,27),(30,29),(31,30),(36,31),(37,32)],
    [(4,0),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),(13,2),(16,3),(18,6),(21,9),(22,8),(24,7),(26,5),(27,5),(28,5),(29,4),(32,12),(38,13),(35,15),(36,14),(46,10),(40,11),(41,11),(42,11),(49,16),(53,17),(55,17),(56,17),(57,18),(51,19),(53,20),(55,20),(56,20),(57,21),(62,24),(63,25),(67,22),(68,26),(68,28),(69,27),(70,29),(71,30),(73,31),(74,32),(77,34),(78,34),(80,33),(76,35),(81,36),(82,36),(83,36),(85,39),(86,38),(87,38),(88,37),(92,42),(90,43),(93,41),(94,41),(97,43),(98,43),(100,46),(101,45),(102,45),(104,44),(106,48),(107,47),(108,49),(109,53),(111,52),(112,51),(113,51),(116,53),(117,53),(119,56),(120,55),(121,55),(123,54),(125,58),(126,57),(131,59),(132,60)],
    [(0,1),(5,0),(3,2),(4,2),(6,3),(9,4),(10,5),(11,6),(12,7),(13,8),(14,9,),(15,9),(16,9),(17,10),(18,11),(19,12),(21,13),(25,14),(26,15)],
    [(0,3),(1,2),(3,4),(5,1),(11,0),(13,5),(14,6),(15,7),(16,7),(17,8)],
    [(0,0),(1,1),(2,2),(3,2),(6,3),(8,4)],
    [(0,0),(1,1),(2,2),(4,3),(5,4),(8,5),(11,6),(12,7),(13,8),(15,9),(16,10),(17,11),(18,12),(19,12),(20,12),(21,13),(22,14),(23,15),(24,16),(26,17),(31,18),(33,19)],
    [(0,0),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,11),(13,11),(14,12),(15,13),(16,14),(17,15),(18,16),(19,17),(20,18),(21,19),(22,20),(23,21),(24,22),(25,23),(28,24),(29,25)],
]

# You pass in the predicted alignements for fold
# 1 and it give back the score for each of the methods
epoch = 100
null_flag = True

def get_pred_align_test_1(train,test,fm_flag=False):
    t_e_given_f,t_f_given_e = ibmmodel1.get_alignment_models_1(train, epoch, null_flag,fm_flag)
    return [ibmmodel1.get_phrase_alignment(t_e_given_f,t_f_given_e,fs,es,null_flag) for fs,es in test]


def get_pred_align_test_2(train,test,fm_flag):
    t_e_given_f, d_e_given_f, t_f_given_e, d_f_given_e = ibmmodel2.get_alignment_models_2(train,epoch,epoch,null_flag,fm_flag)
    return [ibmmodel2.get_phrase_alignment_2(t_e_given_f, d_e_given_f, t_f_given_e, d_f_given_e, fs, es, null_flag) for fs,es in test]


def check_if_closest_in_same_col(same_col,align,pred_alignment):
    if len(same_col) == 0:
        return False
    sorted_col = sorted(same_col)
    closest_left = sorted_col[0]
    closest_right = sorted_col[-1]
    if closest_left[0] < align[0]:
        # check free between
        issue = False
        for i in range(closest_left[0]+1, align[0]):
            if any([x for x in pred_alignment if x[0] == i]):
                issue = True
        if not issue:
            return True
    if closest_right[0] > align[0]:
        issue = False
        for i in range(align[0], closest_left[0]):
            if any([x for x in pred_alignment if x[0] == i]):
                issue = True
        if not issue:
            return True
    return False


def is_consistent(align, pred_alignment):
    same_row = [x for x in pred_alignment if x[0] == align[0]]
    same_col = [x for x in pred_alignment if x[1] == align[1]]
    if not any(same_row) and check_if_closest_in_same_col(same_col,align,pred_alignment):
        return True
    elif not any(same_col):
        invert_row = [(y,x) for x,y in same_row]
        invert_align = (align[1],align[0])
        invert_all = [(y,x) for x,y in pred_alignment]
        return check_if_closest_in_same_col(invert_row,invert_align,invert_all)
    return False

# print(is_consistent((0, 0), [(1, 0), (2, 1)]))
# print(is_consistent((0, 1), [(1, 0), (2, 1)]))
# print(is_consistent((2, 2), [(1, 0), (2, 1)]))
# print(is_consistent((1, 2), [(1, 0), (2, 1)]))

def score_alignment_recall(pred_aligns):
    results = []
    for i in range(len(alignments)):
        pred_align = pred_aligns[i]
        true_align = alignments[i]
        score = 0
        for pair in true_align:
            if pair in pred_align or is_consistent(pair,pred_align):
                score += 1
        results.append(score / len(true_align))
    return results


def score_alignment_precision(pred_aligns):
    results = []
    for i in range(len(alignments)):
        pred_align = pred_aligns[i]
        true_align = alignments[i]
        neg_score = 0
        consist = 0
        for pair in true_align:
            if pair not in pred_align:
                neg_score += 1
            elif  is_consistent(pair,pred_align):
                neg_score += 1
                consist += 1
        results.append((len(true_align) - neg_score) / (consist+len(pred_align)))
    return results


def combine_split_aligns(pred_aligns,test,split_test):
    result = []
    cur_test_index = 0
    prev_e_start = 0
    prev_f_start = 0
    current_alignment = []
    for i,split in enumerate(split_test):

        assert(prev_e_start + len(split[0]) <= len(test[cur_test_index][0]))
        # assert(prev_f_start + len(split[1]) <= len(test[cur_test_index][1]))
        current_alignment.extend([(e+prev_e_start,f+prev_f_start) for e,f in pred_aligns[i]])
        prev_e_start += len(split[0])
        prev_f_start += len(split[1])
        if prev_e_start == len(test[cur_test_index][0]):
            cur_test_index += 1
            result.append(current_alignment)
            current_alignment = []
            prev_e_start = 0
            prev_f_start = 0
    return result


def print_alignment_compare(pred_align,number,data_pair):
    print(number)
    true_align = alignments[number]
    print(" ".join(data_pair[0]))
    print(" ".join(data_pair[1]))
    es, fs= data_pair
    max_e = len(es)
    max_f = len(fs)
    print("    "+" ".join([f[0] for f in fs]))
    for i,e in enumerate(range(max_e)):
        print_str = str(i) + es[e][0]+" "
        if i < 10:
            print_str = " "+print_str
        for f in range(max_f):
            if (e,f) in true_align and \
                    ((e,f) in pred_align or is_consistent((e,f), pred_align)):
                print_str += "x "
            elif (e,f) in pred_align:
                print_str += "o "
            elif (e,f) in true_align:
                print_str += "0 "
            else:
                print_str += ". "
        print(print_str)

    # print_alignment(pred_aligns,data_pair)
    # print_alignment(alignments[number],data_pair)


