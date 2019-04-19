import get_data
from get_classic_results import get_translations_from_file

# first set with_shuffle to false in get_data
from tools.minimum_edit_distance import minimum_edit_distance_per_token

translations = []
tr_train = get_translations_from_file("/results/traditional_train.txt")
tr_test1 = get_translations_from_file("/results/traditional_test1.txt")
tr_test2 = get_translations_from_file("/results/traditional_test2.txt")
translations.extend(tr_train + tr_test1 + tr_test2)
data = get_data.train_test_data + get_data.validation_set
results = []
for i, pair in enumerate(data):
    truth = pair[1]
    results.append(minimum_edit_distance_per_token(translations[i], truth))
results = results[len(tr_train):len(translations) - len(get_data.validation_set)]
print(sum(results)/len(results))