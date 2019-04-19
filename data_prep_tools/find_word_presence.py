from data_prep_tools.constants import base_dir_2, base_dir_1
from data_prep_tools import get_data
base = base_dir_2

def find_files(word):
    file_map = get_data.get_file_map("transcripts_var_replaced/",base)

    for i in range(1,17):
        for file in file_map[i]:
            with open(base + str(i) + "/transcripts_var_replaced/" + file, 'r') as data:
                text = data.read()
                if word in text:
                    print(str(i) +" - " + file)
                    print(text)

find_files("then")