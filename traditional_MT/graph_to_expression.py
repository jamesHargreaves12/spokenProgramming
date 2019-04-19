from enum import Enum

from data_prep_tools.constants import base_dir_2
from data_prep_tools.graph_funs import DependencyGraph
from tools.find_resource_in_project import get_path
from traditional_MT import load_dep_parse


class Context(Enum):
    ROOT = 1
    L_ASSIGN = 2
    R_ASSIGN = 3
    ARITHMETIC = 4
    RETURN = 5
    VAR_CONST = 6
    FUNCT_CALL = 7
    BOOL = 8
    EXP = 9

trans_dict = {"plus": "+",
              "minus": "-",
              "time+s": "*",
              "multiply": "*",
              "multiply+ed": "*",
              "devide": "/",
              "divide+ed": "/",
              "add": "+",
              "equal+s": "=",
              "equal": "=",
              "store in": "=",
              "true": "true",
              "false": "false",
              "return": "return",
              "variable_0": "VARIABLE_0",
              "variable_1": "VARIABLE_1",
              "variable_2": "VARIABLE_2",
              "variable_3": "VARIABLE_3",
              "variable_4": "VARIABLE_4",
              "variable_5": "VARIABLE_5",
              "variable_6": "VARIABLE_6",
              "variable_7": "VARIABLE_7",
              "function_call_0": "FUNCTION_CALL_0",
              "function_call_1": "FUNCTION_CALL_1",
              "function_call_2": "FUNCTION_CALL_2",
              "function_call_3": "FUNCTION_CALL_3",
              "function_call_4": "FUNCTION_CALL_4",
              "function_call_5": "FUNCTION_CALL_5",
              "function_call_6": "FUNCTION_CALL_6",
              "function_call_7": "FUNCTION_CALL_7",
              "function_call_8": "FUNCTION_CALL_8",
              "function_call_9": "FUNCTION_CALL_9",
              "function_call_10": "FUNCTION_CALL_10",
              "number": "NUMBER",
              "and": "and",
              "plus equal+s": "+=",
              "empty": "[]",
              "empty not+": "!= []",
              "set": "=",
              "in": "in",
              "while": "while",
              "if":"if",
              "else":"else",
              "be+s greater": ">",
              "be+s greater than": ">",
              "greater than": ">",
              "less than": "<",
              "larger": ">",
              "be+s larger": ">",
              "be+s": "==",
              "for": "for",
              "initialize": "=",
              "increment": "+= 1",
              "index": "index",
              "key": "index",
              "increment by": "+=",
              "add to": "+=",
              "for in": ("for", "in"),
              "get": "=",
              "create": "=",
              "open bracket":"(",
              "close bracket": ")",
              "open parenthesis+s":"(",
              "close parenthesis+s": ")",
              "open bracket+s":"(",
              "close bracket+s": ")",
              "open parenthesis":"(",
              "close parenthesis": ")",
              "be+s equal": "=",
              "plus equal": "+=",
              "increments by": "+=",
              "set equal": "=",
              'look+ing up': "index",
              'look up': "index",
              "dot": ".",
              "be+s less than": "<",
              "smaller than": "<",
              "index+ed at": "index",
              "or": "or",
              "str": "STRING_CONST",
              "not+": "not",
              "not+ equal": "!=",
              "be+s less than or equal": "<=",
              "less than or equal": "<=",
              "less than or": "<",
              "be+s greater than or equal": ">=",
              "greater than or equal": ">=",
              "greater than or": ">",
              "increment+s by": "+=",
              "plus plus": "+= 1",
              "minus minus": "-= 1",
              "store": "=",
              "percent": "%",
              "equal+s equal+s": "==",
              "increment+ing": "+= 1",
              "increment+ing by": "+=",
              "otherwise": "else",
              "different": "!=",
              "return+s": "return",
              "over":"/",
              "decrement+s by":" -=",
              "decrement+s": "-= 1",
              "be+s bigger than": ">",
              "bigger than": ">",
              "subtract": "-",
              "add and": "+",
              "store that": "="

}
# Mapping from token to context list in which they shouldnt be filtered
# empty list implies all contexts
filter_mapping = {
    "this":[],
    "so":[],
    "by":[],
    'variable':[],
    "name+ed":[],
    "next":[],
    "then":[],
    "a":[],
    "do":[],
    "let":[],
    "take": [],
    "the":[],
    "it": [],
    "to": [],
    "block":[],
    "together":[],
    "end":[],
    "of": [],
    "on": [],
    "get": [],
    "from": [],
    "start": [],
    "remove+ed": [],
    "loop": [],
    "new": [],
    "that": [],
    "be":[],
    "than":[],
    "item":[],
    "each":[],
    "inclusive":[],
    "value":[],
    "at":[],
    "all":[],
    "use+ing": [],
    "as": [],
    "item+s": [],
    "list": [],
    "obtain+ed": [],
    "and then": [],
    "end for": [],
    "end if": [],
    "end while": [],
    "'s+": [],
    "give+en": [],
    "with":[],
    "between": [],
    "integer":[],
    "time":[],
    "do+s": [],
    "put":[],
    "speech": [],
    "mark+s": [],
    "follow+ing": [],
    "up": [],
    "calculate": [],
    # This is a weird one but I think it is best to put it in here
    "recursively":[],
    "recurse":[],
    "where": [],
    "result": [],
    "call+ed": [],
}
rotate_up_tokens = ["store in"]
lr_assign_infix = ["plus plus", "increment+ing", "increment+s by","set equal","equal+s","plus equal","plus equal+s","set", "equal", "increment by", "increment+s by","decrement+s by","increment+ing by", "be+s equal"]
lr_assign_prefix = ["set","initialize","add to","create"]
rl_assign = ["store in","store", "store that"]
no_affect_on_context = ["and","by","or","not+"]
comparison_strings = ["be+s less than", "different", "be+s bigger than","bigger than", "bigger", "be+s greater than", "be+s greater ", "greater than or","greater than or equal","be+s greater than or equal","be+s less than or equal","less than or equal","less than or","smaller than", "greater than", "less than", "be+s","be+s equal", "not+ equal", "be+s larger", "greater","smaller","larger", "equal+s equal+s"]
index_infix = ["index","key","index+ed at"]
index_prefix = ["look+ing up", "look up"]
expected_tails = ["true","false","empty not+", "open parenthesis", "close bracket+s","open bracket+s", "close parenthesis", "open parenthesis+s", "close parenthesis+s", "open bracket", "close bracket", "str"]
boolean_control_flow = ["if","else", "else if", "while", "for","otherwise"]

# bad examples are 30,34,47,

def get_next_context(cur_context, token,child_num):
    if token in load_dep_parse.aritmetic_strings + comparison_strings:
        return Context.ARITHMETIC
    elif token in ["return","return+s"]:
        return Context.RETURN
    elif token in boolean_control_flow:
        return Context.BOOL if child_num == 0 else Context.ROOT
    elif token in lr_assign_infix + lr_assign_prefix:
        return Context.L_ASSIGN if child_num == 0 else Context.R_ASSIGN
    elif token in no_affect_on_context or token in filter_mapping.keys():
        return cur_context
    elif token.startswith("variable_") or token in ["number","empty"]:
        return Context.VAR_CONST
    elif token.startswith("function_call_"):
        return Context.FUNCT_CALL
    elif token == 'dot':
        return Context.FUNCT_CALL
    elif token == "for":
        return Context.EXP
    elif token in ["be+s"]:
        return Context.BOOL
    elif token in ["increment","decrement"]:
        return Context.L_ASSIGN
    elif token in ["in"]:
        return Context.EXP
    if token in expected_tails:
        return Context.EXP
    if token in index_infix:
        return Context.L_ASSIGN if child_num == 0 else Context.EXP
    elif token in rl_assign:
        return Context.R_ASSIGN if child_num == 0 else Context.L_ASSIGN
    elif token == "for in":
        return Context.L_ASSIGN if child_num == 0 else Context.EXP
    elif token in index_prefix:
        return Context.L_ASSIGN if child_num == 0 else Context.EXP
    elif token == "add and":
        return Context.ARITHMETIC
    else :
        print("get_next_context uncovered case:",token,cur_context)


def filter_graph(graph:DependencyGraph, root, context):
    token = root["token"]
    root_orig_index = root["orig_index"]
    child_count = 0
    for orig_index in [x["orig_index"] for x in graph.get_children(root)]:
        child = graph.get_vertex_by_orig_index(orig_index)
        next_context = get_next_context(context,token,child_count)
        filter_graph(graph, child, next_context)
        child_count += 1
    # required since deleting earlier verticies deletes root
    root = graph.get_vertex_by_orig_index(root_orig_index)
    assert root["token"]==token, "token changed: " + token
    if token in filter_mapping and context not in filter_mapping[token]:
        graph.remove_vertex_with_child_promote(root)


def transform_graph(graph:DependencyGraph, root, context):
    orig_indicies = [x["orig_index"] for x in graph.get_children(root)]
    if root["token"] in rotate_up_tokens:
        parents = graph.get_parents(root.index)
        if parents:
            graph.rotate_edge((parents[0],root.index))
    child_count = 0
    for orig_index in orig_indicies:
        child = graph.get_vertex_by_orig_index(orig_index)
        next_context = get_next_context(context, root["token"], child_count)
        transform_graph(graph,child,next_context)
        child_count += 1

def get_expression(graph, root, contex):
    token = root["token"]
    children = sorted(graph.get_children(root),key=lambda x:x["orig_index"])
    child_terms = []

    if token in trans_dict:
        node_str = trans_dict[token]
    else:
        print("Token not in dictionary:", token)
        node_str = ""

    for i, child in enumerate(children):
        child_terms.append(get_expression(graph, child, get_next_context(contex, token, i)))

    items:list = child_terms

    if token in lr_assign_infix + lr_assign_prefix:
        if contex not in [Context.L_ASSIGN,Context.R_ASSIGN,Context.RETURN]:
            if (children and children[0]["orig_index"] < root["orig_index"]) or token in lr_assign_prefix:
                items.insert(1,node_str)
            else:
                items.insert(0,node_str)

    elif token in rl_assign:
        if contex not in [Context.L_ASSIGN,Context.R_ASSIGN,Context.RETURN]:
            items = [x for x in reversed(items)]
        items.insert(1,node_str)

    elif token == "dot":
        items.insert(1,node_str)

    elif token == "in":
        if contex not in [Context.RETURN, Context.FUNCT_CALL, Context.ARITHMETIC]:
            items.insert(1,node_str)

    elif token in load_dep_parse.aritmetic_strings:
        if len(items) > 1:
            items.insert(1,node_str)
        else:
            items.insert(-1,node_str)

    elif token in ["increment", "decrement"]:
        items.insert(-1,node_str)

    elif token == "add and":
        items.insert(1,node_str)

    elif token in ["return","return+s"]:
        items.insert(0,node_str)

    elif token == "not+":
        items.insert(0,node_str)

    elif token.startswith("variable_") or token.startswith("function_call_") or token == "number":
        insert_index = sum([1 for x in children if x["orig_index"] < root["orig_index"]])
        items.insert(insert_index,node_str)

    elif token in ["and","or"]:
        if contex in [Context.BOOL, Context.EXP]:
            items.append(node_str)

    elif token in boolean_control_flow:
        items.insert(0, node_str)

    elif token in index_infix:
        if len(items) >= 2:
            items.insert(1,node_str)
        else:
            items.insert(0,node_str)

    elif token in index_prefix:
        if len(items) > 1:
            items.reverse()
            items.insert(1,node_str)
        else:
            items.insert(0,node_str)

    elif token in expected_tails:
        # we expect no children for these - if they exist we wish for it to be appended
        items.insert(0, node_str)

    elif token in comparison_strings:
        items.insert(1,node_str)

    elif token == "for in":
        items.insert(0,node_str[0])
        if len(items) >= 2 and len(items[1].split(" ")) > 1:
            array_toks = items[1].split(" ")
            array_toks.insert(1, node_str[1])
            items[1] = " ".join(array_toks)
        else:
            items.insert(2,node_str[1])

    else:
        print("unknown root",token)

    return " ".join(items)


def get_output_string(tokens,dependencies):
    dependency_graph = load_dep_parse.get_dependency_graph(tokens,dependencies)

    for orig_index in [x["orig_index"] for x in dependency_graph.get_roots()]:
        next_root = dependency_graph.get_vertex_by_orig_index(orig_index)
        filter_graph(dependency_graph, next_root,Context.ROOT)

    for orig_index in [x["orig_index"] for x in dependency_graph.get_roots()]:
        next_root = dependency_graph.get_vertex_by_orig_index(orig_index)
        filter_graph(dependency_graph,next_root,Context.ROOT)

    for orig_index in [x["orig_index"] for x in dependency_graph.get_roots()]:
        next_root = dependency_graph.get_vertex_by_orig_index(orig_index)
        transform_graph(dependency_graph,next_root,Context.ROOT)

    total = ""
    roots = dependency_graph.get_roots()
    for root in roots:
        exp_str = get_expression(dependency_graph,root,Context.ROOT)
        if exp_str:
            total += exp_str + " "
    return total

if __name__ == "__main__":
    toks,deps = load_dep_parse.get_token_deps(base_dir=base_dir_2)
    # for i in range (40,49):
    #     print("***************",i)
    #     print(get_output_string(toks[i],deps[i]))

    # with open(get_path("/results/traditional_train.txt"),"w+") as file:
    #     for tok,dep in zip(toks[:49],deps[:49]):
    #         file.write(get_output_string(tok,dep))
    #         file.write('\n')

    with open(get_path("/results/traditional_test2.txt"),"w+") as file:
        for tok,dep in zip(toks,deps):
            file.write(get_output_string(tok,dep))
            file.write('\n')
