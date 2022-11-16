import json
import logging
import os
import pickle
from datetime import datetime, timezone

import igraph as ig
from tqdm import tqdm

from utils import (EDGE_DIR, NUM_TRENDS, TRENDS_DIR, extract_representatives,
                   graph_union, igraph2trend, time_windows)


def trends():
    """
    Detect trends and store in JSON format.
    """

    # cleanup of trends directory
    os.system("rm -rf ./data/trends && mkdir ./data/trends && bash ./scripts/init-trends-dir.sh")

    # temporally matched communities (across snapshots)
    with open(os.path.join(EDGE_DIR, "matched-communities.pkl"), "rb") as fp:
        matched_communities = pickle.load(fp)

    # time windows
    tw = time_windows()
    tw_formatted = [
        f"{datetime.fromtimestamp(t[0], tz=timezone.utc).date()} - {datetime.fromtimestamp(t[1], tz=timezone.utc).date()}"
        for t in tw]

    # find overall trend scores per trend
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

    if len(matched_communities) < NUM_TRENDS:
        raise Exception("Not enough trends found!")
    else:
        matched_communities = list(matched_communities)[:NUM_TRENDS]

    # trend_complete: list of tuples like trend_snapshot (see below)
    for trend_id, trend_complete in tqdm(enumerate(matched_communities), desc="trends"):
        g_com = ig.Graph()
        # community snapshots
        # trend_snapshot: tuples (snapshot, community id)
        for trend_snapshot in sorted(trend_complete, key=(lambda _: _[0])):
            graph_file = f"{tw[trend_snapshot[0]][0]}-{tw[trend_snapshot[0]][1]}-com-{trend_snapshot[1]}.pkl"
            g_cur = ig.Graph.Read_Pickle(os.path.join(EDGE_DIR, graph_file))

            # trend score: sum of node occurrences of graph
            trend_score = sum([n["weight"] for n in g_cur.vs])

            # log evolution
            rep = extract_representatives(g_cur)
            logging.info(f"Time window: {tw_formatted[trend_snapshot[0]]} | Trend score: {trend_score} -> {rep}")

            # save network as JSON file
            # centrality score is taken as new node weight
            network = igraph2trend(g=g_cur, trend_score=trend_score)
            with open(os.path.join(TRENDS_DIR, f"{trend_snapshot[0]}/{trend_id}/network.json"), "w") as f:
                json.dump(network.dict(), f, sort_keys=True, indent=4)

            if g_com.vcount() == 0:  # initial state when graph is empty
                g_com = g_cur.copy()
            else:
                g_com = graph_union(g_com, g_cur)

        trend_score = sum([n["weight"] for n in g_com.vs])
        network = igraph2trend(g=g_com, trend_score=trend_score)
        with open(os.path.join(TRENDS_DIR, f"complete/{trend_id}/network.json"), "w") as f:
            json.dump(network.dict(), f, sort_keys=True, indent=4)

        rep = extract_representatives(g_com)
        logging.info(f"Aggregated | Trend score: {trend_score} -> {rep}\n")
