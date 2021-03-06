from pseudocode_lang_1 import pseudo_lex
from data_prep_tools.do_to_all_files import do_to_all_files
from data_prep_tools.constants import base_dir_1


def transform(data):
    pseudo_lex.lexer.input(data)
    variable_list = []
    fun_list = []
    str_list = []
    tok = pseudo_lex.lexer.token()
    while True:
        if not tok:
            break
        if tok.type == "ID":
            var = tok.value.replace("_", " ")
            next_tok = pseudo_lex.lexer.token()
            if next_tok and next_tok.type == "OPEN_BRACKET":
                if var not in fun_list:
                    fun_list.append(var)
            else:
                if var not in variable_list:
                    variable_list.append(var)
            tok = next_tok
        elif tok.type == "STRING_CONST":
            var = tok.value.replace("\"","")
            if var not in str_list:
                str_list.append(var)
            tok = pseudo_lex.lexer.token()
        else:
            tok = pseudo_lex.lexer.token()
    variable_list = sorted(variable_list,key=lambda variable: len(variable),reverse=True)
    if str_list:
        print(str_list)
    overall = variable_list + ["*********"] +fun_list + ["*********"]+str_list
    return "\n".join(overall)
    # if fun_list:
    #     return "\n".join(variable_list) + '\n*********\n' + '\n'.join(fun_list)
    # else :
    #     return "\n".join(variable_list)+ '\n*********'

do_to_all_files(input_dir1="pseudocode", input_dir2=None, output_dir="variable_list", transform=transform)