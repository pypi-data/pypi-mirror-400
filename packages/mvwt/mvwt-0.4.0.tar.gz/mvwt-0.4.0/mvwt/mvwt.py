#!/usr/bin/env python3
"""Main module."""

import csv
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

DATA_TYPES = {
    "weight": {
        "units": "kg",
        "label": "Bodyweight",
    },
    "diet": {
        "units": "none",
        "label": "Diet",
    },
    "calories": {
        "units": "calories",
        "label": "Calories",
    },
}


def new_entry(key, entry, days_offset=0):
    """Make new timestamped database entry.

    Args:
        key (str): Key for the kind of entry (e.g. weight or diet)
        entry (Any):  Value to be entered in database.
    """

    to_write = []

    outfile = Path.home() / f".mvwt/{key}_log.csv"
    if not outfile.is_file():
        outfile.parent.mkdir(parents=True, exist_ok=True)
        to_write.append(["Date", "Time", "Measurement", "Value", "Unit"])

    date = (datetime.today() - timedelta(days=days_offset)).strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    label = DATA_TYPES[key]["label"]
    units = DATA_TYPES[key]["units"]

    to_write.append([date, time, label, entry, units])

    with open(outfile, "a+") as file_pointer:
        writer = csv.writer(
            file_pointer, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerows(to_write)

    print_recent(key)
    return True


def print_recent(key):
    logfile = Path.home() / f".mvwt/{key}_log.csv"
    if key == "calories":
        df = pd.read_csv(logfile, parse_dates=["Date"])
        df = df[pd.Timestamp.now() - df.Date < pd.Timedelta(1, "D")]
        print("\nToday's entries:")
        print(df)
        print("\n\nToday's total:")
        print(df.groupby("Date").sum())
