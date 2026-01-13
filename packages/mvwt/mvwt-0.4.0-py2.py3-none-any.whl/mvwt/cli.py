#!/usr/bin/env python3
"""Console script for mvwt."""
import argparse
import sys

from mvwt.mvwt import new_entry, print_recent
from mvwt.plotting import plot


def main():
    """Console script for mvwt."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--weight", type=float, help="Weight entry")
    parser.add_argument(
        "-d", "--diet", type=int, help="Diet entry (1 (good) / 2 (ok) /3 (bad))"
    )
    parser.add_argument(
        "-c", "--calories", type=int, help="Calories entry as an integer"
    )
    parser.add_argument(
        "-p", "--plot", action="store_true", help="Generate summary plot"
    )
    parser.add_argument(
        "-y", "--yesterday", action="store_true", help="Data entry for yesterday"
    )
    parser.add_argument(
        "-t", "--today", action="store_true", help="Print summary for today"
    )
    args = parser.parse_args()

    days_offset = 1 if args.yesterday else 0

    if args.weight is not None:
        new_entry("weight", args.weight, days_offset=days_offset)
    if args.diet is not None:
        new_entry("diet", args.diet, days_offset=days_offset)
    if args.calories is not None:
        new_entry("calories", args.calories, days_offset=days_offset)
    if args.plot:
        plot()
    if args.today:
        print_recent("calories")

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
