import re
from collections import defaultdict
import matplotlib.pyplot as plt

results_1 = [(0.5, 1019),(0.6,1019),(0.7,1019),(0.8,1016),(0.9,1015),(1.0, 1018),(1.1,1018),(1.2,1020),(1.5, 1020),(2.0, 1019),(2.5, 1019)]
results_2 = [(0.5, 706), (1.0, 706), (1.5, 706), (2.0, 701), (2.5, 698), (2.7, 698), (2.8, 698), (2.9, 698), (3.0, 698),
           (3.1, 698), (3.2, 698), (3.3, 699), (3.4, 699), (3.5, 697), (3.6, 697), (3.7, 697), (3.8, 702), (3.9, 702),
           (4.0, 702)]

xs = [x for x,_ in results_2]
ys = [y for _,y in results_2]
plt.plot(xs, ys)
plt.xlabel('ω')
plt.ylabel('Sum minimum edit distance')
plt.title('Minimum edit distance at different values of ω')
plt.show()


# minimum edit distance / length of
from get_data import validation_set
from tools.find_resource_in_project import get_path
from tools.minimum_edit_distance import minimum_edit_distance


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

trans = get_translations("/logs/omega-v1.txt")
file_trans = defaultdict(list)
omegas = [k for k in trans]
for k in trans:
    for i,pseud in enumerate(trans[k]):
        file_trans[i].append(pseud)

eds = defaultdict(list)
average = []
for i,pair in enumerate(validation_set):
    _,real = pair
    preds = file_trans[i]
    total = 0
    for j,pred in enumerate(preds):
        tokenized_pred = pred.strip('\n').split(" ")
        ed = minimum_edit_distance(tokenized_pred, real)
        total += ed
        eds[omegas[j]].append(ed)
    average.append(total/len(preds))

for omega in omegas:
    points = [eds[omega][i] - average[i] for i in range(14)]
    plt.plot(points,'-',linestyle='dashed')
plt.show()



