import os
from data_prep_tools.constants import base_dir_2

def get_data_from_directory(dir_name, base_dir_path=None):
    if not base_dir_path:
        print("Default path set")
        base_dir_path = base_dir_2
    data = []
    for i in range(1, 17):
        dir = base_dir_path + str(i) + dir_name
        input_files = os.listdir(dir)
        for filename in input_files:
            # if dir_name == "/transcripts_var_replaced/":
            #     print(len(data),i,filename)
            with open(dir + filename, "r") as in_file:
                data.append(in_file.read())
    return data


def get_file_map(dir_name,base=None):
    if not base:
        print("Default path set")
        base = base_dir_2
    file_map = {}
    for i in range(1, 17):
        dir = base + str(i)
        trans_files = os.listdir(dir + "/" + dir_name)
        file_map[i] = trans_files
    return file_map


