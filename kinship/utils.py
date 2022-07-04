import networkx as nx
import igraph as ig


class FloatBinHandler:

    def __init__(self, precision: int, max_value):
        """
        Handler functions to quickly and easily convert floats to bins with padding, useful when encoding genotypes
        since all the binary representation must be of the same length
        :param precision: number of decimals to be considered
        :param max_value: maximum value of the float numbers to be converted, needed for padding
        """
        self.precision = precision
        # conversion constant needed to transform floeat into int
        self.const = 10**precision
        # length of the padded bin string
        self.length = len(bin(int(max_value * self.const))) - 2

    def float2bin(self, f: float):
        """
        Coverts float to binary sting
        :param f: float to be converted
        :return: binary sting with buffer
        """
        b = bin(int(f * self.const))
        pb = "0b" + b[2:].zfill(self.length)
        return pb

    def bin2float(self, b: str):
        """
        Converts binary string to float
        :param b: Binary string
        :return: float conversion
        """
        return int(b, 2) / self.const


class IBDFamilyTree:
    """
    DAG to deal with genealogy of agents in the model
    """

    def __init__(self, G: nx.DiGraph, model):
        """
        :param G: _description_
        :type G: nx.DiGraph
        :param model: associated model
        :type model: IBDFamilyModel
        """

        self.G = G
        self.ig = ig.Graph.from_networkx(G)
        self.model = model

    def ibd_coeff(self, n1, n2):
        """
        computing relatedness between two agents based on lowest common ancestor in the DAG
        using only networkx

        :param n1: first agent
        :type n1: IBDFamilyAgent
        :param n2: second agent
        :type n2: IBDFamilyAgent
        :return: relatedness score
        :rtype: float
        """
        ancestor = nx.algorithms.lowest_common_ancestor(self.G, n1, n2)

        if not ancestor:
            return 0

        pl = nx.algorithms.shortest_path_length(
            self.G, source=ancestor, target=n1)

        return 0.5 ** pl

    def ig_ibd_coeff(self, n1, n2):
        """
        computing relatedness between two agents based on lowest common ancestor in the DAG
        using igraph

        :param n1: first agent
        :type n1: IBDFamilyAgent
        :param n2: second agent
        :type n2: IBDFamilyAgent
        :return: relatedness score
        :rtype: float
        """
        ancestor = self.ig_LCA(n1, n2)
        if type(ancestor) != int:
            return 0
        v1 = self.ig.vs(lambda x: x["_nx_name"] == n1)[0]
        p = self.ig.get_shortest_paths(ancestor, to=v1, output="vpath")[0]
        pl = len(p) - 1
        return 0.5 ** pl

    def ig_LCA(self, n1, n2):
        """
        Computing lowest common ancestor

        :param n1: first agent
        :type n1: IBDFamilyAgent
        :param n2: second agent
        :type n2: IBDFamilyAgent
        :return: _description_ id of LCA in the graph
        :rtype: _type_ int
        """
        v1, v2 = self.ig.vs(lambda x: x["_nx_name"] == n1)[0], self.ig.vs(lambda x: x["_nx_name"] == n2)[0]
        lca = self.rLCA(v1, v2)
        if lca:
            return lca[0]
        else:
            return None

    def rLCA(self, v1, v2):
        """
        Recursive function to find LCA, should not be called directly, use ig_LCA instead
        :param v1: id of first vertex
        :param v2: id of second vertex
        :return:
        """
        p1, p2 = self.ig.predecessors(v1), self.ig.predecessors(v2)
        i = [value for value in p1 if value in p2]
        if len(i) > 0:
            return i
        else:
            for a1 in p1:
                for a2 in p2:
                    return self.rLCA(a1, a2)

    def remove_generation(self, gen_id):
        """
        Removing an entire  generation from the DAG

        :param gen_id:  ID of the generation to remove
        :type gen_id: int
        """
        gen = [n for n in self.G.nodes if n.split("#")[0] == str(gen_id)]
        self.G.remove_nodes_from(gen)

    def add_child(self, child, cid):
        """
        Adding agent to the DAG

        :param child: agents to be added
        :type child: IBDFamilyAgent
        :param cid: child ID for the graph
        :type cid: str
        """
        pid = [f"{self.model.schedule.steps - 1}#{p}" for p in child["parents id"]]
        self.G.add_edges_from([[p, f"{self.model.schedule.steps}#{cid}"] for p in pid])

    def update_ig(self):
        """
        update igraph DAG from networkx DAG
        """
        self.ig = ig.Graph.from_networkx(self.G)