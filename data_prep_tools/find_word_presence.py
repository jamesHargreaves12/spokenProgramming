from data_prep_tools.constants import base_dir_2, base_dir_1
from data_prep_tools import get_data
base = base_dir_1

def find_files(word):
    file_map = get_data.get_file_map("pseudocode_simplified/",base)

    for i in range(1,17):
        for file in file_map[i]:
            with open(base + str(i) + "/pseudocode_simplified/" + file, 'r') as data:
                if word in data.read():
                    print(str(i) +" - " + file)

find_files("for VARIABLE_")
