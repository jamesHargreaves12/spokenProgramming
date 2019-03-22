from data_prep_tools.do_to_all_files import do_to_all_files
import re

def variable_transform(transcript_data, variable_data):
    variable_list:list = variable_data.split('\n')
    replace_text = "VARIABLE_"
    for index,variable in enumerate(variable_list):
        if variable == '':
            print("ISSUE")
            continue
        elif variable == '*********' and replace_text == "VARIABLE_":
            replace_text = "FUNCTION_CALL_"
            continue
        elif variable == '*********' and replace_text == "FUNCTION_CALL_":
            replace_text = "STR"
            continue
        elif variable == '*********':
            print("ISSUE")
        cur_replace_text = replace_text + str(index) if replace_text != "STR" else replace_text
        if variable == "\\n":
            transcript_data = re.sub(r'\\n',"STR",transcript_data)
        else:
            transcript_data = re.sub(r' '+variable+r'\s', " "+cur_replace_text+" ", transcript_data)
            transcript_data = re.sub(r' '+variable+r'$', " "+cur_replace_text, transcript_data)
            transcript_data = re.sub(r'^'+variable+r' ', cur_replace_text+" ", transcript_data)
            transcript_data = re.sub(r' ' + variable + r'\s', " " + cur_replace_text + " ", transcript_data)
            transcript_data = re.sub(r' ' + variable + r'$', " " + cur_replace_text, transcript_data)
            transcript_data = re.sub(r'^' + variable + r' ', cur_replace_text + " ", transcript_data)
    transcript_data = re.sub("empty string", "STR", transcript_data)
    return transcript_data


def number_transform(transcript_data):
    return re.sub(r' [0-9]+\.{0,1}[0-9]*'," NUMBER",transcript_data)


def remove_extra_white_space(transcript_data):
    return re.sub(r'  *',' ',transcript_data).strip(" ")


def overall_transform(transcript_data, variable_data):
    variables_replaced_transcripts = variable_transform(transcript_data, variable_data)
    return remove_extra_white_space(number_transform(variables_replaced_transcripts))

do_to_all_files(input_dir1='transcripts', input_dir2='variable_list', output_dir='transcripts_var_replaced', transform=overall_transform)
