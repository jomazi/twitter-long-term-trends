import logging

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from utils import (NUM_SNAPSHOTS, NUM_TRENDS, time_window, trend_description,
                   trend_scores)


def plot_timeline():
    """
    Plot timeline of detected trends.
    credits: https://stackoverflow.com/a/51122276 (accessed 08-09-22)
    """

    plt.rcParams["figure.figsize"] = [15.5, 9]
    plt.rcParams["savefig.dpi"] = 600
    plt.rcParams["font.size"] = 14

    # get trend data
    data = []
    descriptions = []
    for i in reversed(range(NUM_TRENDS)):
        # scores
        scores = trend_scores(trend_id=i)
        data.append(scores)

        # descriptions
        res = trend_description(trend_id=i)
        _, descr = zip(*sorted(zip(res["weights"], res["keywords"]), reverse=True))  # sort by descending importance
        descriptions.append(list(descr)[:6])

    # normalize by maximum
    data = np.array(data)
    row_sums = data.max(axis=1)
    data = data / row_sums[:, np.newaxis]
    data[data == 0] = np.nan

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

    logging.info(f"Descriptions:\n{descriptions_formatted}")

    # time windows
    time = []
    for i in range(NUM_SNAPSHOTS):
        window = time_window(snapshot_id=i)
        time.append(window["start"])

    fig = plt.figure()
    # plt.title("Temporal Heatmap of Trend Scores", fontsize=32, weight="bold", pad=20)
    c = plt.pcolor(data, edgecolors="k", linestyle="solid", linewidths=0.2,
                   cmap=LinearSegmentedColormap.from_list('wg', ["w", "g"], N=256), vmin=0.0, vmax=1.0)

    def show_values(pc, fmt="%.1f", **kw):
        pc.update_scalarmappable()
        ax = pc.axes

        for p, color, value in zip(pc.get_paths(), pc.get_facecolors(), pc.get_array()):
            x, y = p.vertices[:-2, :].mean(0)

            # decide whether black or white color
            if np.all(color[:3] > 0.5):
                color = (0.0, 0.0, 0.0)
            else:
                color = (1.0, 1.0, 1.0)

            # text of value
            ax.text(x, y, fmt % value, ha="center", va="center", color=color, **kw)

    show_values(c)

    # overwrite labels
    new_labels = [""] * NUM_SNAPSHOTS
    for i in range(NUM_SNAPSHOTS):
        if i % 2 == 1:
            new_labels[i] = time[i].strftime("%B") + "\n" + time[i].strftime("%Y")

    plt.xticks(ticks=range(NUM_SNAPSHOTS),
               labels=new_labels)
    plt.yticks(ticks=[_ + 0.5 for _ in range(NUM_TRENDS)], labels=descriptions_formatted)

    # add colorbar label
    cbar = plt.colorbar(c)
    cbar.ax.get_yaxis().labelpad = 15
    cbar.ax.set_ylabel("trend score", rotation=270)

    plt.tight_layout()
    plt.savefig("./figures/timeline.png")
    plt.close(fig)
