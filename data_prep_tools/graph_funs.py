igraph = __import__("igraph")

from igraph import *


class DependencyGraph():
    def __init__(self,labels):
        self.graph = igraph.Graph(directed=True)
        self.graph.add_vertices(len(labels))
        self.graph.vs["token"] = labels
        self.graph.vs["orig_index"] = [i for i in range(len(labels))]
        self.graph.es["type"] = []

    def print_tokens(self):
        print(" ".join(self.graph.vs["token"]))

    def add_edge(self, edge, label):
        """ edge = (head_pos,end_pos)
            label = dependency type
        """
        self.graph.add_edge(edge[0],edge[1])
        eid = self.graph.get_eid(edge[0], edge[1])
        self.graph.es[eid]["type"] = label

    def get_edges(self):
        return self.graph.get_edgelist()

    def remove_edge(self,edge):
        eid = self.graph.get_eid(edge[0],edge[1])
        self.graph.delete_edges(eid)

    def remove_vertex(self,vid):
        self.graph.delete_vertices(vid)

    def get_parents(self,vertex):
        edges = self.graph.es.select(_target=vertex)
        return [x.source for x in edges]

    def output(self):
        igraph.summary(self.graph)

    def get_verticies(self, edge):
        return self.graph.vs[edge[0]], self.graph.vs[edge[1]]

    def get_edges_with_dependent_token(self, token):
        edges = []
        vertices = self.graph.vs.select(token=token)
        for vertex in vertices:
            vid = vertex.index
            edges.extend([(x,vid) for x in self.graph.neighbors(vid,mode="in")])
        return edges

    def get_children_indices(self, vid):
        return self.graph.neighbors(vid, mode="out")

    def get_children(self,vertex):
        return vertex.neighbors(mode="out")

    def get_label(self, edge):
        eid = self.graph.get_eid(edge[0],edge[1])
        return self.graph.es[eid]["type"]

    def get_edges_with_type(self, type):
        return [(edge.source,edge.target) for edge in self.graph.es if edge["type"]==type]

    def get_vertex_lable(self, id):
        return self.graph.vs[id]["token"]

    def get_roots(self):
        roots = []
        for vertex in self.graph.vs:
            vid = vertex.index
            if not self.get_parents(vid):
                roots.append(vertex)
        return roots

    def combine(self, edge, keep_first_tok=True):
        self.remove_edge(edge)
        hd,tl = self.get_verticies(edge)
        if keep_first_tok:
            hd["token"] = hd["token"]+" "+tl["token"]
        else:
            hd["token"] = tl["token"]
            hd["orig_index"] = tl["orig_index"]

        for child in self.get_children(tl):
            original_edge = (tl.index,child.index)
            new_edge = (hd.index,child.index)
            self.add_edge(new_edge,self.get_label(original_edge))
        self.remove_vertex(tl.index)

    def get_token(self, vertex_id):
        return self.graph.vs[vertex_id]["token"]

    def get_vertex_tuple(self, vertex):
        return (vertex["token"], vertex["orig_index"])

    def transitive_closure(self, root, seen):
        closure = [root]
        for child in self.get_children(root):
            if child not in closure+seen:
                child_vals = self.transitive_closure(child, closure+seen)
                closure.extend(child_vals)
        return closure

    def print_v_list(self,v_list):
        print([self.get_vertex_tuple(v) for v in v_list])

    def print_clusters(self):
        roots = self.get_roots()
        clusters = []
        for root in roots:
            self.print_v_list(self.transitive_closure(root,[]))


    def get_vertex_color(self,vertex):
        if self.is_root(vertex):
            return "blue"
        return "red"

    def plot_graph(self):
        self.graph.vs["label"] = [self.get_vertex_tuple(v) for v in self.graph.vs]
        layout = self.graph.layout("fr")
        plot(self.graph, layout=layout, vertex_color=[self.get_vertex_color(v) for v in self.graph.vs])

    def is_root(self,vertex):
        return len(self.get_parents(vertex.index)) == 0

    def get_closest_to_root(self, root, vertices:list):
        to_search = [root]
        visited = []
        while to_search:
            head:Vertex = to_search.pop(0)
            if head in vertices:
                return head
            if head in visited:
                continue
            visited.append(head)
            to_search.extend(self.get_children(head))

    def get_distance(self, from_v, to_v):
        return self.graph.shortest_paths_dijkstra(from_v,to_v)

    def get_path(self, from_v, to_v):
    # performing a depth first search
        if from_v == to_v:
            return [from_v]
        for child in self.get_children(from_v):
            path = self.get_path(child,to_v)
            if path:
                path.append(from_v)
                return path
        return []

    def remove_cycles(self,root,visited=[]):
        children = self.get_children(root)
        visited += [root]
        for child in children:
            if child in visited:
                self.remove_edge((root.index,child.index))
            else:
                visited += [child]
                visited = self.remove_cycles(child,visited)
        return visited

    def get_child_with_token(self, root, token):
        childs = [child for child in self.get_children(root) if child["token"] == token]
        if len(childs) == 1:
            return childs[0]
        else:
            print("wrong number of children with token",len(childs))

        pass

    def rotate_edge(self, edge):
        cur_lab = self.get_label(edge)
        self.remove_edge(edge)
        self.add_edge((edge[1],edge[0]),cur_lab)

    def get_vertex_from_id(self, vid):
        return self.graph.vs[vid]

    def get_vertex_by_orig_index(self, orig_index):
        v = self.graph.vs.find(orig_index=orig_index)
        return self.graph.vs.find(orig_index=orig_index)

