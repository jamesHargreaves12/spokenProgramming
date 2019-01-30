from data_prep_tools.do_to_all_files import do_to_all_files

import re
from pseudocode_lang_1 import pseudo_yacc

def simplified_output(tree, variable_list):
    label = tree[0]
    # print(tree)
    if label == "STATEMENTS":
        output = ""
        for x in tree[1]:
            output += simplified_output(x,variable_list) + " "
        return output

    elif label == "STATEMENT1":
        if tree[1] == "continue":
            return "continue "
        return simplified_output(tree[1],variable_list)

    elif label == "RETURN":
        return "return " + simplified_output(tree[1],variable_list) + " "

    elif label == "FOR IN":
        expr = simplified_output(tree[2],variable_list)
        block = simplified_output(tree[3],variable_list)
        return "for VARIABLE in " + expr + " " + block

    elif label == "FOR":
        exp1 = simplified_output(tree[1],variable_list) + " "
        exp2 = simplified_output(tree[2],variable_list) + " "
        exp3 = simplified_output(tree[3],variable_list) + " "
        block = simplified_output(tree[4],variable_list) + " "
        return "for " + exp1 + exp2 + exp3 + block

    elif label == "WHILE":
        exp = simplified_output(tree[1], variable_list)
        block = simplified_output(tree[2],variable_list)
        return "while " + exp + " " + block

    elif label == "IF":
        exp = simplified_output(tree[1],variable_list)
        block = simplified_output(tree[2],variable_list)
        return "if " + exp + " " + block

    elif label == "IF_ELSE":
        exp = simplified_output(tree[1],variable_list)
        block = simplified_output(tree[2],variable_list)
        rest = simplified_output(tree[3],variable_list)
        return "if " + exp + " " + block + " " +rest

    elif label == "ELSE_IF":
        exp = simplified_output(tree[1],variable_list)
        block = simplified_output(tree[2],variable_list)
        rest = simplified_output(tree[3],variable_list)
        return "else if " + exp + " " + block + " " +rest

    elif label == "ELSE":
        return "else " + simplified_output(tree[1],variable_list) + " "

    elif label == "ELSE_IF_ONLY":
        exp = simplified_output(tree[1],variable_list)
        block = simplified_output(tree[2],variable_list)
        return "else if " + exp + " " + block

    elif label == "BLOCK":
        return simplified_output(tree[1],variable_list)

    elif label == "FUNC":
        function_num = variable_list.index(tree[1])
        function_name = "FUNCTION_CALL_" + str(function_num)
        if tree[2] == ():
            return function_name
        args = simplified_output(tree[2],variable_list)
        return function_name + " " + args

    elif label == "ARG_LIST":
        output = ""
        for x in tree[1]:
            output += simplified_output(x,variable_list) + " "
        return output

    elif label == "STATEMENT2":
        lhs = simplified_output(tree[2],variable_list)
        rhs = simplified_output(tree[3],variable_list)
        op_toks = " ".join([x for x in tree[1]])
        return lhs + " " + op_toks + " " + rhs

    elif label == "EXPRESSION":
        left = simplified_output(tree[2],variable_list)
        right = simplified_output(tree[3],variable_list)
        return left + " " + tree[1] + " " + right

    elif label == "METHOD_CALL":
        exp = simplified_output(tree[1],variable_list)
        func = simplified_output(tree[2],variable_list)
        return exp + " . " + func

    elif label == "INDEX":
        exp1 = simplified_output(tree[1],variable_list)
        exp2 = simplified_output(tree[2],variable_list)
        return exp1 + " index " + exp2

    elif label == "UNARY":
        if tree[1] in ["++","--","-"]:
            tokenized_op = " ".join([x for x in tree[1]])
            return tokenized_op + " " + simplified_output(tree[2],variable_list)
        else:
            tokenized_op = " ".join([x for x in tree[2]])
            return simplified_output(tree[1],variable_list) + " " + tokenized_op

    elif label == "SUBLIST":
        exp1 = simplified_output(tree[1],variable_list)
        exp2 = simplified_output(tree[2],variable_list)
        exp3 = simplified_output(tree[3],variable_list)
        return exp1 + " sublist " + exp2 + " : " + exp3

    elif label == "BRAKET_VAL":
        exp1 = simplified_output(tree[1],variable_list)
        return "( " + exp1 + " )"

    elif label == "VAL":
        data = tree[1]
        if str(data) in ["true", "false"]:
            return str(data)
        elif str(data) == "[]":
            return "EMPTY_LIST"
        elif str(data) == "\"\\n\"":
            return "NEWLINE"
        elif re.match("^\".*\"$",str(data)):
            return "STRING_CONST"
        elif re.match("^[0-9]+.{0,1}[0-9]*$",str(data)):
            return "NUMBER"
        elif data[0] == "FUNC":
            return simplified_output(data,variable_list)
        else:
            variable_num = variable_list.index(data)
            return "VARIABLE_" + str(variable_num)

    else:
        print("Label not recognised: " + label)


def transform(pseudocode,variable_data):
    variable_list:list = [x.replace(" ", "_") for x in variable_data.split('\n')]
    parser = pseudo_yacc.parser
    parsed = parser.parse(pseudocode)
    return simplified_output(parsed,variable_list)


do_to_all_files(input_dir1='pseudocode', input_dir2='variable_list', output_dir='pseudocode_simplified', transform=transform)