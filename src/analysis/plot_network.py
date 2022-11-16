import json
import os

import igraph as ig

from utils import TRENDS_DIR


def plot_network(snapshot_id: int, trend_id: int):
    """
    Create plot of trend network.

    Parameter:
    - snapshot_id: id of temporal snapshot
    - trend_id: id of trend
    """

    # create network
    with open(os.path.join(TRENDS_DIR, f"{snapshot_id}/{trend_id}/network.json"), "r") as f:
        network = json.load(f)

    g = ig.Graph(directed=False)

    for n in network["nodes"]:
        g.add_vertex(name=n["id"], label=n["name"], weight=n["weight"])

    for e in network["edges"]:
        g.add_edge(source=e["node_id_1"], target=e["node_id_2"], weight=e["weight"])

    print("Graph created: ", g.summary())

    visual_style = {}
    visual_style["vertex_size"] = [1500 * _ for _ in g.vs["weight"]]
    visual_style["vertex_label"] = g.vs["label"]
    visual_style["edge_width"] = g.es["weight"]
    visual_style["layout"] = g.layout_fruchterman_reingold()
    visual_style["margin"] = 100
    visual_style["vertex_color"] = "rgba(0,0,0,1)"
    visual_style["vertex_label_dist"] = 1.5
    visual_style["edge_color"] = "rgba(0,0,0,0.35)"
    visual_style["vertex_label_size"] = 32

    # plot graph
    plot = ig.Plot(
        os.path.join("./figures/network-plot", f"{snapshot_id}-{trend_id}.png"),
        bbox=(1000, 1000),
        background="white")
    plot.add(g, **visual_style)

    # make the plot draw itself on the Cairo surface
    plot.redraw()

    # save the plot
    plot.save()
