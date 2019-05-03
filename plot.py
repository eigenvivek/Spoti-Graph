import matplotlib.pyplot as plt
import networkx as nx


def plot(G):

    node_attrs = nx.get_node_attributes(G, 'name')
    custom_node_attrs = {}
    for node, attr in node_attrs.items():
        custom_node_attrs[node] = attr

    pos_nodes = nx.spring_layout(G, k=0.15, iterations=20)

    nx.draw_networkx(G, pos_nodes, edge_color='grey', labels=custom_node_attrs)
    plt.show()
