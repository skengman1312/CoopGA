import networkx as nx
import matplotlib.pyplot as plt
import igraph as ig
from networkx.drawing.nx_pydot import graphviz_layout


class IBDFamilyTree:

    def __init__(self, G: nx.DiGraph, model):
        """

        :param G:
        :param model: the associated model
        """
        self.G = G
        self.ig = ig.Graph.from_networkx(G)
        self.model = model

    def ibd_coeff(self, n1, n2):
        ancestor = nx.algorithms.lowest_common_ancestor(self.G, n1, n2)
        if not ancestor:
            return 0
        pl = nx.algorithms.shortest_path_length(
            self.G, source=ancestor, target=n1)
        return 0.5 ** pl

    def ig_ibd_coeff(self, n1, n2):
        ancestor = self.ig_LCA(n1, n2)
        if type(ancestor) != int:
            return 0
        v1 = self.ig.vs(lambda x: x["_nx_name"] == n1)[0]
        p = self.ig.get_shortest_paths(ancestor, to=v1, output="vpath")[0]
        pl = len(p)-1
        return 0.5 ** pl

    def ig_LCA(self, n1, n2):
        v1, v2 = self.ig.vs(lambda x: x["_nx_name"] == n1)[0], self.ig.vs(lambda x: x["_nx_name"] == n2)[0]
        lca = self.rLCA(v1, v2)
        if lca:
            return lca[0]
        else:
            return None

    def rLCA(self, v1, v2):
        p1, p2 = self.ig.predecessors(v1), self.ig.predecessors(v2)
        i = [value for value in p1 if value in p2]
        if len(i) > 0:
            return i
        else:
            for a1 in p1:
                for a2 in p2:
                    return self.rLCA(a1, a2)

    def remove_generation(self, gen_id):
        gen = [n for n in self.G.nodes if n.split("#")[0] == str(gen_id)]
        self.G.remove_nodes_from(gen)

    def add_child(self, child, cid):
        pid = [f"{self.model.schedule.steps - 1}#{p}" for p in child["parents id"]]
        self.G.add_edges_from([[p, f"{self.model.schedule.steps}#{cid}"] for p in pid])

    def update_ig(self):
        print("update")
        self.ig = ig.Graph.from_networkx(self.G)



if __name__ == "__main__":
    fam = [[0, 10], [1, 10], [0, 11], [1, 11], [0, 12], [1, 12],
           [13, 20], [13, 21], [10, 20], [10, 21], [
               12, 22], [11, 23], [14, 22], [15, 23]
           ]
    fam = [["0#0", "1#0"], ["0#0", "1#1"], ["0#0", "1#2"], ["0#1", "1#0"], ["0#1", "1#1"], ["0#1", "1#2"],
           ["1#0", "2#0"], ["1#0", "2#1"], [
               "1#0", "2#2"], ["1#1", "2#3"], ["1#1", "2#4"]
           ]
    tree = IBDFamilyTree(nx.DiGraph(fam), model=None)
    # itree = ig.Graph.from_networkx(tree)
    # nx.draw(g)
    # nx.draw_networkx_nodes(g, pos)

    pos = graphviz_layout(tree.G, prog="dot")
    nx.draw_networkx_labels(tree.G, pos)
    nx.draw(tree.G, pos)
    plt.show()
    # tree.remove_generation(0)
    # pos = graphviz_layout(tree.G, prog="dot")
    # nx.draw_networkx_labels(tree.G, pos)
    # nx.draw(tree.G,pos)
    # plt.show()
    print("fine")
