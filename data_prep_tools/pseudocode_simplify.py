from data_prep_tools.do_to_all_files import do_to_all_files
import re
from pseudocode_lang_1 import pseudo_yacc

def simplified_output(tree):
    label = tree[0]
    # print(tree)
    if label == "STATEMENTS":
        output = ""
        for x in tree[1]:
            output += simplified_output(x) + " "
        return output

    elif label == "STATEMENT1":
        if tree[1] == "continue":
            return "continue "
        return simplified_output(tree[1])

    elif label == "RETURN":
        return "return " + simplified_output(tree[1]) + " "

    elif label == "FOR IN":
        expr = simplified_output(tree[2])
        block = simplified_output(tree[3])
        return "for VARIABLE in " + expr + " " + block

    elif label == "FOR":
        exp1 = simplified_output(tree[1]) + " "
        exp2 = simplified_output(tree[2]) + " "
        exp3 = simplified_output(tree[3]) + " "
        block = simplified_output(tree[4]) + " "
        return "for " + exp1 + exp2 + exp3 + block

    elif label == "WHILE":
        exp = simplified_output(tree[1])
        block = simplified_output(tree[2])
        return "while " + exp + " " + block

    elif label == "IF":
        exp = simplified_output(tree[1])
        block = simplified_output(tree[2])
        return "if " + exp + " " + block

    elif label == "IF_ELSE":
        exp = simplified_output(tree[1])
        block = simplified_output(tree[2])
        rest = simplified_output(tree[3])
        return "if " + exp + " " + block + " " +rest

    elif label == "ELSE_IF":
        exp = simplified_output(tree[1])
        block = simplified_output(tree[2])
        rest = simplified_output(tree[3])
        return "else if " + exp + " " + block + " " +rest

    elif label == "ELSE":
        return "else " + simplified_output(tree[1]) + " "

    elif label == "ELSE_IF_ONLY":
        exp = simplified_output(tree[1])
        block = simplified_output(tree[2])
        return "else if " + exp + " " + block

    elif label == "BLOCK":
        return simplified_output(tree[1])

    elif label == "FUNC":
        if tree[2] == ():
            return "FUNCTION_CALL"
        args = simplified_output(tree[2])
        return "FUNCTION_CALL " + args

    elif label == "ARG_LIST":
        output = ""
        for x in tree[1]:
            output += simplified_output(x) + " "
        return output

    elif label == "STATEMENT2":
        lhs = simplified_output(tree[2])
        rhs = simplified_output(tree[3])
        op_toks = " ".join([x for x in tree[1]])
        return lhs + " " + op_toks + " " + rhs

    elif label == "EXPRESSION":
        left = simplified_output(tree[2])
        right = simplified_output(tree[3])
        return left + " " + tree[1] + " " + right

    elif label == "METHOD_CALL":
        exp = simplified_output(tree[1])
        func = simplified_output(tree[2])
        return exp + " . " + func

    elif label == "INDEX":
        exp1 = simplified_output(tree[1])
        exp2 = simplified_output(tree[2])
        return exp1 + " index " + exp2

    elif label == "UNARY":
        if tree[1] in ["++","--","-"]:
            tokenized_op = " ".join([x for x in tree[1]])
            return tokenized_op + " " + simplified_output(tree[2])
        else:
            tokenized_op = " ".join([x for x in tree[2]])
            return simplified_output(tree[1]) + " " + tokenized_op

    elif label == "SUBLIST":
        exp1 = simplified_output(tree[1])
        exp2 = simplified_output(tree[2])
        exp3 = simplified_output(tree[3])
        return exp1 + " [ " + exp2 + " : " + exp3 + " ]"

    elif label == "BRAKET_VAL":
        exp1 = simplified_output(tree[1])
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
            return simplified_output(data)
        else:
            return "VARIABLE"

    else:
        print("Label not recognised: " + label)


def transform(pseudocode):
    parser = pseudo_yacc.parser
    parsed = parser.parse(pseudocode)
    return simplified_output(parsed)


do_to_all_files(input_dir1='pseudocode', input_dir2=None, output_dir='pseudocode_simplified', transform=transform)