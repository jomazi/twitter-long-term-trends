import argparse
import logging

from analysis import plot_network, prepare_data, temporal_communities, trends

if __name__ == "__main__":
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", help="prepare data", action="store_true")
    parser.add_argument("--communities", help="detect temporal communities", action="store_true")
    parser.add_argument("--trends", help="extract trends", action="store_true")
    parser.add_argument("--plot_network", help="plot network of given snapshot and trend id", nargs="+", type=int)

    args = parser.parse_args()

    # logging
    logging.basicConfig(filename="main.log", level=logging.INFO, filemode="w", format="%(message)s")

    if args.prepare:
        print("Prepare data ...\n")
        prepare_data()

    if args.communities:
        print("Detect temporal communities ...\n")
        temporal_communities()

    if args.trends:
        print("Extract trends ...\n")
        trends()

    if args.plot_network:
        snapshot_id, trend_id = tuple(args.plot_network)
        plot_network(snapshot_id, trend_id)

    if not args.prepare and not args.communities and not args.trends and not args.plot_network:
        print("Please select task!")
