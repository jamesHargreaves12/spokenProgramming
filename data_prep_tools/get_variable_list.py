from pseudocode_lang_1 import pseudo_lex
from data_prep_tools.do_to_all_files import do_to_all_files
base_dir = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"


def transform(data):
    pseudo_lex.lexer.input(data)
    variable_list = []
    fun_list = []
    tok = pseudo_lex.lexer.token()
    while True:
        if not tok:
            break
        if tok.type == "ID":
            var = tok.value.replace("_", " ")
            next_tok = pseudo_lex.lexer.token()
            if next_tok.type == "OPEN_BRACKET":
                if var not in fun_list:
                    fun_list.append(var)
            else:
                if var not in variable_list:
                    variable_list.append(var)
            tok = next_tok
        else:
            tok = pseudo_lex.lexer.token()
    variable_list = sorted(variable_list,key=lambda variable: len(variable),reverse=True)
    return "\n".join(variable_list) + '\n*********\n' + '\n'.join(fun_list)

do_to_all_files(input_dir1="pseudocode", input_dir2=None, output_dir="variable_list", transform=transform)