from data_prep_tools.graph_funs import DependencyGraph

# probs can delete this class since not used
class VertexFilter():
    def __init__(self,graph:DependencyGraph, vertex_list_callable):
        self.orig_index_list = [v["orig_index"] for v in vertex_list_callable()]
        self.graph= graph

    def get_next(self):
        next_index = self.orig_index_list.pop()
        return self.graph.get_vertex_by_orig_index(next_index)

    def is_empty(self):
        return len(self.orig_index_list) == 0