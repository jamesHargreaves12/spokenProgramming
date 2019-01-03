from data_prep_tools.get_data import get_data_from_directory
import ibmmodel1

transcripts = get_data_from_directory("/transcripts_var_replaced/")
pseudocode = get_data_from_directory("/pseudocode_simplified/")
pairs = [([a.strip('\n') for a in x.split(" ") if a != ''],[a.strip('\n') for a in y.split(" ") if a != '']) for x,y in zip(transcripts,pseudocode)]

t = ibmmodel1.train(pairs,1000)

pseudocode_lexicon = ['NULL','.', '<', 'if', ']', 'or', '-', '+', '!=', 'for', 'true', ')', '>', 'NEWLINE', '&', '>=', 'continue', 'while', 'index', 'else', 'return', '<=', 'false', 'FUNCTION_CALL', '(', '*', '=', '/', 'STRING_CONST', '%', 'and', 'EMPTY_LIST', 'VARIABLE', '==', '[', ':', 'in', 'NUMBER']
english_lexicon = ['', 'the', 'there', 'called', 'look', 'onto', 'while', 'second', 'equals', 'returns', 'results', 'subtract', 'front', "let's", 'divide', 'smaller', 'result', 'into', 'VARIABLE', 'else', 'false', 'b', 'also', 'of', 'plus', 'parenthesis', 'then', 'to', 'brackets', 'is', 'not', 'end', 'define', 'be', 'on', 'backslash', 'both', 'it', 'for', 'line', 'minus', 'remaineder', 'greater', 'removed', 'do', 'source', 'from', 'half', 'marks', 'element', 'first', 'fizz', 'less', 'recursively', 'defined', 'increment', 'calculate', 'put', 'halves', 'more', 'sort', 'inclusive', 'equal', 'items', 'if', 'parentheses', 'times', 'empty', 'using', 'indices', 'between', 'way', 'close', 'next', 'so', 'or', 'set', 'percent', 'than', 'square', 'start', 'store', 'multiplied', 'different', 'beginning', 'variable', 'list', 'return', 'initialize', 'div', 'indexed', 'check', 'does', 'otherwise', 'NUMBER', 'j', 'incrementing', 'a', 'item', 'let', 'speech', 'this', 'bigger', 'obtained', 'time', 'loop', 'nothing', 'sorted', 'which', 'call', 'function', 'with', 'th', 'following', 'add', 'together', 'by', 'variables', 'divided', 'integer', 'an', 'as', 'get', 'FUNCTION_CALL', 'larger', 'block', 'n', 'multiply', 'open', 'where', 'position', 'over', 'up', 'buzz', 'true', 'in', 'that', 'increments', 'take', 'bracket', 'all', 'decrements', 'each', 'new', 'create', 'given', 'dot', 'merged', 'key', 'and', 'named', 'algorithm', 'at', 'looking', 'value', 'character', 'off', 'index']


for e in english_lexicon:
    max_val = 0
    max_p = ""
    for p in pseudocode_lexicon:
        if t[(e,p)] > max_val:
            max_val = t[(e,p)]
            max_p = p
    print("For Token: "+ e +" closest P: "+max_p +'                 with prob:' + str(t[(e,max_p)]))
