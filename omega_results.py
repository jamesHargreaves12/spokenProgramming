from tools.find_resource_in_project import get_path
import re
import matplotlib.pyplot as plt

from tools.get_results_from_file import get_edit_distances_from_file

results_1 = [(0.5, 1019),(0.6,1019),(0.7,1019),(0.8,1016),(0.9,1015),(1.0, 1018),(1.1,1018),(1.2,1020),(1.5, 1020),(2.0, 1019),(2.5, 1019)]
results_2 = [(0.5, 706), (1.0, 706), (1.5, 706), (2.0, 701), (2.5, 698), (2.7, 698), (2.8, 698), (2.9, 698), (3.0, 698),
           (3.1, 698), (3.2, 698), (3.3, 699), (3.4, 699), (3.5, 697), (3.6, 697), (3.7, 697), (3.8, 702), (3.9, 702),
           (4.0, 702)]
enhanced = [(0.5, 370), (1.0, 385), (2.5, 371), (3.0, 371), (3.1, 371), (3.2, 371), (3.3, 372), (3.4, 372), (3.5, 372), (3.6, 372), (3.7, 372), (3.8, 374), (3.9, 374), (4.0, 374)] \
    + [(1.5, 374), (2.0, 373), (0.6, 370), (0.7, 371), (0.8, 375), (0.9, 384), (1.9, 374), (1.8, 375), (1.7, 374), (1.6, 374), (1.4, 383), (1.3, 384), (1.2, 384), (1.1, 385)] \
    + [(0.4, 370), (0.3, 379), (0.2, 382), (0.1, 387), (2.4, 368), (2.3, 368), (2.6, 371), (2.7, 371), (2.8, 371), (2.9, 371)] \
    + [(2.1, 373), (2.2, 373)]

split_v2 = [(0.5, 689), (1.0, 689), (1.5, 689)]


def get_translations(filename):
    predicts:dict = {}
    omega = -1
    # Edit distance = 1015
    # omega 1.1
    ed_re = re.compile(r"Edit distance = (\d+)\n")
    o_re = re.compile(r"omega ([0-9.]+)\n")
    pred_re = re.compile(r"predict: (.*)\n")
    omega_preds = []
    with open(get_path(filename), "r") as file:
        for line in file.readlines():
            if ed_re.match(line):
                ed = int(ed_re.match(line).group(1))
            elif o_re.match(line):
                if omega != -1:
                    predicts[omega] = omega_preds
                omega_preds = []
                omega = float(o_re.match(line).group(1))
            elif pred_re.match(line):
                pred = pred_re.match(line).group(1)
                omega_preds.append(pred)
            # print(line)
    predicts[omega] = omega_preds
    return predicts




# print(get_edit_distances("logs/omega-v2.txt"))

# trans = get_translations("/logs/omega_enhanced.txt")
# file_trans = defaultdict(list)
# omegas = [k for k in trans]
# for k in trans:
#     for i,pseud in enumerate(trans[k]):
#         file_trans[i].append(pseud)
#
# eds = defaultdict(list)
# average = []
# for i,pair in enumerate(validation_set):
#     _,real = pair
#     preds = file_trans[i]
#     total = 0
#     for j,pred in enumerate(preds):
#         tokenized_pred = pred.strip('\n').split(" ")
#         ed = minimum_edit_distance(tokenized_pred, real)
#         total += ed
#         eds[omegas[j]].append(ed)
#     average.append(total/len(preds))
#
# for omega in omegas:
#     points = [eds[omega][i] - average[i] for i in range(14)]
#     plt.plot(points,'-',linestyle='dashed')
# plt.show()
#


def show_results(eds, with_invert_y=False):
    eds = sorted(eds)
    print(eds)
    xs = [x for x,_ in eds]
    ys = [y for _,y in eds]
    plt.plot(xs, ys)
    if with_invert_y:
        plt.gca().invert_yaxis()
    plt.xlabel('ω')
    plt.ylabel('Sum minimum edit distance')
    plt.title('Minimum edit distance at different values of ω')
    plt.show()


enhanced = get_edit_distances_from_file("logs/omega_enhanced.txt")
enhanced.extend(get_edit_distances_from_file("logs/omega_enhanced_2.txt"))
enhanced.extend(get_edit_distances_from_file("logs/omega_enhanced_3.txt"))
enhanced.extend(get_edit_distances_from_file("logs/omega_enhanced_4.txt"))
# enhanced omega = 2.4

splits_v1 = get_edit_distances_from_file("logs/omega_split_v1.txt")
splits_v1.extend(get_edit_distances_from_file("logs/omega_split_v1_2.txt"))
# show_results(splits_v1)
# split_v1_omega = 1.5

splits_v2 = get_edit_distances_from_file("logs/omega_split_v2.txt")
splits_v2.extend(get_edit_distances_from_file("logs/omega_split_v2_2.txt"))
splits_v2.extend(get_edit_distances_from_file("logs/omega_split_v2_3.txt"))
# split_v2_omega = 2.9
# show_results(splits_v2)

v1 = get_edit_distances_from_file("logs/omega_v1.txt")
v1.extend(get_edit_distances_from_file("logs/omega_v1_2.txt"))
show_results(v1)

v2 = get_edit_distances_from_file("logs/omega_v2_3.txt")
v2.extend(get_edit_distances_from_file("logs/omega_v2.txt"))
v2.extend(get_edit_distances_from_file("logs/omega_v2_2.txt"))
# show_results(v2)
# v2_omega = 2.0

enhanced_2 = get_edit_distances_from_file("logs/omega_new_enhanced.txt")
enhanced_2.extend(get_edit_distances_from_file("logs/omega_new_enhanced_2.txt"))
enhanced_2.extend(get_edit_distances_from_file("logs/omega_new_enhanced_3.txt"))
# show_results(enhanced_2)
# enhanced_2_omega = 2.6
