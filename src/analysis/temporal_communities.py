import logging
import math
import os
import pickle

import igraph as ig
from tqdm import tqdm

from utils import (COMMUNITY_CORE_SIZE, EDGE_DIR, degree_distro,
                   detect_communities, extract_representatives,
                   get_node_occurrences, matching, tweets_in_time_window)


def temporal_communities():
    """
    Detection of temporal communities (per snapshot).
    """

    # clean up old data (communities and degree distributions)
    os.system(f"cd {EDGE_DIR} && rm -rf *-com* && rm -rf *.png")

    # for every network snapshot detect communities
    snapshot_files = [f for f in os.listdir(EDGE_DIR) if os.path.isfile(
        os.path.join(EDGE_DIR, f)) and f.endswith(".pkl")]
    snapshot_files = sorted(snapshot_files, key=(lambda f: int(f.split("-")[0])), reverse=False)

    for f in tqdm(snapshot_files, desc="snapshots"):
        # get network
        f_path = os.path.join(EDGE_DIR, f)
        g = ig.Graph.Read_Pickle(f_path)

        # extract time windows used to aggregate network into snapshot
        ts1 = int(f.split("-")[0])
        ts2 = int(f.split("-")[1].split(".")[0])

        # remove "unimportant" nodes (degree below median)
        median = degree_distro(degrees=g.degree(), file=os.path.join(
            "figures/degree-distro", f.split(".pkl")[0] + ".png"))
        g.delete_vertices(g.vs.select(_degree_lt=median))

        # weights of nodes = node occurrence during time window
        node_occurrences = get_node_occurrences(ts1, ts2, [v["name"] for v in g.vs])
        g.vs["weight"] = node_occurrences

        # simplify network
        g.es["weight"] = [1 for _ in range(g.ecount())]
        g.simplify(multiple=True, loops=True, combine_edges=dict(weight="sum", timestamp="ignore"))

        # number of tweets in time window
        total_tweets = tweets_in_time_window(ts1, ts2)

        # use PMI (point-wise mutual information) as edge weight
        # PMI(node_1; node_2) = log(p(co-occurrence node_1 and node_2)/(p(occurrence node_1) * p(occurrence node_2)))
        # probability -> frequency
        new_weights = []
        for e in g.es():
            p1 = g.vs[e.tuple[0]]["weight"]
            p1 = p1 / total_tweets
            p2 = g.vs[e.tuple[1]]["weight"]
            p2 = p2 / total_tweets
            p12 = e["weight"] / total_tweets
            pmi = math.log(p12 / (p1 * p2))
            new_weights.append(pmi)

        g.es["weight"] = new_weights

        # community detection
        membership = detect_communities(g=g, method="leiden", membership=True)
        g.vs["community"] = membership

        # save network
        g.write_pickle(os.path.join(EDGE_DIR, (f.split(".pkl")[0] + "-com" + ".pkl")))

    # extract temporal communities
    temporal_communities_files = [f for f in os.listdir(EDGE_DIR) if os.path.isfile(
        os.path.join(EDGE_DIR, f)) and f.endswith("-com.pkl")]
    temporal_communities_files = sorted(temporal_communities_files, key=(lambda f: int(f.split("-")[0])), reverse=False)

    temporal_communities_formatted = []  # format needed for temporal matching

    for f in tqdm(temporal_communities_files, desc="snapshots"):  # communities are temporally sorted at this point
        g = ig.Graph.Read_Pickle(os.path.join(EDGE_DIR, f))
        clustering = ig.VertexClustering(g, g.vs["community"])

        communities_snapshot = {}

        # community subgraph
        for i in range(len(clustering)):
            g_sub = clustering.subgraph(i)
            logging.info(f"Community subgraph: {extract_representatives(g_sub)}")
            communities_snapshot[i] = set(extract_representatives(g_sub, num=COMMUNITY_CORE_SIZE))
            g_sub.write_pickle(os.path.join(EDGE_DIR, (f.split(".pkl")[0] + f"-{i}" + ".pkl")))

        temporal_communities_formatted.append(communities_snapshot)

    # temporal matching
    matched_communities = matching(temporal_communities_formatted, memory=4)

    with open(os.path.join(EDGE_DIR, "matched-communities.pkl"), "wb") as fp:
        pickle.dump(matched_communities, fp)
