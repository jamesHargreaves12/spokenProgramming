from enum import Enum

from data_prep_tools.graph_funs import DependencyGraph
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
              "number": "NUMBER",
              "and": "and",
              "plus equal+s": "+=",
              "empty": "[]",
              "empty not+": "!= []",
              "set": "=",
              "while": "while",
              "if":"if",
              "else":"else",
              "greater than": ">",
              "less than": "<",
              "larger": ">",
              "be+s larger": ">",
              "be+s": "==",
              "be+s equal": "==",
              "for": "for",
              'in': "in",
              "initialize": "=",
              "increment": "+= 1",
              "index": ("[","]"),
              "get": "="
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
    "let":[],
    "take": [],
    "the":[],
    "it": [],
    "to": [],
    "block":[],
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
    "at":[]
}
rotate_up_tokens = ["store in"]
lr_assign_infix = ["equal+s","plus equal+s","set", "equal"]
lr_assign_prefix = ["set","initialize"]
rl_assign = ["store in"]
no_affect_on_context = ["and","by"]
comparison_strings = ["greater than", "less than", "be+s","be+s equal", "be+s larger", "greater","smaller","larger"]

def get_next_context(cur_context, token,child_num):
    if token in load_dep_parse.aritmetic_strings + comparison_strings:
        return Context.ARITHMETIC
    elif token == "return":
        return Context.RETURN
    elif token in ["if","else" "else if", "while"]:
        return Context.BOOL if child_num == 0 else Context.ROOT
    elif token in lr_assign_infix + lr_assign_prefix:
        return Context.L_ASSIGN if child_num == 0 else Context.R_ASSIGN
    elif token in no_affect_on_context or token in filter_mapping.keys():
        return cur_context
    elif token.startswith("variable_") or token in ["number","empty"]:
        return Context.VAR_CONST
    elif token.startswith("function_call_"):
        return Context.FUNCT_CALL
    elif token == "for":
        return Context.EXP
    elif token in ["be+s"]:
        return Context.BOOL
    elif token in ["increment","decrement"]:
        return Context.L_ASSIGN
    elif token in ["in"]:
        return Context.EXP
    elif token in rl_assign:
        return Context.R_ASSIGN if child_num == 0 else Context.L_ASSIGN
    else :
        print("get_next_context uncovered case:",token,cur_context)

def filter_graph(graph:DependencyGraph, root, context):
    token = root["token"]
    root_orig_index = root["orig_index"]
    child_count = 0
    for orig_index in [x["orig_index"] for x in dependency_graph.get_children(root)]:
        child = dependency_graph.get_vertex_by_orig_index(orig_index)
        next_context = get_next_context(context,token,child_count)
        filter_graph(graph, child, next_context)
        child_count += 1
    # required since deleting earlier verticies deletes root
    root = graph.get_vertex_by_orig_index(root_orig_index)
    assert root["token"]==token, "token changed: " + token
    if token in filter_mapping and context not in filter_mapping[token]:
        children_list = graph.get_children(root)

        if len(children_list) == 0:
            graph.remove_vertex(root.index)
        elif len(children_list) == 1:
            graph.combine((root.index,children_list[0].index),keep_first_tok=False)
        else :
            # this currently just chooses the first avaliable child and promotes it amy want to look if a better solution
            graph.combine((root.index,children_list[0].index),keep_first_tok=False)

def transform_graph(graph:DependencyGraph, root, context):
    orig_indicies = [x["orig_index"] for x in dependency_graph.get_children(root)]
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
    node_str = trans_dict[token]
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

    elif token in load_dep_parse.aritmetic_strings:
        items.insert(-1,node_str)

    elif token in ["increment", "decrement"]:
        items.insert(-1,node_str)

    elif token == "return":
        items.insert(0,node_str)

    elif token.startswith("variable_") or token.startswith("function_call_") or token == "number":
        insert_index = sum([1 for x in children if x["orig_index"] < root["orig_index"]])
        items.insert(insert_index,node_str)

    elif token in ["and"]:
        if contex in [Context.BOOL, Context.EXP]:
            items.append(node_str)

    elif token in ["if", "while", "for"]:
        items.insert(0, node_str)

    elif token in ["index"]:
        # this is a difficult case because index is represented by the surrounding brakets in [exp]
        items.insert(0,node_str[0])
        items.insert(2,node_str[1])

    elif token in ["empty not+", "in"]:
        # we expect no children for these - if they exist we wish for it to be appended
        items.insert(0, node_str)

    elif token in comparison_strings:
        items.insert(1,node_str)

    else:
        print("unknown root",token)

    return " ".join(items)

toks,deps = load_dep_parse.get_token_deps()

for i in range (0,15):
    print("***************",i)
    dependency_graph = load_dep_parse.get_dependency_graph(toks[i],deps[i])
    dependency_graph.print_tokens()
    # if i == 9:
    #     dependency_graph.plot_graph()

    for orig_index in [x["orig_index"] for x in dependency_graph.get_roots()]:
        next_root = dependency_graph.get_vertex_by_orig_index(orig_index)
        filter_graph(dependency_graph, next_root,Context.ROOT)

    for orig_index in [x["orig_index"] for x in dependency_graph.get_roots()]:
        next_root = dependency_graph.get_vertex_by_orig_index(orig_index)
        filter_graph(dependency_graph,next_root,Context.ROOT)

    for orig_index in [x["orig_index"] for x in dependency_graph.get_roots()]:
        next_root = dependency_graph.get_vertex_by_orig_index(orig_index)
        transform_graph(dependency_graph,next_root,Context.ROOT)

    if i == 12:
        dependency_graph.plot_graph()

    total = ""
    roots = dependency_graph.get_roots()
    for root in roots:
        exp_str = get_expression(dependency_graph,root,Context.ROOT)
        if exp_str:
            total += exp_str + " "
    print(total)
