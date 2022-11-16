import logging
import os
import pickle
from typing import List, Tuple

import igraph as ig
import matplotlib.pyplot as plt
from tqdm import tqdm

from utils import (EDGE_DIR, NUM_TRENDS, alluvial, num_overlap, time_window,
                   time_windows, trend_description)


def get_network_nodes(time_window: Tuple[int], community_id: int) -> List[str]:
    """
    Get network nodes given a time window and community id.

    Parameter:
    - time_window: time window of network as unix time stamp tuple
    - community_id: id of community

    Return:
    - list of node labels
    """

    _g = ig.Graph.Read_Pickle(os.path.join(EDGE_DIR, f"{time_window[0]}-{time_window[1]}-com-{community_id}.pkl"))

    return [_["name"] for _ in _g.vs]


def plot_alluvial(snapshot_id: int):
    """
    Plot alluvial diagram of given snapshot.
    (flow between networks of snapshot and snapshot + 1)

    Parameter:
    - snapshot_id: id of snapshot
    """

    # temporally matched communities (across snapshots)
    with open(os.path.join(EDGE_DIR, "matched-communities.pkl"), "rb") as fp:
        # matched communities across snapshots
        # list of dicts with values as tuples (t, i) of time step t and community number i
        matched_communities = pickle.load(fp)

    # find overall trend scores per trend
    tw = time_windows()
    trend_scores = []
    for trend_complete in tqdm(matched_communities, desc="trends"):
        trend_score_complete = 0

        # trend snapshots
        # trend_snapshot: tuples (snapshot, community id)
        for trend_snapshot in sorted(trend_complete, key=(lambda _: _[0])):
            graph_file = f"{tw[trend_snapshot[0]][0]}-{tw[trend_snapshot[0]][1]}-com-{trend_snapshot[1]}.pkl"
            g_cur = ig.Graph.Read_Pickle(os.path.join(EDGE_DIR, graph_file))

            # trend score: sum of node occurrences of graph
            trend_score_complete += sum([n["weight"] for n in g_cur.vs])

        trend_scores.append(trend_score_complete)

    # sort trend according to overall popularity
    _, matched_communities = zip(*sorted(zip(trend_scores, matched_communities), reverse=True))

    # trend descriptions
    descriptions = []
    for i in range(NUM_TRENDS):
        res = trend_description(trend_id=i)
        _, descr = zip(*sorted(zip(res["weights"], res["keywords"]), reverse=True))  # sort by descending importance
        descriptions.append(list(descr)[:6])

    # format descriptions
    descriptions_formatted = []
    for d in descriptions:
        txt = ""
        for i, _ in enumerate(d):
            if i % 2 == 0:
                txt += _
            elif i % 2 == 1 and i != 5:
                txt += "  " + _ + "\n"
            else:
                txt += "  " + _
        descriptions_formatted.append(txt)

    # trends
    trends = dict(zip(descriptions_formatted, matched_communities[:NUM_TRENDS]))

    # check if trends are present in given snapshot or snapshot + 1
    com_1 = dict()  # key: trend description; value: community id in snapshot
    com_2 = dict()  # key: trend description; value: community id in snapshot + 1
    for key, value in trends.items():
        c1 = [_ for _ in value if _[0] == snapshot_id]
        c2 = [_ for _ in value if _[0] == snapshot_id + 1]

        if len(c1) > 0:
            com_1[key] = c1[0][1]

        if len(c2) > 0:
            com_2[key] = c2[0][1]

    # alluvial data
    # list of tuples (community snapshot 1, community snapshot 2)
    time_window_1 = time_windows()[snapshot_id]
    time_window_2 = time_windows()[snapshot_id + 1]

    # replace community ids by nodes
    for key, value in com_1.items():
        com_1[key] = get_network_nodes(time_window=time_window_1, community_id=value)

    for key, value in com_2.items():
        com_2[key] = get_network_nodes(time_window=time_window_2, community_id=value)

    # final data
    data = []
    for k1, v1 in com_1.items():
        for k2, v2 in com_2.items():
            for _ in range(num_overlap(v1, v2)):
                data.append([k1, k2 + "-2"])

    # plot
    plt.rcParams["savefig.dpi"] = 600

    ax = alluvial.plot(data, h_gap_frac=0.05, v_gap_frac=0.15, res=15,
                       colors=["tab:purple", "tab:pink", "tab:blue", "tab:olive", "tab:orange", "tab:red", "tab:green",
                               "tab:brown", "tab:gray", "tab:cyan"])
    fig = ax.get_figure()

    # snapshot time span as strings
    dt_1 = time_window(snapshot_id)
    dt_2 = time_window(snapshot_id + 1)
    month_1 = dt_1["start"].strftime("%B")
    month_2 = dt_2["start"].strftime("%B")
    year_1 = dt_1["start"].strftime("%Y")
    year_2 = dt_2["start"].strftime("%Y")

    assert year_1 == year_2, "Years are not the same -> fix title!"

    logging.info(f"Evolution of Communities: {month_1} - {month_2} {year_1}")

    # ax.set_title(f"Evolution of Communities: {month_1} - {month_2} {year_1}", fontsize=28, weight="bold", pad=10)
    fig.set_size_inches(12, 10)
    plt.tight_layout()
    plt.savefig(f"./figures/alluvial/{snapshot_id}.png")
