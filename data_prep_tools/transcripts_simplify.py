from data_prep_tools.do_to_all_files import do_to_all_files
import re

def variable_transform(transcript_data, variable_data):
    variable_list:list = variable_data.split('\n')
    replace_text = "VARIABLE_"
    for index,variable in enumerate(variable_list):
        if variable == '':
            print("ISSUE")
            continue
        elif variable == '*********':
            replace_text = "FUNCTION_CALL_"
            continue
        cur_replace_text = replace_text + str(index)
        transcript_data = re.sub(r' '+variable+r'\s', " "+cur_replace_text+" ", transcript_data)
        transcript_data = re.sub(r' '+variable+r'$', " "+cur_replace_text, transcript_data)
        transcript_data = re.sub(r'^'+variable+r' ', cur_replace_text+" ", transcript_data)
    return transcript_data


def number_transform(transcript_data):
    return re.sub(r' [0-9]+\.{0,1}[0-9]*'," NUMBER",transcript_data)


def remove_extra_white_space(transcript_data):
    return re.sub(r'  *',' ',transcript_data).strip(" ")


def overall_transform(transcript_data, variable_data):
    variables_replaced_transcripts = variable_transform(transcript_data, variable_data)
    return remove_extra_white_space(number_transform(variables_replaced_transcripts))

do_to_all_files(input_dir1='transcripts', input_dir2='variable_list', output_dir='transcripts_var_replaced', transform=overall_transform)
