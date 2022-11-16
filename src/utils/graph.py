import logging

import igraph as ig
import matplotlib.pyplot as plt
import powerlaw as pl

from .model import Edge, EdgeType, Network, Node, NodeType


def detect_communities(g: ig.Graph, method: str, membership: bool = True, initial_membership: list[int] = []):
    """
    Community detection.

    Parameter:
    - g: igraph graph instance
    - method: community algorithm (leiden or infomap)
    - membership: return membership vector?
    - initial_membership: provide initial membership vector

    Return:
    - either membership vector or igraph network clustering
    """

    assert method in ["infomap", "leiden"]

    # 10 runs with best modularity
    best_modularity = 0
    best_clustering: ig.VertexClustering

    for _ in range(10):
        # apply community detection
        if method == "infomap":
            if initial_membership:
                raise Exception("Initial membership not allowed with Infomap.")
            communities = g.community_infomap(edge_weights="weight", trials=10)
        elif method == "leiden":
            assert not g.is_directed(), "graph has to be undirected"
            communities = g.community_leiden(
                objective_function="modularity", weights="weight", resolution_parameter=1, n_iterations=1000,
                node_weights=None, initial_membership=(initial_membership if initial_membership else None))

        mod = g.modularity(membership=communities)
        logging.info(f"Best modularity: {best_modularity} - Current modularity: {mod}")

        if mod > best_modularity:
            best_modularity = mod
            best_clustering = communities

    if membership:
        return best_clustering.membership
    else:
        return best_clustering


def degree_distro(degrees: list[int], file: str) -> float:
    """
    Fitting and plotting of degree distribution:

    Parameter:
    - degrees: list of node degrees
    - file: file to store plot

    Return:
    - median of distribution
    """

    plt.rcParams["figure.figsize"] = [10, 5]
    plt.rcParams["savefig.dpi"] = 600
    plt.rcParams["font.size"] = 12

    fig, ax = plt.subplots()

    # plot degree density distribution
    pl.plot_pdf(degrees, linestyle="solid", color="black", ax=ax)

    # power law fit
    fit = pl.Fit(degrees, xmin=1, discrete=True)
    fit.power_law.plot_pdf(ax=ax, linestyle="dashed", color="black", label=rf"$p(k)=k^{{{-1 * round(fit.alpha, 2)}}}$")

    # check if exponential is better fit
    # see https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0085777&type=printable; accessed 06-09-22
    """
    R is the log likelihood ratio between the two candidate distributions. This number will be positive if the data is more likely in the first distribution, and negative if the data is more likely in the second distribution. The significance value for that direction is p.
    """
    R, p = fit.distribution_compare("power_law", "exponential", normalized_ratio=True)
    print(f"R: {R}, p: {p}")

    assert R > 0, "Power-law is not a good fit!"

    # median of power-law: https://en.wikipedia.org/wiki/Power_law#cite_note-Newman-2:~:text=The%20median%20does,holds.%5B2%5D (accessed 28-06-22)
    if fit.alpha > 1:
        median = 2**(1 / (fit.alpha - 1)) * fit.xmin
    else:
        raise Exception("Median of power law cannot be determined.")

    plt.axvline(x=median, ymin=0.05, ymax=0.95, color="black",
                linestyle="dotted", label=rf"$k_{{1/2}} = {round(median, 2)}$")

    ax.set_xscale("log", base=10)
    ax.set_yscale("log", base=10)
    ax.set_xlabel(r"$k$")
    ax.set_ylabel(r"$p(k)$")
    # ax.set_title("Distribution of Degrees", fontsize=14, weight="bold")
    ax.set_xlim(1)
    ax.legend()

    plt.tight_layout()
    plt.savefig(file)
    plt.close(fig)

    return median


def extract_representatives(g: ig.Graph, num: int = 10) -> list[str]:
    """
    Extract most central nodes.

    Parameter:
    - g: igraph graph instance
    - num: number of nodes to extract

    Return:
    - list of node labels (ordered by centrality)
    """

    centralities = g.pagerank()
    g.vs["centrality"] = centralities
    min_centrality = sorted(centralities, reverse=True)[:num][-1]
    central_nodes = g.vs.select(lambda v: v["centrality"] >= min_centrality)[:num]
    central_nodes = [n["name"] for n in central_nodes]
    central_nodes_sorted = sorted(central_nodes, reverse=True, key=lambda _: g.vs.select(name_eq=_)[0]["centrality"])

    return central_nodes_sorted


def graph_union(g1: ig.Graph, g2: ig.Graph) -> ig.Graph:
    """
    Union of two networks.

    Parameter:
    - g1: first network
    - g2: second network

    Return:
    - union of both networks
    """

    edges = []
    node_weights = {}

    # node weights
    for g in [g1, g2]:
        for v in g.vs:
            if v["name"] in node_weights:
                node_weights[v["name"]] = node_weights[v["name"]] + v["weight"]
            else:
                node_weights[v["name"]] = v["weight"]

    # temporal edges
    for g in [g1, g2]:
        for e in g.es:
            n1 = g.vs[e.tuple[0]]["name"]
            n2 = g.vs[e.tuple[1]]["name"]
            weight = e["weight"]
            edges.append([n1, n2, weight])

    g_res = ig.Graph.TupleList(edges, directed=False, vertex_name_attr="name", edge_attrs=["weight"])
    g_res.simplify(multiple=True, loops=True, combine_edges=dict(weight="sum"))

    # add node weights
    g_res.vs["weight"] = [node_weights[v["name"]] for v in g_res.vs]

    return g_res


def igraph2trend(g: ig.Graph, trend_score: float) -> Network:
    """
    Extract trend network from igraph network instance.

    Parameter:
    - g: igraph network instance
    - trend_score: trend score associated with trend network

    Return:
    - trend network
    """

    assert g.is_simple(), "Graph has to be simple."

    # normalize centrality
    centralities = g.pagerank()
    total_centrality = sum(centralities)
    normalized_centralities = [c / total_centrality for c in centralities]
    g.vs["centrality"] = normalized_centralities

    # subgraph of most central nodes
    min_centrality = sorted(centralities, reverse=True)[:10][-1]
    central_nodes = g.vs.select(lambda v: v["centrality"] >= min_centrality)[:10]
    g_central = g.induced_subgraph(central_nodes)

    # extract nodes
    nodes = []
    for v in g_central.vs():
        n = Node(id=v.index, name=v["name"], weight=v["centrality"], typ=NodeType.hashtag)
        nodes.append(n)

    # extract edges
    edges = []
    for e in g_central.es():
        edges.append(Edge(node_id_1=e.tuple[0], node_id_2=e.tuple[1], weight=e["weight"], typ=EdgeType.co_occurrence))

    return Network(nodes=nodes, edges=edges, trend_score=trend_score)
