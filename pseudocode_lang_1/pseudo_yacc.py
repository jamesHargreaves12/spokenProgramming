from pseudocode_lang_1 import pseudo_lex
import os
import ply.yacc as yacc
from data_prep_tools.constants import base_dir_2

tokens = pseudo_lex.tokens
lexer = pseudo_lex.lexer
# PROBS wanna lable all the tuples if using


string_input = ""
with open(base_dir_2 + "1/pseudocode/329759.txt", "r") as file:
    string_input = file.read()


def p_file(p):
    '''
    statements : statements statement
    '''
    x = p[1][1]
    x.append(p[2])
    p[0] = ("STATEMENTS",x)
    # print(p[0])

def p_file2(p):
    '''statements :
    '''
    p[0] = ("STATEMENTS",[])

def p_statement1(p):
    '''
    statement : expression END_STMT
              | return_state END_STMT
              | if_state
              | if_else_state
              | while_state
              | for_state
              | CONTINUE END_STMT
    '''
    p[0] = ("STATEMENT1",p[1])

def p_statement2(p):
    '''
    statement : expression ASSIGN expression END_STMT
              | expression ADD_ASSIGN expression END_STMT
              | expression MINUS_ASSIGN expression END_STMT
              | expression DIVIDE_ASSIGN expression END_STMT
              | expression MULT_ASSIGN expression END_STMT
              | expression AND_ASSIGN expression END_STMT
    '''
    p[0] = ("STATEMENT2",p[2],p[1],p[3])

def p_statement3(p):
    '''
    return_state : RETURN expression
    '''
    p[0] = ("RETURN",p[2])

def p_for_state1(p):
    '''
    for_state : FOR ID IN expression block
    '''
    p[0] = ("FOR IN",p[2],p[4],p[5])

def p_for_state2(p):
    '''
    for_state : FOR statement statement statement block
    '''
    p[0] = ("FOR",p[2],p[3],p[4],p[5])

def p_while_state1(p):
    '''
    while_state : WHILE expression block
    '''
    p[0] = ("WHILE",p[2],p[3])

def p_if_state1(p):
    '''
    if_state : IF expression block
    '''
    p[0] = ("IF",p[2],p[3])

def p_if_else_state1(p):
    '''
    if_else_state : IF expression block else_state
    '''
    p[0] = ("IF_ELSE",p[2],p[3],p[4])

def p_else_state1(p):
    '''
    else_state : ELSE_IF expression block else_state
    '''
    p[0] = ("ELSE_IF",p[2],p[3],p[4])


def p_else_state2(p):
    '''
    else_state : ELSE block
    '''
    p[0] = ("ELSE",p[2])

def p_else_state3(p):
    '''
    else_state : ELSE_IF expression block
    '''
    p[0] = ("ELSE_IF_ONLY",p[2],p[3])

def p_block(p):
    '''
    block : OPEN_CURL statements CLOSE_CURL
    '''
    p[0] = ("BLOCK", p[2])

def p_function_call1(p):
    '''
    function_call : ID OPEN_BRACKET arg_list CLOSE_BRACKET
    '''
    p[0] = ('FUNC', p[1], p[3])

def p_function_call2(p):
    '''
    function_call : ID OPEN_BRACKET CLOSE_BRACKET'''
    p[0] = ('FUNC',p[1],())

def p_arg_list1(p):
    '''
    arg_list : expression COMMA arg_list
    '''
    args = [p[1]]
    args.extend(p[3][1])
    p[0] = ("ARG_LIST",args)

def p_arg_list2(p):
    '''
    arg_list : expression
    '''
    p[0] = ("ARG_LIST",[p[1]])

def p_expression1(p):
    '''
    expression  : expression MULTIPLY expression
                | expression DIVIDE expression
                | expression PLUS expression
                | expression MINUS expression
                | expression GTEQ expression
                | expression LTEQ expression
                | expression LESS_THAN expression
                | expression MORE_THAN expression
                | expression EQUAL_EQUAL expression
                | expression NOT_EQUAL expression
                | expression AND expression
                | expression OR expression
                | expression PERCENT expression
    '''
    p[0] = ("EXPRESSION",p[2],p[1],p[3])


def p_expression2(p):
    '''
    expression : value

    '''
    p[0] = p[1]


def p_expression3(p):
    '''
    expression : expression DOT function_call
    '''
    p[0] = ('METHOD_CALL',p[1],p[3])


def p_expression4(p):
    '''
    expression : expression OPEN_SQUARE expression CLOSE_SQUARE
    '''
    p[0] = ('INDEX', p[1],p[3])

def p_expression5(p):
    '''
    expression : PLUS_PLUS expression
                | MINUS_MINUS expression
                | expression PLUS_PLUS
                | expression MINUS_MINUS
                | MINUS expression
    '''
    p[0] = ("UNARY",p[1],p[2])

def p_expression6(p):
    '''
    expression : expression OPEN_SQUARE expression COLON expression CLOSE_SQUARE
    '''
    p[0] = ('SUBLIST', p[1], p[3], p[5])


def p_value1(p):
    '''
    value : OPEN_BRACKET expression CLOSE_BRACKET
    '''
    p[0] = ("BRAKET_VAL",p[2])


def p_value2(p):
    '''
    value  : INT
           | FLOAT
           | ID
           | function_call
           | STRING_CONST
           | TRUE
           | FALSE
           | empty_list
    '''
    p[0] = ("VAL",p[1])

def p_empty_list(p):
    '''
    empty_list : OPEN_SQUARE CLOSE_SQUARE
    '''
    p[0] = ("[]")


errors = []

def p_error(t):
    print(t)
    if t:
        errors.append("Syntax error at line {}, token = {}".format(t.lineno,t.type))


parser = yacc.yacc()

def get_errors(string):
    global  errors
    lexer.lineno = 0
    errors = []
    parser.parse(string)
    return errors


if __name__ == "__main__":
    file_map = {}


    for i in range(1, 17):
        dir = base_dir_2 + str(i)
        trans_files = os.listdir(dir + "/transcripts")
        file_map[i] = trans_files

    for current_dir in range(1,17):
        print('')
        print(current_dir)
        to_go_files = file_map[current_dir]
        current_file_name = ""

        while len(to_go_files) > 0:
            lexer.lineno = 1
            current_file_name = to_go_files.pop(0)
            print(current_file_name)
            filepath = base_dir_2 + str(current_dir) + "/pseudocode/" + current_file_name
            with open(filepath,'r') as datafile:
                string_input = datafile.read()

            parser.parse(string_input)
    print()
    print()
    print()
    get_errors("""
		if input_list[j] > input_list[j+1]{
			swap(j,j+1, input_list);
		}	""")

    test_str = """with_tax = 1.2 * meal_price;
with_tip = 1.1 * with_tax;"""
    print(parser.parse(test_str))
    print(parser.parse("return meal_price * 1.2;"))
