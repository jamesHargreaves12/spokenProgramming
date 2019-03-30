from data_prep_tools import get_data
from data_prep_tools.constants import base_dir

file_map = get_data.get_file_map("transcripts_var_replaced")

for current_dir in range(11, 17):
    print('')
    print("**************",current_dir)
    to_go_files = file_map[current_dir]
    while len(to_go_files) > 0:
        current_file_name = to_go_files.pop(0)
        print(current_file_name)
        input_filepath1 = base_dir + str(current_dir) + "/transcripts_var_replaced/" + current_file_name
        with open(input_filepath1, 'r+') as datafile:
            print(datafile.read())
        print()
        print()
        print()
