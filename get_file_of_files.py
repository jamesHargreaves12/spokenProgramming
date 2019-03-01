from data_prep_tools import get_data

# files = get_data.get_data_from_directory("/transcripts/")
# with open("/Users/james_hargreaves/Documents/ThirdYear/transcripts.txt","w+") as write_file:
#     for file in files:
#         write_file.write(file.replace('\n',''))
#         write_file.write('\n')
#
#
# files = get_data.get_data_from_directory("/transcripts_var_replaced/")
# with open("/Users/james_hargreaves/Documents/ThirdYear/transcripts_replaced.txt","w+") as write_file:
#     for file in files:
#         write_file.write(file.replace('\n',''))
#         write_file.write('\n')

files = get_data.get_data_from_directory("/pseudocode/")
with open("/Users/james_hargreaves/Documents/ThirdYear/pseudocode.txt","w+") as write_file:
    for file in files:
        write_file.write(file.replace('\n',''))
        write_file.write('\n')

files = get_data.get_data_from_directory("/pseudocode_simplified/")
with open("/Users/james_hargreaves/Documents/ThirdYear/pseudocode_simplified.txt","w+") as write_file:
    for file in files:
        write_file.write(file.replace('\n',''))
        write_file.write('\n')