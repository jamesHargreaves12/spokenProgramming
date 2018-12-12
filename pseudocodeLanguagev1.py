import ply.lex as lex
import ply.yacc as yacc
base_dir = "/Users/james_hargreaves/Documents/ThirdYear/Part2ProjectData/"

string_input = ""
with open(base_dir+"1/pseudocode/329759.txt","r") as file:
    string_input = file.read()


tokens = [
    'RETURN',
    'INT',
    'FLOAT',
    'ID',
    'PLUS',
    'MINUS',
    'DIVIDE',
    'MULTIPLY',
    'ASSIGN',
    'END_STMT',
    'NEWLINE'
]

reserved = {
    'return' : 'RETURN'
}

tokens += reserved.values()

t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_ASSIGN = r'\='
t_END_STMT = r';'
t_ignore = ' '

def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno +=1

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
    print("Illegal characters!")
    t.lexer.skip(1)


lexer = lex.lex()

lexer.input(string_input)
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)



def p_file(p):
    '''
    statements : statements statement
    '''
    print(p[2])

def p_file2(p):
    '''statements :
    '''

def p_statement1(p):
    '''
    statement : expression END_STMT
    '''
    p[0] = p[1]

def p_statement2(p):
    '''
    statement : ID ASSIGN expression END_STMT
    '''
    p[0] = (p[2],p[1],p[3])

def p_statement3(p):
    '''
    statement : RETURN expression END_STMT
    '''
    p[0] = (p[1],p[2])

def p_expression(p):
    '''
    expression  : expression MULTIPLY expression
                | expression DIVIDE expression
                | expression PLUS expression
                | expression MINUS expression
    '''
    p[0] = (p[2],p[1],p[3])


def p_expression_value(p):
    '''
    expression : value
    '''
    p[0] = p[1]

def p_number(p):
    '''
    value  : INT
           | FLOAT
           | ID
    '''
    p[0] = p[1]


parser = yacc.yacc()

parser.parse(string_input)