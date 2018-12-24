import ply.lex as lex
import os
base_dir = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"

tokens = [
    'ADD_ASSIGN',
    'EQUAL_EQUAL',
    'NOT_EQUAL',
    'PLUS_PLUS',
    'MINUS_MINUS',
    'MINUS_ASSIGN',
    'MULT_ASSIGN',
    'DIVIDE_ASSIGN',
    'AND_ASSIGN',
    'ASSIGN',
    'LESS_THAN',
    'LTEQ',
    'MORE_THAN',
    'GTEQ',
    'INT',
    'FLOAT',
    'ID',
    'PLUS',
    'PERCENT',
    'MINUS',
    'DIVIDE',
    'MULTIPLY',
    'COMMA',
    'DOT',
    'COLON',
    'END_STMT',
    'OPEN_BRACKET',
    'CLOSE_BRACKET',
    'OPEN_CURL',
    'CLOSE_CURL',
    'OPEN_SQUARE',
    'CLOSE_SQUARE',
    'STRING_CONST',
]

reserved = {
    'return' : 'RETURN',
    'for': 'FOR',
    'in' : 'IN',
    'while' : 'WHILE',
    'if' : 'IF',
    'else_if' : 'ELSE_IF',
    'else' : 'ELSE',
    'and' : 'AND',
    'or' : 'OR',
    'continue': 'CONTINUE',
    'true': 'TRUE',
    'false': 'FALSE'
}


tokens += reserved.values()
t_ADD_ASSIGN = r'\+\='
t_PLUS_PLUS = r'\+\+'
t_MINUS_MINUS = r'\-\-'
t_EQUAL_EQUAL = r'\=\='
t_NOT_EQUAL = r'\!\='
t_MINUS_ASSIGN = r'\-\='
t_MULT_ASSIGN = r'\*\='
t_DIVIDE_ASSIGN = r'\/\='
t_ASSIGN = r'\='
t_LESS_THAN = r'\<'
t_LTEQ = r'\<='
t_MORE_THAN = r'\>'
t_GTEQ = r'\>='
t_AND_ASSIGN = r'\&\='
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_PERCENT = r'\%'
t_COMMA = r','
t_DOT = r'\.'
t_COLON = r'\:'
t_END_STMT = r';'
t_OPEN_BRACKET = r'\('
t_CLOSE_BRACKET = r'\)'
t_OPEN_CURL = r'\{'
t_CLOSE_CURL = r'\}'
t_OPEN_SQUARE = r'\['
t_CLOSE_SQUARE = r'\]'
t_ignore = ' '

def t_STRING_CONST(t):
    r'\".*\"'
    return t

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno +=1

def t_WHITESPACE(t):
    r'\t'
    return None

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-z_][a-z_0-9]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()

if __name__ == "__main__":
    file_map = {}


    for i in range(1, 17):
        dir = base_dir + str(i)
        trans_files = os.listdir(dir + "/transcripts")
        file_map[i] = trans_files

    current_dir = 2
    to_go_files = file_map[current_dir]
    current_file_name = ""

    while len(to_go_files) > 0:
        current_file_name = to_go_files.pop(0)
        print(current_file_name)
        filepath = base_dir + str(current_dir) + "/pseudocode/"+current_file_name
        with open(filepath,'r') as datafile:
            string_input = datafile.read()

        lexer.input(string_input)
        while True:
            tok = lexer.token()
            if not tok:
                break
            # print(tok)

