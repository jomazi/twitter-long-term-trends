import json
import os
from datetime import datetime, timezone
from typing import List

from dateutil.relativedelta import relativedelta

from .config import NUM_SNAPSHOTS, NUM_TRENDS, START, TRENDS_DIR
from .model import TimeWindow, TrendDescription


def trend_scores(trend_id: int) -> List[float]:
    """
    Trend scores [1.5, 5, 10, ...] of all snapshots for a given trend.

    Parameter:
    - trend_id: id of trend

    Return:
    - list of trend scores
    """

    assert trend_id < NUM_TRENDS and trend_id >= 0

    result = []
    for snapshot_id in range(NUM_SNAPSHOTS):
        try:
            with open(os.path.join(TRENDS_DIR, str(snapshot_id), str(trend_id), "network.json")) as f:
                network = json.load(f)
                result.append(float(network["trend_score"]))
        except FileNotFoundError:
            result.append(0)
    return result


def trend_description(trend_id: int) -> TrendDescription:
    """
    Trend description {"keywords": [corona, covid19, lockdown, ...] ...}.

    Parameter:
    - trend_id: id of trend

    Return:
    - description of trend
    """

    assert trend_id < NUM_TRENDS and trend_id >= 0

    keywords = []
    weights = []
    with open(os.path.join(TRENDS_DIR, "complete", str(trend_id), "network.json")) as f:
        network = json.load(f)
        for n in network["nodes"]:
            keywords.append(n["name"])
            weights.append(n["weight"])
    return {"keywords": keywords, "weights": weights}


def time_window(snapshot_id: int) -> TimeWindow:
    """
    Time window (start, stop) of snapshot.

    Parameter:
    - snapshot_id: id of snapshot

    Return:
    - time window covered by snapshot
    """

    assert snapshot_id < NUM_SNAPSHOTS and snapshot_id >= 0

    start = datetime.fromisoformat(START) + relativedelta(months=snapshot_id)
    start = start.replace(tzinfo=timezone.utc)

    stop = start + relativedelta(months=1)

    return {"start": start, "stop": stop}
