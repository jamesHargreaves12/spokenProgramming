from get_data import train_test_split, split_data, validation_set

# split_validation = split_data(validation_set)
# for _,pseud in split_validation:
#     print(" ".join(pseud))

test,train = train_test_split[0]
split_test = split_data(test)
cur_length = 0
cur_index = 0
count = 0
data_to_num_splits = []
for i,split in enumerate(split_test):
    cur_length += len(split[0])
    count += 1
    if cur_length == len(test[cur_index][0]):
        data_to_num_splits.append(count)
        print(count)
        count = 0
        cur_index += 1
        cur_length = 0
    # assert(cur_length <= len(test[cur_index]))
# print(result)
# print(len(result))
smt_1_split = [23.158511877059937, 17.928679943084717, 7.093222141265869, 0.2992420196533203, 0.01236581802368164, 161.66583585739136, 0.4742918014526367, 145.21631121635437, 0.012727975845336914, 0.13468217849731445, 0.19139885902404785, 7.174773216247559, 0.014552116394042969, 4.141145944595337, 0.6633639335632324, 5.002076864242554, 68.05002403259277, 0.07972979545593262, 4.886976957321167, 16.03090500831604, 38.760308027267456, 21.868879795074463, 47.66094398498535, 0.5053720474243164, 13.756984949111938, 11.322916030883789, 0.010975122451782227, 43.38949918746948, 33.274548292160034, 0.012513160705566406, 45.14101314544678, 0.7718138694763184, 0.015434026718139648, 0.46886110305786133, 0.016488313674926758, 10.215588808059692, 3.918661117553711, 0.3053169250488281, 0.012896060943603516, 45.88708472251892, 2.6535470485687256]
fold_times = []
start_index = 0
for num_splits in data_to_num_splits:
    fold_times.append(sum(smt_1_split[start_index:start_index+num_splits]))
    start_index += num_splits
print(fold_times)
