import os

from utils import EDGE_DIR, temporal_network, time_windows


def prepare_data():
    """
    For each snapshot create network.
    """
    for t in time_windows():
        f = os.path.join(EDGE_DIR, f"{t[0]}-{t[1]}")
        tn = temporal_network(file=(f + ".csv"))
        tn.write_pickle((f + ".pkl"))
