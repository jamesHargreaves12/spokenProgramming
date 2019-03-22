import os
base_dir = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData_2/"

def get_data_from_directory(dir_name, base_dir_path=None):
    if not base_dir_path:
        base_dir_path = base_dir
    data = []
    for i in range(1, 17):
        print(i)
        dir = base_dir_path + str(i) + dir_name
        input_files = os.listdir(dir)
        for filename in input_files:
            print(filename)
            with open(dir + filename, "r") as in_file:
                data.append(in_file.read())
    return data

def get_file_map(dir_name,base=None):
    if not base:
        base = base_dir
    file_map = {}
    for i in range(1, 17):
        dir = base + str(i)
        trans_files = os.listdir(dir + "/" + dir_name)
        file_map[i] = trans_files
    return file_map


