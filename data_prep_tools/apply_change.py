import re
from pseudocode_lang_1 import pseudo_yacc
from data_prep_tools import get_data

base_dir = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"
file_map = {}
replacements = {"one hundred": "100",
                "one": "1",
                "two": "2",
                "three": "3",
                "four": "4",
                "five": "5",
                "six": "6",
                "seven": "7",
                "eight": "8",
                "nine": "9",
                "nought": "0",
                "naught": "0",
                "eleven": "11",
                "zero": "0"}
# replace 4 point 5 by 4.5
# replacements = {r"([0-9]+?) point ([0-9]+?)" : r"\1.\2"}
# remove punctuation
# replacements = {r"([^0-9])\." : r"\1"}
# replacements = {r"\.([^0-9])" : r"\1"}
# replacements = {r"\.$" : r""}
# replacements = {r"\.([^0-9])" : r"\1"}
# replacements = {"twenty 1": "21"}
# replacements = {r"(([a-z_]+)?)\.append\(((.*)?)\)": r"append(\3,\2)"}
# replacements = {r" ([a-z]?)th ":r" \1 th "}

file_map = get_data.get_file_map("transcripts")

for current_dir in range(1, 17):
    print('')
    print(current_dir)
    to_go_files = file_map[current_dir]
    current_file_name = ""

    while len(to_go_files) > 0:
        current_file_name = to_go_files.pop(0)
        print(current_file_name)
        filepath = base_dir + str(current_dir) + "/transcripts/" + current_file_name
        with open(filepath, 'r+') as datafile:
            data = datafile.read()
        updated = data
        for exp in replacements.keys():
            updated = re.sub(exp, replacements[exp],updated)
        if "pseudocode" in filepath and pseudo_yacc.get_errors(updated):
            print(updated)
            print("ISSUE")
        else:
            with open(filepath, "w") as datafile:
                datafile.write(updated.lower())

