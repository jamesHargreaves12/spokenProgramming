from data_prep_tools.get_data import get_data_from_directory

pseudocode = get_data_from_directory("/pseudocode_simplified/")
transcriptions = get_data_from_directory("/transcripts_var_replaced/")
# max_diff = len(transcriptions[0].split(" "))/len(pseudocode[0].split(" "))
var = 0
count = 0
max_length = 0

max_data = ""
keywords = ["if", "while", "else", "return", "for", "and", "or"]
for data in transcriptions:
    a = data.split(" ")
    split_up = []
    current = []
    for x in a:
        if x in keywords:
            if current:
                split_up.append(current)
                if len(current) > max_length:
                    max_length = len(current)
                    max_data = current
            current = [x]
        else:
            current.append(x)
    split_up.append(current)

    # print(" ".join(split_up[0]))
    # print()
    #




print(max_length)
print(max_data)
print(count)
