import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import graphviz_layout

def ibd_coeff(G,n1,n2):
    ancestor = nx.algorithms.lowest_common_ancestor(G, n1, n2)
    if not ancestor:
        return 0
    pl = nx.algorithms.shortest_path_length(g, source = ancestor, target = n1)
    return 0.5**pl

if __name__ == "__main__":
    fam = [[0,10],[1,10],[0,11],[1,11],[0,12],[1,12],
           [13,20],[13,21],[10,20],[10,21] , [12, 22], [11, 23],  [14,22], [15, 23]
           ]
    g = nx.DiGraph(fam)
    #nx.draw(g)

    pos = nx.circular_layout(g)
    #nx.draw_networkx_nodes(g, pos)
    pos = graphviz_layout(g, prog="dot")
    nx.draw_networkx_labels(g, pos)
    nx.draw(g,pos)
    plt.show()
    print("fine")
