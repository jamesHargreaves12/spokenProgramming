from data_prep_tools import get_data


def find_files(word):
    base_dir = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"
    file_map = get_data.get_file_map("/pseudocode_simplified/")

    for i in range(1,17):
        for file in file_map[i]:
            with open(base_dir+str(i)+"/pseudocode_simplified/"+file,'r') as data:
                if word in data.read():
                    print(str(i) +" - " + file)

find_files("Issue")