import argparse
import logging

from analysis import prepare_data, temporal_communities

if __name__ == "__main__":
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", help="prepare data", action="store_true")
    parser.add_argument("--communities", help="detect temporal communities", action="store_true")

    args = parser.parse_args()

    # logging
    logging.basicConfig(filename="main.log", level=logging.INFO, filemode="w", format="%(message)s")

    if args.prepare:
        print("Prepare data ...\n")
        prepare_data()

    if args.communities:
        print("Detect temporal communities ...\n")
        temporal_communities()

    if not args.prepare and not args.communities:
        print("Please select task!")
