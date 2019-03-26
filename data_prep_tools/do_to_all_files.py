import os
from data_prep_tools import get_data

base_dir = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"


def do_to_all_files(input_dir1, input_dir2, output_dir, transform):
    file_map = get_data.get_file_map(input_dir1)

    for current_dir in range(1, 17):
        print('')
        print(current_dir)
        to_go_files = file_map[current_dir]
        # print(to_go_files)
        output_path = base_dir + str(current_dir) + "/" + output_dir
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        while len(to_go_files) > 0:
            current_file_name = to_go_files.pop(0)
            print(current_file_name)
            input_filepath1 = base_dir + str(current_dir) + "/"+input_dir1+"/" + current_file_name
            with open(input_filepath1, 'r+') as datafile:
                data1 = datafile.read()
            if input_dir2 == None:
                updated = transform(data1)
            else:
                input_filepath2 = base_dir + str(current_dir) + "/" + input_dir2 + "/" + current_file_name
                with open(input_filepath2, 'r+') as datafile:
                    data2 = datafile.read()
                # print(data1)
                # print(data2)
                updated = transform(data1,data2)
            output_filepath = output_path+"/" + current_file_name
            with open(output_filepath, "w") as datafile:
                datafile.write(updated)

