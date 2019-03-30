import re
from collections import namedtuple,defaultdict
from data_prep_tools.graph_funs import DependencyGraph
from data_prep_tools.constants import base_dir

Dependency = namedtuple('Dependency', 'type, head_val, head_position, head_type, dependent_val, dependent_position, dependent_type')
tokens_re = re.compile(r"\|([\'a-z+0-9_]+?):([0-9]+?)_(([A-Z&0-9]+?)|\$)\|")
# OLD dependency_re = re.compile(r"\(\|([a-z0-9]+?)\|( _| \|[a-z]+\|){0,1} \|([a-z+0-9_]+?):([0-9]+?)_([A-Z&0-9]+?)\| \|([a-z+0-9_]+?):([0-9]+?)_([A-Z0-9&]+?)\|( _| \|[a-z]+\|){0,1}\)\n")
dependency_re = re.compile(r"\(\|([\'a-z+0-9_]+?)\|(?: _| \|[a-z]+\|){0,1}(?: \|(?:[\'a-z+0-9_]+):(?:[0-9]+)_(?:[A-Z&0-9]+)\|){0,1} \|([\'a-z+0-9_]+?):([0-9]+?)_([A-Z&0-9]+?)\| \|([\'a-z+0-9_]+?):([0-9]+?)_([A-Z0-9&]+?)\|( _| \|[a-z]+\|){0,1}\)\n")

dependency_extra_info_re = re.compile(r"\(\|([a-z]+?)\| \|([a-z+0-9_]+?):([0-9]+?)_([A-Z&0-9]+?)\|\)\n")
aritmetic_strings = ["subtract","plus","minus", "over", "time+s","multiply", "multiply+ed", "devide","divide+ed","add","percent"]

# list of head token, tail token to types of relationship you want to combine
# if list is empty then it will apply to all types of relationship
combine_mapping = {
    ("and","equal+s"):["conj"],
    ("time+s", "equal+s"):["conj"],
    ("minus", "equal+s"):["conj"],
    ("add", "equal+s"):["conj"],
    ("plus", "equal+s"):["conj"],
    ("greater","than"): ["cmod"],
    ("empty","not+"): [],
    ("be+s","larger"): [],
    ("be+s","smaller"): [],
    ("be+s","equal"): [],
    ("store","in"):[],
    ("else","if"):[],
    ("set","equal"):[],
    ("at","index"):[],
    ("for","in"):[],
}

# head, tail, start, end(non inclusive)
combine_by_position_mapping = [
    ("increment","by",1,4),
    ("increment+s","by",1,3),
    ("decrement+s","by",1,3),
    ("decrement","by",1,4),
    ("for", "in", 1,4),
    ("add","to",1,4),
    ("open", "bracket", 1, 2),
    ("close", "bracket", 1, 2),
    ("open", "parenthesis+s", 1, 2),
    ("close", "parenthesis+s", 1, 2),
    ("open", "parenthesis", 1, 2),
    ("close", "parenthesis", 1, 2),
    ("open", "bracket+s", 1, 2),
    ("close", "bracket+s", 1, 2),
    ("be+s", "equal", 1, 2),
    ("plus", "equal",1,2),
    ("plus", "plus",1,2),
    ("equal+s", "equal+s",1,2),
    ("minus", "minus",1,2),
    ("and","then",1,2),
    ("end", "for", 1, 3),
    ("end", "if", 1, 3),
    ("end", "while", 1, 3),
    ("look+ing", "up", 1, 2),
    ("look", "up", 1, 2),
    ("less", "than", 1, 2),
    ("be+s", "less than", 1, 2),
    ("be+s less than", "or", 3, 4),
    ("be+s less than or", "equal", 4, 5),
    ("less than","or",2,3),
    ("less than or","equal",3,4),
    ("greater", "than", 1,2),
    ("be+s", "greater",1,2),
    ("be+s", "greater than", 1, 2),
    ("greater than","or",2,3),
    ("greater than or","equal",3,4),
    ("be+s","greater than",1,2),
    ("be+s greater than","or",3,4),
    ("be+s greater than or","equal",4,5),
    ("index+ed", "at", 1, 2),
    ("smaller", "than", 1, 2),
    ("not+", "equal", 1, 2),
    ("increment+ing", "by", 1, 2),
    ("bigger", "than", 1, 2),
    ("be+s", "bigger than", 1, 2),
    ("add", "and", 2, 4),
    ("store", "that", 1, 2),
]


def get_token_deps():
    with open(base_dir + "transcripts_replaced.parses", "r") as file:
        line = file.readline()
        token_lists = []
        dep_strs = []
        while line:
            dep_lines = []
            while line and len(line) > 1:
                dep_lines.append(line)
                line = file.readline()
            line = file.readline()
            if dep_lines:
                # token_lists.append(dep_lines[0])
                token_lists.append([tok[0] for tok in tokens_re.findall(dep_lines[0])])
                # dep_strs.append(dep_lines[2:])
                dep_strs.append([get_dependency(dep_str) for dep_str in dep_lines[2:]])
    return token_lists,dep_strs


def get_dependency(dependency_str):
    match = dependency_re.match(dependency_str)
    if match:
        return Dependency(match[1],match[2],match[3],match[4],match[5],match[6],match[7])
    elif dependency_extra_info_re.match(dependency_str):
        # of the form: (|passive| |name+ed:10_VVN|)
        return
    else:
        print("ISSUE", dependency_str)

# maybe move this into DependencyGraph class
def break_graph(graph:DependencyGraph,edge,enforce_order_on_split):
    # if child of dependent from earlier token switch it onto the head
    # if head after dependent attach it to dependent
    graph.remove_edge(edge)
    if not enforce_order_on_split:
        return
    head = edge[0]
    new_root_vert = edge[1]

    if head > new_root_vert:
        head_parents = graph.get_parents(head)
        for head_parent in head_parents:
            cur_edge_lab = graph.get_label((head_parent, head))
            graph.add_edge((new_root_vert, head), cur_edge_lab)
            graph.remove_edge((head_parent, head))
        if head_parents:
            head = head_parents[0]

    return_child_verts = graph.get_children_indices(edge[1])
    for child in return_child_verts:
        if child < new_root_vert:
            # attach child to returns original parent
            cur_edge = (new_root_vert, child)
            new_edge = (head, child)
            edge_lab = graph.get_label(cur_edge)
            graph.add_edge(new_edge, edge_lab)
            graph.remove_edge(cur_edge)



def get_rejected_root(graph:DependencyGraph, vertex, root1, root2):
    keywords = ["while", "for", "if", "else", "return"]
    root1_key = root1["token"] in keywords
    root2_key = root2["token"] in keywords
    if root1_key and not root2_key:
        return root2
    elif root2_key and not root1_key:
        return root1
    dist1 = graph.get_distance(root1,vertex)
    dist2 = graph.get_distance(root2,vertex)
    if dist1 > dist2:
        return root1
    elif dist2 > dist1:
        return root2
    # default:
    return root2


def is_new_expression(graph:DependencyGraph, vertex_id):
    return graph.get_token(vertex_id) in ["plus equal+s"]


def filter_out_double_edge(graph:DependencyGraph, edges:list):
    edges = edges.copy()
    filtered_edges = []
    while edges:
        edge = edges.pop()
        clashes = [e for e in edges+filtered_edges if e[1] == edge[0]]
        if not any(clashes):
            filtered_edges.append(edge)
    return filtered_edges


def remove_tokens(graph:DependencyGraph, edges, tokens, tail_only=False):
    filter_edges = []
    for edge in edges:
        hd, tl = edge
        if not(tail_only) and graph.get_vertex_lable(hd) in tokens or \
                graph.get_vertex_lable(tl) in tokens:
            continue
        elif not(graph.get_parents(hd) or is_new_expression(graph, edge[1])):
            continue
        else:
            filter_edges.append(edge)
    return filter_edges


def filter_if_both_aritmetic(graph:DependencyGraph, edges):
    filtered = []
    for edge in edges:
        hd,tl = graph.get_verticies(edge)
        if not(hd["token"] in aritmetic_strings and tl["token"] in aritmetic_strings):
            filtered.append(edge)
    return filtered


def graph_combine(graph:DependencyGraph):
    loop = True
    while loop:
        loop = False
        for edge in graph.get_edges():
            head,tl = graph.get_verticies(edge)
            tok_tup = (head["token"],tl["token"])
            if tok_tup in combine_mapping.keys() and (combine_mapping[tok_tup] == []
                    or graph.get_label(edge) in combine_mapping[tok_tup]):
                graph.combine(edge)
                loop = True
                break


def graph_break_1(graph:DependencyGraph):
    # token signifies new tree
    enforce_order_on_split = True
    for edge in graph.get_edges_with_dependent_token("return"):
        break_graph(graph,edge, True)
    for edge in graph.get_edges_with_dependent_token("for"):
        break_graph(graph,edge, True)
    for edge in graph.get_edges_with_dependent_token("while"):
        break_graph(graph,edge, True)
    for edge in graph.get_edges_with_dependent_token("if"):
        break_graph(graph,edge, True)
    for edge in graph.get_edges_with_dependent_token("else"):
        break_graph(graph, edge, True)
    for edge in graph.get_edges_with_dependent_token("set"):
        break_graph(graph, edge, True)

def edge_joins_identical_tokens(graph,edge):
    hd,tl = edge
    return graph.get_vertex_lable(hd) == graph.get_vertex_lable(tl)

def graph_break_2(graph:DependencyGraph):
    ht_disallowed_tokens = ["by","than","to"]
    t_dissallowed_tokens = ["number"]
    ccomp_edges = graph.get_edges_with_type("ccomp")
    filter_edges = remove_tokens(graph,ccomp_edges,ht_disallowed_tokens)
    filter_edges = remove_tokens(graph,filter_edges,t_dissallowed_tokens,tail_only=True)
    filter_edges = filter_if_both_aritmetic(graph,filter_edges)
    filter_edges = filter_out_double_edge(graph, filter_edges)

    for edge in filter_edges:
        identical_toks = edge_joins_identical_tokens(graph,edge)
        break_graph(graph,edge,enforce_order_on_split=identical_toks)

def graph_break_3(graph:DependencyGraph):
    #  This solves the problem where a graph has 2 roots
    #  for a single node ie not a tree
    #  Also removes any cycles by choosing to delete the last visited edge on traversal from root

    roots = graph.get_roots()
    transitive_closures = [set(graph.transitive_closure(root,[])) for root in roots]
    # compute all pairwise intersections
    for i,root1 in enumerate(roots):
        for j,root2 in enumerate(roots):
            if i >= j:
                continue
            intersect = transitive_closures[i] & transitive_closures[j]
            if intersect:
                intersect = list(intersect)
                # closest vertex is common to both roots
                vertex = graph.get_closest_to_root(root1,intersect)
                root = get_rejected_root(graph, vertex, root1, root2)
                path = graph.get_path(root,vertex)
                graph.remove_edge((path[-1].index,path[-2].index))

    for root in graph.get_roots():
        graph.remove_cycles(root)

def graph_break_4(graph):
    for hd,tl in graph.get_edges():
        head = graph.get_vertex_from_id(hd)
        tail = graph.get_vertex_from_id(tl)
        if abs(head["orig_index"] - tail["orig_index"]) > 12:
            graph.remove_edge((hd,tl))

def transform_dependency_graph(dg:DependencyGraph):
    graph_combine(dg)
    graph_break_1(dg)
    graph_break_2(dg)
    graph_break_3(dg)
    graph_break_4(dg)
    graph_combine(dg)


def pronoun_resolution(labels:list):
    # in all the examples I looked at it refered to the previous variable mention:
    # (if it occurs before a variable has been found then will leave it alone and then delete in filter stage)
    prev_variable = ""
    for i in range(len(labels)):
        if labels[i].startswith("variable_"):
            prev_variable = labels[i]
        elif labels[i] == "it":
            if prev_variable:
                labels[i] = prev_variable
    return labels


def get_dependency_graph(labels, dependencies):
    dg = DependencyGraph(pronoun_resolution(labels))
    for dep in dependencies:
        if dep == None:
            continue
        head_pos = int(dep.head_position)
        dependent_pos = int(dep.dependent_position)
        dg.add_edge((head_pos,dependent_pos),dep.type)
    dg.print_tokens()
    transform_dependency_graph(dg)
    combine_by_postion(dg)
    return dg

def combine_by_postion(graph:DependencyGraph):
    for head_tk,tail_tk,start,end in combine_by_position_mapping:
        head_orig_is = [x["orig_index"] for x in graph.get_verticies_by_token(head_tk)]
        for head_og_i in head_orig_is:
            head = graph.get_vertex_by_orig_index(head_og_i)
            if head:
                for i in range(start,end):
                    pos_tl = graph.get_vertex_by_orig_index(head["orig_index"]+i)
                    if pos_tl and pos_tl["token"] == tail_tk:
                        head["token"] = head_tk + " " +  tail_tk
                        graph.remove_vertex_with_child_promote(pos_tl)


if __name__ == "__main__":

    token_lists, deps = get_token_deps()
    only_look_at = -1

    for i in range(6,7):
        if i != only_look_at and only_look_at >= 0:
            continue
        print("**************",i)
        labels = token_lists[i]
        dependencies = deps[i]
        dg: DependencyGraph = get_dependency_graph(labels,dependencies)

        dg.print_clusters()
        if only_look_at >= 0:
            dg.plot_graph()
