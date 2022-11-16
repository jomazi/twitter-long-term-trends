import os
from datetime import datetime, timezone

import igraph as ig
import pandas as pd
from dateutil.relativedelta import relativedelta

from .config import DATA_DIR, NODE_DIR, NUM_SNAPSHOTS, START


def time_windows() -> list[tuple[int]]:
    """
    Time windows of network snapshots.

    Return:
    - list of unix time stamp tuples
    """

    start = datetime.fromisoformat(START)
    start = start.replace(tzinfo=timezone.utc)
    _start = start

    result = []

    for _ in range(0, NUM_SNAPSHOTS):
        _start_int = int(_start.timestamp())
        _start = _start + relativedelta(months=1)
        _stop_int = int(_start.timestamp())

        result.append((_start_int, _stop_int))

    return result


def temporal_network(file: str) -> ig.Graph:
    """
    Converting edge list into undirected co-occurrence network.

    Parameter:
    - file: file of stored edge list

    Return:
    - igraph network/graph instance
    """

    df = pd.read_csv(file)
    g = ig.Graph.TupleList(df.itertuples(index=False), directed=True,
                           vertex_name_attr="name", edge_attrs=["timestamp"])

    # convert to undirected network
    # "mutual" means that pair of directed edges is combined to undirected one
    g.to_undirected(mode="mutual", combine_edges=dict(timestamp="first"))

    return g


def tweets_in_time_window(start: int, stop: int) -> int:
    """
    Number of tweets for a given time window (snapshot).

    Parameter:
    - start: unix start time of snapshot
    - stop: unix stop time of snapshot

    Return:
    - number of tweets
    """

    df = pd.read_csv(os.path.join(DATA_DIR, "tweets.csv"))
    count = df.query(f"start == {start} and stop == {stop}").values[0][-1]

    return count


def get_node_occurrences(start: int, stop: int, nodes: list[str]) -> list[int]:
    """
    Cumulative node occurrence count for given time window.

    Parameter:
    - start: unix start time of snapshot
    - stop: unix stop time of snapshot
    - nodes: list of nodes (labels)

    Return:
    - list of occurrence counts
    """

    f = os.path.join(NODE_DIR, f"{start}-{stop}.csv")
    df = pd.read_csv(f, index_col=0)

    result = [df.loc[n]["count"] for n in nodes]

    return result
