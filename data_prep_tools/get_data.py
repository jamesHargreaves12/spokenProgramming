import os
base_dir = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"

def get_data_from_directory(dir_name):
    data = []
    for i in range(1, 17):
        dir = base_dir + str(i) + dir_name
        input_files = os.listdir(dir)
        for filename in input_files:
            with open(dir + filename, "r") as in_file:
                data.append(in_file.read())
    return data

def get_file_map(dir_name):
    file_map = {}
    for i in range(1, 17):
        dir = base_dir + str(i)
        trans_files = os.listdir(dir + "/" + dir_name)
        file_map[i] = trans_files
    return file_map


