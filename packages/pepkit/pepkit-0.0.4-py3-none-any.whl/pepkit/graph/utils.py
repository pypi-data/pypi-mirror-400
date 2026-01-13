import networkx as nx


def print_graph_attributes(G: nx.Graph) -> None:
    """Print all node and edge attributes from a NetworkX graph.

    Parameters:
        G (nx.Graph): A NetworkX graph (Graph, DiGraph, MultiGraph, etc.).
    """
    print("🔹 Nodes and their attributes:")
    for node, attr in G.nodes(data=True):
        print(f"  Node {node}: {attr}")

    print("\n🔸 Edges and their attributes:")
    if G.is_multigraph():
        for u, v, key, attr in G.edges(data=True, keys=True):
            print(f"  Edge {u}-{v} (key={key}): {attr}")
    else:
        for u, v, attr in G.edges(data=True):
            print(f"  Edge {u}-{v}: {attr}")
